from typing import List, Optional

from features.languages import LANGUAGE_NAMES, Language
from features.letter_shuffles.letter_shuffle_model import LetterShuffleItem, LetterShuffleSet, LetterShuffleSetCreate
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleSetTranslationCreate,
)
from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_model import GapFillChoiceExerciseCreate, InfoPageCreate
from features.topics.topic_model import TopicCreate, TopicType
from haintech.ai import AITaskExecutor, BaseAIModel
from haintech.ai.open_ai import OpenAIModel
from pydantic import BaseModel
from shared.prompts.prompt_executor import PromptExecutor
from shared.prompts.prompt_service import PromptService


class ExpressionAndDefintion(BaseModel):
    expression: str
    definition: str


class TeacherService:
    def __init__(
        self,
        prompt_service: PromptService,
        ai_model: Optional[BaseAIModel] = None,
        language: Language = Language.EN,
        level: Optional[Level] = None,
    ) -> None:
        self.prompt_service = prompt_service
        self.ai_model = ai_model or OpenAIModel("gpt-4.1-mini", {"temperature": 0})
        self.language = language
        self.level = level
        self.language_name = LANGUAGE_NAMES[language]
        self.system_instructions = f"You are a {language} teacher."
        self.system_instructions += f"\nUse phrases and expressions that are natural to the {self.language_name} language and related to {self.language_name} tradition."
        self.system_instructions += f"\nAlways respond in {self.language_name}."

    def generate_word_set(self, theme: str, max_count: int = 10) -> list[str]:
        ret = PromptExecutor(self.ai_model, self.prompt_service).execute_list(
            "generate_word_set", target_language=self.language_name, theme=theme, max_count=max_count
        )
        return ret

    def filter_word_set(self, theme: str, word_set: list[str]) -> list[str]:
        ret = PromptExecutor(self.ai_model, self.prompt_service).execute_list(
            "filter_word_set", target_language=self.language_name, theme=theme, word_set=word_set
        )
        return ret

    def create_definition_guess(self, theme: str, phrase: str, order: int) -> DefinitionGuessCreate:
        return PromptExecutor(self.ai_model, self.prompt_service).execute_typed(
            "create_definition_guess",
            DefinitionGuessCreate,
            language=self.language,
            language_name=self.language_name,
            theme=theme,
            phrase=phrase,
            order=order,
        )

    def create_letter_shuffle_set(self, theme_en: str, number_of_words: int = 10) -> LetterShuffleSetCreate:
        description_en = f"Words and phrases related to {theme_en}"
        words = self.generate_word_list(theme_en, number_of_words)
        if self.language != Language.EN:
            translation = self.translate_expression_and_definition(self.language, theme_en, description_en)
            theme = translation.expression
            description = translation.definition
        else:
            theme = theme_en
            description = description_en
        ret = LetterShuffleSetCreate(
            target_language_code=self.language, target_title=theme, target_description=description, items=[]
        )
        for word in words:
            definition = self.get_word_definition(theme, word)
            if isinstance(definition, str):
                ret.items.append(LetterShuffleItem(target_phrase=word, target_description=definition))
        return ret

    def create_letter_shuffle_set_translation(
        self, letter_shuffle_set: LetterShuffleSet, native_language_code: Language
    ) -> LetterShuffleSetTranslationCreate:
        translation = self.translate_expression_and_definition(
            native_language_code, letter_shuffle_set.target_title, letter_shuffle_set.target_description
        )
        ret = LetterShuffleSetTranslationCreate(
            id=letter_shuffle_set.id,
            target_language_code=letter_shuffle_set.target_language_code,
            target_title=letter_shuffle_set.target_title,
            target_description=letter_shuffle_set.target_description,
            native_language_code=native_language_code,
            native_title=translation.expression,
            native_description=translation.definition,
            items=[],
            image_name=letter_shuffle_set.image_name,
        )
        for item in letter_shuffle_set.items:
            translation = self.translate_expression_and_definition(
                native_language_code, item.target_phrase, item.target_description
            )
            item_translation = LetterShuffleItemTranslation(
                target_phrase=item.target_phrase,
                target_description=item.target_description,
                target_phrase_audio_file_name=item.target_phrase_audio_file_name,
                target_description_audio_file_name=item.target_description_audio_file_name,
                phrase_image_name=item.phrase_image_name,
                native_phrase=translation.expression,
                native_description=translation.definition,
            )
            ret.items.append(item_translation)
        return ret

    def generate_word_list(self, theme: str, count: int = 30):
        s, u = self.prompt_service.render(
            "generate_word_list", target_language=self.language_name, theme=theme, count=count
        )
        task = AITaskExecutor(self.ai_model, s, u, "json")
        ret = task.execute()
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]
        if isinstance(ret, dict) and len(ret) == 2:
            words = list(ret.values())[0]
            phrases = list(ret.values())[1]
            ret = words + phrases
        return ret

    def get_word_definition(self, theme: str, word: str):
        s, u = self.prompt_service.render(
            "get_word_definition", target_language=self.language_name, theme=theme, word=word
        )
        task = AITaskExecutor(self.ai_model, s, u, "text")
        ret = task.execute()
        return ret

    def translate_expression_and_definition(
        self, native_language: Language, expression: str, definition: str
    ) -> ExpressionAndDefintion:

        return PromptExecutor(self.ai_model, self.prompt_service).execute_typed(
            "translate_expression_and_definition",
            ExpressionAndDefintion,
            language_name=self.language_name,
            level=self.level,
            native_language_name=LANGUAGE_NAMES[native_language],
            expression=expression,
            definition=definition,
        )

    def create_gap_fill_choice_excercises(self, theme: str, count: int = 10) -> List[GapFillChoiceExerciseCreate]:
        return PromptExecutor(self.ai_model, self.prompt_service).execute_typed_list(
            "create_gap_fill_choice",
            GapFillChoiceExerciseCreate,
            target_language=self.language_name,
            theme=theme,
            count=count,
        )

    def create_info_pages(self, theme: str) -> List[InfoPageCreate]:
        return PromptExecutor(self.ai_model, self.prompt_service).execute_typed_list(
            "create_info_page",
            InfoPageCreate,
            target_language=self.language_name,
            level=self.level,
            theme=theme,
        )

    def create_topic_description(self, level: Level, type: TopicType, topic_name: str) -> str:
        ret = PromptExecutor(self.ai_model, self.prompt_service).execute(
            "create_topic_description",
            language=self.language,
            language_name=LANGUAGE_NAMES[self.language],
            level=level,
            topic_type=type,
            topic_name=topic_name,
        )
        assert ret.content
        return ret.content.strip()

    def create_topic_create(self, level: Level, type: TopicType, topic_name: str) -> TopicCreate:
        topic_description = self.create_topic_description(level, type, topic_name)
        return TopicCreate(
            language=self.language,
            level=level,
            title=topic_name,
            description=topic_description,
            type=type,
        )
