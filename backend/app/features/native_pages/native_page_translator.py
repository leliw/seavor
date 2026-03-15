from typing import Any, Dict
from uuid import UUID

from features.languages import LANGUAGE_NAMES, Language
from features.native_pages.native_page_model import (
    NativeDefinitionGuess,
    NativeDefinitionGuessBase,
    NativeGapFillChoiceExercise,
    NativeGapFillChoiceExerciseBase,
    NativeInfoPage,
    NativeInfoPageBase,
    NativePage,
)
from features.pages.definition_guess_model import DefinitionGuess
from features.pages.page_base_model import PageType
from features.pages.page_model import GapFillChoiceExercise, InfoPage
from features.pages.page_service import PageService
from haintech.ai import AITaskExecutor, BaseAIModel

from shared.prompts.prompt_executor import PromptExecutor
from shared.prompts.prompt_service import PromptService


class NativePageTranslator:
    def __init__(self, ai_model: BaseAIModel, prompt_service: PromptService, service: PageService):
        self.ai_model = ai_model
        self.prompt_executor = PromptExecutor(ai_model, prompt_service)
        self.service = service

    async def translate_page_to_native(
        self, language: Language, native_language: Language, page_id: UUID
    ) -> NativePage:
        page = await self.service.get(page_id)
        match page.type:
            case PageType.GAP_FILL_CHOICE:
                native = await self._translate(language, native_language, page)
                return NativeGapFillChoiceExercise.from_page(page, native)
            case PageType.INFO:
                native = await self._translate_info_page(language, native_language, page)
                return NativeInfoPage.from_page(page, native)
            case PageType.DEFINITION_GUESS:
                native = await self._translate_definition_guess(language, native_language, page)
                return NativeDefinitionGuess.from_page(page, native)
            case _:
                raise NotImplementedError(f"Unsupported page type: {page.type}")

    async def _translate_info_page(
        self, src_language: Language, dest_language: Language, page: InfoPage
    ) -> NativeInfoPageBase:
        return self.prompt_executor.execute_typed(
            "translate_info_page",
            NativeInfoPageBase,
            src_language=LANGUAGE_NAMES[src_language],
            dest_language=LANGUAGE_NAMES[dest_language],
            page_title=page.title,
            page_content=page.content,
        )

    async def _translate(
        self, src_language: Language, dest_language: Language, page: GapFillChoiceExercise
    ) -> NativeGapFillChoiceExerciseBase:
        system_instructions = "You are translating topics of a language course. Translate only if it is necessary."

        message = "Translate the page exercise from {src_language} to {dest_language}. "
        message += "Return the response as a single JSON dictionary."
        message += "\nSentence: **{page.sentence}**"
        message += "\nCorrect answer: **{page.answer}**"
        example = "Example response:\n{{'sentence': 'translated sentence', 'answer': 'translated correct answer'"
        if page.explanation:
            message += "\nExplanation: **{page.explanation}**"
            example += ", 'explanation': 'translated explanation'"
        if page.distractors_explanation:
            message += "\nDistractors explanation:"
            example += ", 'distractors_explanation': {{"
            for distractor in page.distractors_explanation.items():
                message += f"\n{distractor[0]}: **{distractor[1]}**"
                example += f"'{distractor[0]}': 'translated explanation', "
            example += "}}"
        if page.hint:
            message += "\nHint: **{page.hint}**"
            example += ", 'hint': 'translated hint'"
        example += "}}"
        message += "\n\n"
        message += example
        message += "\n"

        task = AITaskExecutor(self.ai_model, system_instructions, message, "json")
        ret: Dict[str, Any] = await task.execute_async(
            src_language=LANGUAGE_NAMES[src_language], dest_language=LANGUAGE_NAMES[dest_language], page=page
        )  # type: ignore
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]

        n_ret = {}
        for k, v in ret.items():
            if k == "sentence":
                continue
            n_ret[f"native_{k}"] = v
        return NativeGapFillChoiceExerciseBase.model_validate(n_ret)

    async def _translate_definition_guess(
        self, language: Language, native_language: Language, definition_guess: DefinitionGuess
    ) -> NativeDefinitionGuessBase:
        return self.prompt_executor.execute_typed(
            "translate_definition_guess",
            NativeDefinitionGuessBase,
            language=language,
            language_name=LANGUAGE_NAMES[language],
            native_language=native_language,
            native_language_name=LANGUAGE_NAMES[native_language],
            definition_guess=definition_guess,
        )
