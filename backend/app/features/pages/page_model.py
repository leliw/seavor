from datetime import datetime, timezone
from enum import StrEnum
from typing import Dict, List, Literal, Optional, Self, Union
from uuid import UUID, uuid4

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class PageType(StrEnum):
    LETTER_SHUFFLE = "letter-shuffle"
    GAP_FILL_CHOICE = "gap-fill-choice"
    INFO = "info"


class PageHeader(BaseModel):
    id: UUID
    order: int
    type: PageType
    created_at: datetime
    updated_at: datetime

class BasePageCreate(BaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    target_language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this

class BasePage(BaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    target_language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this
    created_at: datetime
    updated_at: datetime



class GapFillChoiceExerciseCreate(BasePageCreate):
    type: Literal[PageType.GAP_FILL_CHOICE] = PageType.GAP_FILL_CHOICE
    target_sentence: str
    gap_marker: Optional[str] = None
    options: List[str]
    correct_index: int
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[str, str]] = None
    target_hint: Optional[str] = None

    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    target_hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercisePatch(BaseModel):
    level: Optional[Level] = None
    target_sentence: Optional[str] = None
    gap_marker: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[str, str]] = None
    target_hint: Optional[str] = None

    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    target_hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercise(BasePage):
    type: Literal[PageType.GAP_FILL_CHOICE] = PageType.GAP_FILL_CHOICE
    target_sentence: str
    gap_marker: str = "[____]"
    options: List[str]
    correct_index: int
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[str, str]] = None
    target_hint: Optional[str] = None

    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    target_hint_audio_file_name: Optional[str] = None

    @property
    def target_answer(self) -> str:
        correct_fill = self.options[self.correct_index]
        return self.target_sentence.replace(self.gap_marker, correct_fill)

    @classmethod
    def create(cls, value_create: GapFillChoiceExerciseCreate) -> Self:
        return cls(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **value_create.model_dump(),
        )

    def patch(self, patch_value: GapFillChoiceExercisePatch) -> None:
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict) # type: ignore
        self.updated_at = datetime.now(timezone.utc)


class GapFillChoiceExercisePut(GapFillChoiceExercise):
    pass


class InfoPageCreate(BasePageCreate):
    type: Literal[PageType.INFO]= PageType.INFO
    title: str
    content: str  # markdown / HTML / JSON


class InfoPage(BasePage):
    type: Literal[PageType.INFO]= PageType.INFO
    title: str
    content: str  # markdown / HTML / JSON
    image_url: str | None = None

    @classmethod
    def create(cls, value_create: InfoPageCreate) -> Self:
        return cls(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            **value_create.model_dump(),
        )


Page = Annotated[
    Union[
        GapFillChoiceExercise,
        InfoPage,
    ],
    Field(discriminator="type"),
]

PageCreate = Annotated[
    Union[
        GapFillChoiceExerciseCreate,
        InfoPageCreate,
    ],
    Field(discriminator="type"),
]
