from typing import Annotated, Any, Self, Union, override

from core.translation_status import TranslationStatus
from features.languages import Language
from features.pages.definition_guess_model import DefinitionGuess
from features.pages.page_base_model import PageHeader
from features.pages.page_model import GapFillChoiceExercise, InfoPage
from pydantic import BaseModel, Field, model_validator


class NativePageHeader(PageHeader):
    pass


class NativeGapFillChoiceExerciseBase(BaseModel):
    native_answer: str
    native_explanation: str | None = None
    native_distractors_explanation: dict[str, str] | None = None
    native_hint: str | None = None

    native_sentence_audio_file_name: str | None = None
    native_explanation_audio_file_name: str | None = None
    native_distractors_explanation_audio_file_name: dict[str, str] | None = None
    native_hint_audio_file_name: str | None = None


class NativeGapFillChoiceExercise(GapFillChoiceExercise, NativeGapFillChoiceExerciseBase):
    @classmethod
    def from_page(cls, page: GapFillChoiceExercise, native: NativeGapFillChoiceExerciseBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())

    @override
    def get_audio_file_names(self) -> set[str]:
        ret = super().get_audio_file_names()
        if self.native_sentence_audio_file_name:
            ret.add(self.native_sentence_audio_file_name)
        if self.native_explanation_audio_file_name:
            ret.add(self.native_explanation_audio_file_name)
        if self.native_hint_audio_file_name:
            ret.add(self.native_hint_audio_file_name)
        if self.native_distractors_explanation_audio_file_name:
            for distractor in self.native_distractors_explanation_audio_file_name.values():
                ret.add(distractor)
        return ret


class NativePageBase(BaseModel):
    native_language: Language | None = None
    translation_status: TranslationStatus = "pending"
    error_message: str | None = None

    @model_validator(mode="before")
    @classmethod
    def infer_status_for_legacy_data(cls, data: Any) -> Any:
        if isinstance(data, dict) and "translation_status" not in data:
            data["translation_status"] = "ready"
        return data


class NativeInfoPageBase(NativePageBase):
    native_title: str
    native_content: str  # markdown / HTML / JSON


class NativeInfoPage(InfoPage, NativeInfoPageBase):
    @classmethod
    def from_page(cls, page: InfoPage, native: NativeInfoPageBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())


class NativeSentence(BaseModel):
    text: str


class NativeAnswerOption(BaseModel):
    value: str
    explanation: str | None = None


class NativeDefinitionGuessBase(NativePageBase):
    native_phrase: str
    native_definition: str  # markdown / HTML / JSON

    native_sentences: list[NativeSentence]
    native_alternatives: list[NativeAnswerOption]
    native_distractors: list[NativeAnswerOption]

    native_hint: str | None = None
    native_explanation: str | None = None


class NativeDefinitionGuess(DefinitionGuess, NativeDefinitionGuessBase):
    @classmethod
    def from_page(cls, page: DefinitionGuess, native: NativeDefinitionGuessBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())


NativePage = Annotated[
    Union[
        NativeGapFillChoiceExercise,
        NativeInfoPage,
        NativeDefinitionGuess,
    ],
    Field(discriminator="type"),
]
