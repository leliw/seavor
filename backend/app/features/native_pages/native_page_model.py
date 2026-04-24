from typing import Dict, Optional, Self, Union

from features.pages.definition_guess_model import DefinitionGuess_v2
from features.pages.page_base_model import PageHeader
from features.pages.page_model import (
    GapFillChoiceExercise_v1,
    GapFillChoiceExercise_v2,
    InfoPage_v1,
    InfoPage_v2,
)
from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Annotated


class NativePageHeader(PageHeader):
    pass


class NativeGapFillChoiceExerciseBase(BaseModel):
    native_answer: str
    native_explanation: Optional[str] = None
    native_distractors_explanation: Optional[Dict[str, str]] = None
    native_hint: Optional[str] = None

    native_sentence_audio_file_name: Optional[str] = None
    native_explanation_audio_file_name: Optional[str] = None
    native_distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    native_hint_audio_file_name: Optional[str] = None


class NativeGapFillChoiceExercise_v1(GapFillChoiceExercise_v1, NativeGapFillChoiceExerciseBase):
    pass

    @classmethod
    def from_page(cls, page: GapFillChoiceExercise_v1, native: NativeGapFillChoiceExerciseBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())


class NativeGapFillChoiceExercise_v2(GapFillChoiceExercise_v2, NativeGapFillChoiceExerciseBase):
    pass

    @classmethod
    def from_page(cls, page: GapFillChoiceExercise_v2, native: NativeGapFillChoiceExerciseBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())

    @classmethod
    def from_storage(cls, data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = NativeGapFillChoiceExercise_v1.model_validate(data)
            return cls(
                v=1,
                language=v1.target_language,
                sentence=v1.target_sentence,
                explanation=v1.target_explanation,
                distractors_explanation=v1.target_distractors_explanation,
                hint=v1.target_hint,
                sentence_audio_file_name=v1.target_sentence_audio_file_name,
                explanation_audio_file_name=v1.target_explanation_audio_file_name,
                distractors_explanation_audio_file_name=v1.target_distractors_explanation_audio_file_name,
                hint_audio_file_name=v1.target_hint_audio_file_name,
                **v1.model_dump(
                    exclude={
                        "target_language",
                        "target_sentence",
                        "target_explanation",
                        "target_distractors_explanation",
                        "target_hint",
                        "target_sentence_audio_file_name",
                        "target_explanation_audio_file_name",
                        "target_distractors_explanation_audio_file_name",
                        "target_hint_audio_file_name",
                    }
                ),
            )

    def to_storage(self):
        if self.FORMAT_FLAGS.save_new_format:
            return self.model_dump(by_alias=True, exclude_none=True)
        else:
            return NativeGapFillChoiceExercise_v1(
                target_language=self.language,
                target_sentence=self.sentence,
                target_explanation=self.explanation,
                target_distractors_explanation=self.distractors_explanation,
                target_hint=self.hint,
                target_sentence_audio_file_name=self.sentence_audio_file_name,
                target_explanation_audio_file_name=self.explanation_audio_file_name,
                target_distractors_explanation_audio_file_name=self.distractors_explanation_audio_file_name,
                target_hint_audio_file_name=self.hint_audio_file_name,
                **self.model_dump(
                    exclude={
                        "v",
                        "language",
                        "sentence",
                        "explanation",
                        "distractors_explanation",
                        "hint",
                        "sentence_audio_file_name",
                        "explanation_audio_file_name",
                        "distractors_explanation_audio_file_name",
                        "hint_audio_file_name",
                    }
                ),
            ).model_dump(by_alias=True, exclude_none=True)


NativeGapFillChoiceExercise = NativeGapFillChoiceExercise_v2


class NativeInfoPageBase(BaseModel):
    native_title: str
    native_content: str  # markdown / HTML / JSON


class NativeInfoPage_v1(InfoPage_v1, NativeInfoPageBase):
    pass

    @classmethod
    def from_page(cls, page: InfoPage_v1, native: NativeInfoPageBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())


class NativeInfoPage_v2(InfoPage_v2, NativeInfoPageBase):
    pass

    @classmethod
    def from_page(cls, page: InfoPage_v2, native: NativeInfoPageBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())

    @classmethod
    def from_storage(cls, data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = NativeInfoPage_v1.model_validate(data)
            return cls(v=1, language=v1.target_language, **v1.model_dump(exclude={"target_language"}))

    def to_storage(self):
        if self.FORMAT_FLAGS.save_new_format:
            return self.model_dump(by_alias=True, exclude_none=True)
        else:
            return NativeInfoPage_v1(target_language=self.language, **self.model_dump(exclude={"language"})).model_dump(
                by_alias=True, exclude_none=True
            )


NativeInfoPage = NativeInfoPage_v2

class NativeSentence(BaseModel):
    text: str

class NativeAnswerOption(BaseModel):
    value: str
    explanation: Optional[str] = None

class NativeDefinitionGuessBase(BaseModel):
    native_phrase: str
    native_definition: str  # markdown / HTML / JSON

    native_sentences: list[NativeSentence]
    native_alternatives: list[NativeAnswerOption]
    native_distractors: list[NativeAnswerOption]

    native_hint: Optional[str] = None
    native_explanation: Optional[str] = None

class NativeDefinitionGuess_v2(DefinitionGuess_v2, NativeDefinitionGuessBase):
    pass

    @classmethod
    def from_page(cls, page: DefinitionGuess_v2, native: NativeDefinitionGuessBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())

    @classmethod
    def from_storage(cls, data: dict):
        if "description" in data:
            data["definition"] = data.pop("description")
        if "description_audio_file_name" in data:
            data["definition_audio_file_name"] = data.pop("description_audio_file_name")
        return cls.model_validate(data)

    def to_storage(self):
        return self.model_dump(by_alias=True, exclude_none=True)

NativeDefinitionGuess = NativeDefinitionGuess_v2

NativePage_v1 = Annotated[
    Union[
        NativeGapFillChoiceExercise_v1,
        NativeInfoPage_v1,
    ],
    Field(discriminator="type"),
]

NativePage_v2 = Annotated[
    Union[
        NativeGapFillChoiceExercise_v2,
        NativeInfoPage_v2,
        NativeDefinitionGuess_v2,
    ],
    Field(discriminator="type"),
]

NativePage = NativePage_v2
