from typing import Dict

from features.languages import LANGUAGE_NAMES, Language
from features.letter_shuffles.letter_shuffle_model import LetterShuffleItem, LetterShuffleSet, LetterShuffleSetCreate
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleSetTranslationCreate,
)
from haintech.ai import AITaskExecutor
from haintech.ai.open_ai import OpenAIModel


class TeacherService:

    def __init__(self, target_language_code: Language = Language.EN) -> None:
        target_language = LANGUAGE_NAMES[target_language_code]
        self.ai_model = OpenAIModel("gpt-4.1-mini", {"temperature": 0})
        self.target_language_code = target_language_code
        self.target_language = target_language
        self.system_instructions = f"You are a {target_language} teacher."
        self.system_instructions += f"\nUse phrases and expressions that are natural to the {target_language} language and related to {target_language} tradition."
        self.system_instructions += f"\nAlways respond in {target_language}."

    def create_letter_shuffle_set(self, theme_en: str, number_of_words: int = 10) -> LetterShuffleSetCreate:
        description_en = f"Words and phrases related to {theme_en}"
        words = self.generate_word_list(theme_en, number_of_words)
        if self.target_language_code != Language.EN:
            translation = self.translate_expression_and_definition(self.target_language_code, theme_en, description_en)
            theme = translation["expression"]
            description = translation["definition"]
        else:
            theme = theme_en
            description = description_en
        ret = LetterShuffleSetCreate(
            target_language_code=self.target_language_code, target_title=theme, target_description=description, items=[]
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
            native_title=translation["expression"],
            native_description=translation["definition"],
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
                native_phrase=translation["expression"],
                native_description=translation["definition"],
            )
            ret.items.append(item_translation)
        return ret

    def generate_word_list(self, theme: str, count: int = 30):
        message = f"Prepare a set of {count} words and short (2-3 words) phrases related to {theme}. "
        message += "Return the response as a single JSON list."
        message += "\n\n"
        message += "Example response:"
        message += '\n["word1", "word2", "word3"]'
        message += "\n"

        task = AITaskExecutor(self.ai_model, self.system_instructions, message, "json")
        ret = task.execute()
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]
        if isinstance(ret, dict) and len(ret) == 2:
            words = list(ret.values())[0]
            phrases = list(ret.values())[1]
            ret = words + phrases
        return ret

    def get_word_definition(self, theme: str, word: str):
        message = f"Return the definition of the expression **{word}** used in {theme} context in {self.target_language} without using the expression. Return only definion."

        task = AITaskExecutor(self.ai_model, self.system_instructions, message, "text")
        ret = task.execute()
        return ret

    def translate_expression_and_definition(
        self, language_code: Language, expression: str, definition: str
    ) -> Dict[str, str]:
        language = LANGUAGE_NAMES[language_code]
        message = f"Translate the expression and its definition from {self.target_language} to {language}. "
        message += "Return the response as a single JSON dictionary."
        message += f"\nExpression: **{expression}**"
        message += f"\nDefinition: **{definition}**"
        message += "\n\n"
        message += "Example response:"
        message += "\n{example}"
        message += "\n"

        task = AITaskExecutor(self.ai_model, self.system_instructions, message, "json")
        ret = task.execute(example="{'expression': 'translated expression', 'definition': 'translated definition'}")
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]
        return ret  # type: ignore
