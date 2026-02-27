from datetime import datetime, timezone
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from ampf.base import VersionedBaseModel

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel, ValidationError


class TopicType(StrEnum):
    LETTER_SHUFFLE = "letter-shuffle"
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"


class TopicHeader(BaseModel):
    language: Language
    level: Level
    type: TopicType
    title: str
    description: str
    image_name: Optional[str] = None


class TopicCreate(BaseModel):
    language: Language
    level: Level
    type: TopicType
    title: str
    description: str
    image_name: Optional[str] = None


class Topic_v1(BaseModel):
    v: int = 1
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
    def create(cls, value_create: TopicCreate) -> "Topic_v1":
        return cls(
            id=uuid4(),
            target_language=value_create.language,
            levels=[value_create.level],
            type=value_create.type,
            target_title=value_create.title,
            target_description=value_create.description,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


class Topic_v2(VersionedBaseModel):
    CURRENT_VERSION = 2
    id: UUID
    content_id: Optional[UUID] = None
    content_type: Optional[str] = None
    language: Language
    level: Level
    type: TopicType
    title: str
    description: str
    image_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


    @classmethod
    def create(cls, value_create: TopicCreate) -> "Topic_v2":
        return cls(
            id=uuid4(),
            language=value_create.language,
            level=value_create.level,
            type=value_create.type,
            title=value_create.title,
            description=value_create.description,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def from_storage(cls, data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = Topic_v1.model_validate(data)
            return cls(
                v=v1.v,
                id=v1.id,
                content_id=v1.content_id,
                content_type=v1.content_type,
                language=v1.target_language,
                level=v1.level,
                type=v1.type,
                title=v1.target_title,
                description=v1.target_description,
                image_name=v1.image_name,
                created_at=v1.created_at,
                updated_at=v1.updated_at,
            )

    def to_storage(self):
        if self.FORMAT_FLAGS.save_new_format:
            return self.model_dump(by_alias=True, exclude_none=True)
        else:
            return Topic_v1(
                id=self.id,
                content_id=self.content_id,
                content_type=self.content_type,
                target_language=self.language,
                levels=[self.level],
                type=self.type,
                target_title=self.title,
                target_description=self.description,
                image_name=self.image_name,
                created_at=self.created_at,
                updated_at=self.updated_at,
            ).model_dump(by_alias=True, exclude_none=True)


Topic = Topic_v2
