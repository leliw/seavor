from typing import Any, Dict
from uuid import UUID

from features.languages import LANGUAGE_NAMES, Language
from features.native_pages.native_page_model import (
    NativeGapFillChoiceExercise,
    NativeGapFillChoiceExerciseBase,
    NativeInfoPage,
    NativePage,
)
from features.pages.page_model import GapFillChoiceExercise
from features.pages.page_service import PageService
from haintech.ai import AITaskExecutor, BaseAIModel


class NativePageTranslator:
    def __init__(self, ai_model: BaseAIModel, service: PageService):
        self.service = service
        self.ai_model = ai_model

    async def translate_page_to_native(self, target_language: Language, native_language: Language, page_id: UUID) -> NativePage:
        page = await self.service.get(page_id)
        match page.type:
            case "gap-fill-choice":
                native = await self._translate(target_language, native_language, page)
                return NativeGapFillChoiceExercise.from_page(page, native)
            case "info":
                raise NotImplementedError()
                return NativeInfoPage.from_page(page)
            case _:
                raise NotImplementedError(f"Unsupported page type: {page.type}")

    async def _translate(
        self, src_language: Language, dest_language: Language, page: GapFillChoiceExercise
    ) -> NativeGapFillChoiceExerciseBase:
        system_instructions = "You are translating topics of a language course. Translate only if it is necessary."

        message = "Translate the page exercise from {src_language} to {dest_language}. "
        message += "Return the response as a single JSON dictionary."
        message += "\nSentence: **{page.target_sentence}**"
        message += "\nCorrect answer: **{page.target_answer}**"
        example = "Example response:\n{{'sentence': 'translated sentence', 'answer': 'translated correct answer'"
        if page.target_explanation:
            message += "\nExplanation: **{page.target_explanation}**"
            example += ", 'explanation': 'translated explanation'"
        if page.target_distractors_explanation:
            message += "\nDistractors explanation:"
            example += ", 'distractors_explanation': {{"
            for distractor in page.target_distractors_explanation.items():
                message += f"\n{distractor[0]}: **{distractor[1]}**"    
                example += f"'{distractor[0]}': 'translated explanation', "
            example += "}}"
        if page.target_hint:
            message += "\nHint: **{page.target_hint}**"
            example += ", 'hint': 'translated hint'"
        example += "}}"
        message += "\n\n"
        message += example
        message += "\n"


        task = AITaskExecutor(self.ai_model, system_instructions, message, "json")
        ret: Dict[str, Any] = await task.execute_async(
            src_language=LANGUAGE_NAMES[src_language], dest_language=LANGUAGE_NAMES[dest_language], page=page
        ) # type: ignore
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]

        n_ret = {}
        for k,v  in ret.items():
            if k == "sentence":
                continue
            n_ret[f"native_{k}"] = v
        return NativeGapFillChoiceExerciseBase.model_validate(n_ret)
