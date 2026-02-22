from typing import Dict, Optional, Self, Union

from features.pages.page_model import GapFillChoiceExercise, InfoPage, PageHeader
from pydantic import BaseModel, Field
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


class NativeGapFillChoiceExercise(GapFillChoiceExercise, NativeGapFillChoiceExerciseBase):
    pass

    @classmethod
    def from_page(cls, page: GapFillChoiceExercise, native: NativeGapFillChoiceExerciseBase) -> Self:
        return cls(**page.model_dump(), **native.model_dump())


class NativeInfoPage(InfoPage):
    native_title: str
    native_content: str  # markdown / HTML / JSON

    @classmethod
    def from_page(cls, page: InfoPage, native_title: str, native_content: str) -> Self:
        return cls(
            native_title=native_title,
            native_content=native_content,
            **page.model_dump(),
        )


NativePage = Annotated[
    Union[
        NativeGapFillChoiceExercise,
        NativeInfoPage,
    ],
    Field(discriminator="type"),
]
