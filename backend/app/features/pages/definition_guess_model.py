from datetime import datetime, timezone
from typing import Any, Literal, Optional, Self
from uuid import uuid4

from features.pages.page_base_model import BasePage_v2, BasePageCreate, PageType
from pydantic import BaseModel


class Sentence(BaseModel):
    text_with_gap: str
    gap_filler_form: str
    audio_file_name: Optional[str] = None


class AnswerOption(BaseModel):
    value: str
    explanation: Optional[str] = None
    audio_file_name: Optional[str] = None


class DefinitionGuessCreate(BasePageCreate):
    type: Literal[PageType.DEFINITION_GUESS] = PageType.DEFINITION_GUESS

    phrase: str
    definition: str

    sentences: list[Sentence]
    alternatives: list[AnswerOption]
    distractors: list[AnswerOption]

    hint: Optional[str] = None
    explanation: Optional[str] = None

    image_names: Optional[list[str]] = None
    phrase_audio_file_name: Optional[str] = None
    description_audio_file_name: Optional[str] = None
    hint_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None


class DefinitionGuessPatch(BaseModel):
    phrase: Optional[str] = None
    definition: Optional[str] = None

    sentences: Optional[list[Sentence]] = None
    alternatives: Optional[list[AnswerOption]] = None
    distractors: Optional[list[AnswerOption]] = None

    hint: Optional[str] = None
    explanation: Optional[str] = None

    image_names: Optional[list[str]] = None
    phrase_audio_file_name: Optional[str] = None
    description_audio_file_name: Optional[str] = None
    hint_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None


class DefinitionGuess_v2(BasePage_v2):
    CURRENT_VERSION = 2

    type: Literal[PageType.DEFINITION_GUESS] = PageType.DEFINITION_GUESS
    phrase: str
    definition: str

    sentences: list[Sentence]
    alternatives: list[AnswerOption]
    distractors: list[AnswerOption]

    hint: Optional[str] = None
    explanation: Optional[str] = None

    image_names: Optional[list[str]] = None
    phrase_audio_file_name: Optional[str] = None
    description_audio_file_name: Optional[str] = None
    hint_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None

    @classmethod
    def create(cls, value_create: DefinitionGuessCreate) -> Self:
        return cls(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **value_create.model_dump(),
        )

    def patch(self, patch_value: DefinitionGuessPatch) -> None:
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict)  # type: ignore
        self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def from_storage(cls, data: dict[str, Any]):
        return cls.model_validate(data)

    def to_storage(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


DefinitionGuess = DefinitionGuess_v2
