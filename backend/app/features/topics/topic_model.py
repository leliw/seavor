from datetime import datetime, timezone
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel


class TopicType(StrEnum):
    LETTER_SHUFFLE = "letter-shuffle"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"


class TopicHeader(BaseModel):
    target_language: Language
    level: Level
    type: TopicType
    target_title: str
    target_description: str
    image_name: Optional[str] = None


class TopicCreate(BaseModel):
    target_language: Language
    level: Level
    type: TopicType
    target_title: str
    target_description: str
    image_name: Optional[str] = None


class Topic(BaseModel):
    id: UUID
    content_id: Optional[UUID] = None
    content_type: Optional[str] = None
    target_language: Language
    levels: Optional[List[Level]] = None
    type: TopicType
    target_title: str
    target_description: str
    image_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @property
    def level(self) -> Level:
        if not self.levels:
            raise ValueError("Level is required")
        if len(self.levels) > 1:
            raise ValueError("Level is not unique")
        return self.levels[0]

    @classmethod
    def create(cls, value_create: TopicCreate) -> "Topic":
        return cls(
            id=uuid4(),
            target_language=value_create.target_language,
            levels=[value_create.level],
            type=value_create.type,
            target_title=value_create.target_title,
            target_description=value_create.target_description,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
