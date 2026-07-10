from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Self, Union, override
from uuid import uuid4

from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, DefinitionGuessPatch
from features.pages.page_base_model import BasePage, BasePageCreate, PageType
from pydantic import BaseModel, Field
from typing_extensions import Annotated


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

    def get_texts_to_synthesize(self) -> set[str]:
        ret = set()
        if self.sentence:
            ret.add(self.sentence)
        if self.explanation:
            ret.add(self.explanation)
        if self.hint:
            ret.add(self.hint)
        if self.distractors_explanation:
            for distractor in self.distractors_explanation.items():
                ret.add(distractor[1])
        return ret

    def set_audio_file_names(self, audio_file_names: dict[str, str]) -> None:
        if self.sentence:
            self.sentence_audio_file_name = audio_file_names[self.sentence]
        if self.explanation:
            self.explanation_audio_file_name = audio_file_names[self.explanation]
        if self.hint:
            self.hint_audio_file_name = audio_file_names[self.hint]
        if self.distractors_explanation:
            self.distractors_explanation_audio_file_name = {
                k: audio_file_names[v] for k, v in self.distractors_explanation.items()
            }


class GapFillChoiceExercisePatch(BaseModel):
    type: Literal[PageType.GAP_FILL_CHOICE] = PageType.GAP_FILL_CHOICE
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

    def model_post_init(self, __context):
        self.__pydantic_fields_set__.add("type")


class GapFillChoiceExercise(BasePage):
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

    @override
    def get_audio_file_names(self) -> set[str]:
        ret = set()
        if self.sentence_audio_file_name:
            ret.add(self.sentence_audio_file_name)
        if self.explanation_audio_file_name:
            ret.add(self.explanation_audio_file_name)
        if self.hint_audio_file_name:
            ret.add(self.hint_audio_file_name)
        if self.distractors_explanation_audio_file_name:
            for distractor in self.distractors_explanation_audio_file_name.values():
                ret.add(distractor)
        return ret

    @override
    def get_image_file_names(self) -> set[str]:
        return set()


class GapFillChoiceExercisePut(GapFillChoiceExercise):
    pass


class InfoPageCreate(BasePageCreate):
    type: Literal[PageType.INFO] = PageType.INFO
    title: str
    content: str  # markdown / HTML / JSON


class InfoPage(BasePage):
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

    @override
    def get_audio_file_names(self) -> set[str]:
        return set()

    @override
    def get_image_file_names(self) -> set[str]:
        return {self.image_url} if self.image_url else set()


Page = Annotated[
    Union[
        GapFillChoiceExercise,
        InfoPage,
        DefinitionGuess,
    ],
    Field(discriminator="type"),
]

PageCreate = Annotated[
    Union[
        GapFillChoiceExerciseCreate,
        InfoPageCreate,
        DefinitionGuessCreate,
    ],
    Field(discriminator="type"),
]

PagePatch = Annotated[
    Union[
        GapFillChoiceExercisePatch,
        # InfoPagePatch,
        DefinitionGuessPatch,
    ],
    Field(discriminator="type"),
]
