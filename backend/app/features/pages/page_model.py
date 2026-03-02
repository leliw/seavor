from datetime import datetime, timezone
from enum import StrEnum
from typing import Dict, List, Literal, Optional, Self, Union
from uuid import UUID, uuid4

from ampf.base import VersionedBaseModel

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel, ConfigDict, Field, ValidationError
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

    language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this


class BasePage_v1(BaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    target_language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this
    created_at: datetime
    updated_at: datetime


class BasePage_v2(VersionedBaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this
    created_at: datetime
    updated_at: datetime


BasePage = BasePage_v2


class GapFillChoiceExerciseCreate(BasePageCreate):
    type: Literal[PageType.GAP_FILL_CHOICE] = PageType.GAP_FILL_CHOICE
    sentence: str
    gap_marker: Optional[str] = None
    options: List[str]
    correct_index: int
    explanation: Optional[str] = None
    distractors_explanation: Optional[Dict[str, str]] = None
    hint: Optional[str] = None

    sentence_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None
    distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercisePatch(BaseModel):
    level: Optional[Level] = None
    sentence: Optional[str] = None
    gap_marker: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    distractors_explanation: Optional[Dict[str, str]] = None
    hint: Optional[str] = None

    sentence_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None
    distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercise_v1(BasePage_v1):
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
        self.__dict__.update(patch_dict)  # type: ignore
        self.updated_at = datetime.now(timezone.utc)


class GapFillChoiceExercise_v2(BasePage_v2):
    CURRENT_VERSION = 2

    type: Literal[PageType.GAP_FILL_CHOICE] = PageType.GAP_FILL_CHOICE
    sentence: str
    gap_marker: str = "[____]"
    options: List[str]
    correct_index: int
    explanation: Optional[str] = None
    distractors_explanation: Optional[Dict[str, str]] = None
    hint: Optional[str] = None

    sentence_audio_file_name: Optional[str] = None
    explanation_audio_file_name: Optional[str] = None
    distractors_explanation_audio_file_name: Optional[Dict[str, str]] = None
    hint_audio_file_name: Optional[str] = None

    @property
    def answer(self) -> str:
        correct_fill = self.options[self.correct_index]
        return self.sentence.replace(self.gap_marker, correct_fill)

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
        self.__dict__.update(patch_dict)  # type: ignore
        self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def from_storage(cls, data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = GapFillChoiceExercise_v1.model_validate(data)
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
            return GapFillChoiceExercise_v1(
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


GapFillChoiceExercise = GapFillChoiceExercise_v2


class GapFillChoiceExercisePut(GapFillChoiceExercise):
    pass


class InfoPageCreate(BasePageCreate):
    type: Literal[PageType.INFO] = PageType.INFO
    title: str
    content: str  # markdown / HTML / JSON


class InfoPage_v1(BasePage_v1):
    type: Literal[PageType.INFO] = PageType.INFO
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


class InfoPage_v2(BasePage_v2):
    CURRENT_VERSION = 2

    type: Literal[PageType.INFO] = PageType.INFO
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

    @classmethod
    def from_storage(cls, data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = InfoPage_v1.model_validate(data)
            return cls(
                v=1,
                language=v1.target_language,
                **v1.model_dump(exclude={"target_language"}),
            )

    def to_storage(self):
        if self.FORMAT_FLAGS.save_new_format:
            return self.model_dump(by_alias=True, exclude_none=True)
        else:
            return InfoPage_v1(
                target_language=self.language,
                **self.model_dump(exclude={"language"}),
            ).model_dump(by_alias=True, exclude_none=True)


InfoPage = InfoPage_v2

Page_v1 = Annotated[
    Union[
        GapFillChoiceExercise_v1,
        InfoPage_v1,
    ],
    Field(discriminator="type"),
]

Page_v2 = Annotated[
    Union[
        GapFillChoiceExercise_v2,
        InfoPage_v2,
    ],
    Field(discriminator="type"),
]

Page = Page_v2

PageCreate = Annotated[
    Union[
        GapFillChoiceExerciseCreate,
        InfoPageCreate,
    ],
    Field(discriminator="type"),
]
