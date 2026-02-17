from datetime import datetime, timezone
from typing import Dict, List, Optional, Self
from uuid import UUID, uuid4

from features.languages import Language
from features.levels import LevelRange


class GapFillChoiceExerciseHeader(LevelRange):
    id: UUID
    target_language_code: Language
    created_at: datetime
    updated_at: datetime


class GapFillChoiceExerciseCreate(LevelRange):
    target_language_code: Language
    target_sentence: str
    gap_marker: Optional[str] = None
    options: List[str]
    correct_index: int
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[int, str]] = None

    hint: Optional[str] = None
    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[int, str]] = None
    target_hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercisePatch(LevelRange):
    target_sentence: Optional[str] = None
    gap_marker: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[int, str]] = None

    hint: Optional[str] = None
    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[int, str]] = None
    target_hint_audio_file_name: Optional[str] = None


class GapFillChoiceExercise(LevelRange):
    id: UUID
    target_language_code: Language
    target_sentence: str
    gap_marker: Optional[str] = None
    options: List[str]
    correct_index: int
    target_explanation: Optional[str] = None
    target_distractors_explanation: Optional[Dict[int, str]] = None

    hint: Optional[str] = None
    target_sentence_audio_file_name: Optional[str] = None
    target_explanation_audio_file_name: Optional[str] = None
    target_distractors_explanation_audio_file_name: Optional[Dict[int, str]] = None
    target_hint_audio_file_name: Optional[str] = None

    created_at: datetime
    updated_at: datetime

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
        self.__dict__.update(patch_dict)
        self.updated_at = datetime.now(timezone.utc)


class GapFillChoiceExercisePut(GapFillChoiceExercise):
    pass
