from datetime import datetime, timezone
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4, uuid5

from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from pydantic import BaseModel


class TopicType(StrEnum):
    LETTER_SHUFFLE = "letter-shuffle"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"


class TopicCreate(BaseModel):
    target_language_code: Language
    level: Level
    type: TopicType
    target_title: str
    target_description: str
    image_name: Optional[str] = None


class Topic(BaseModel):
    id: UUID
    content_id: Optional[UUID] = None
    content_type: Optional[str] = None
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    native_language_code: Optional[Language] = None
    native_title: Optional[str] = None
    native_description: Optional[str] = None
    image_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, value_create: TopicCreate) -> "Topic":
        return cls(
            id=uuid4(),
            target_language_code=value_create.target_language_code,
            levels=[value_create.level],
            target_title=value_create.target_title,
            target_description=value_create.target_description,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def from_letter_shuffle_translation(cls, level: Level, value: LetterShuffleSetTranslation) -> "Topic":
        return cls(
            id=uuid5(value.id, level),
            content_id=value.id,
            content_type="letter-shuffle",
            target_language_code=value.target_language_code,
            levels=value.levels,
            target_title=value.target_title,
            target_description=value.target_description,
            native_language_code=value.native_language_code,
            native_title=value.native_title,
            native_description=value.native_description,
            image_name=value.image_name,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )
