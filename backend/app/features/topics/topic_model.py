from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid5

from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from pydantic import BaseModel


class Topic(BaseModel):
    id: UUID
    content_id: Optional[UUID] = None
    content_type: Optional[str] = None
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    native_language_code: Language
    native_title: str
    native_description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_letter_shuffle_translation(cls, level: Level, value: LetterShuffleSetTranslation) -> "Topic":
        return cls(
            id=uuid5(value.id, level),
            content_id = value.id,
            content_type = "letter-shuffle",
            target_language_code=value.target_language_code,
            levels=value.levels,
            target_title=value.target_title,
            target_description=value.target_description,
            native_language_code=value.native_language_code,
            native_title=value.native_title,
            native_description=value.native_description,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )
