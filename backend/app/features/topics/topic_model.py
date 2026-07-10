import logging
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from ampf.base import VersionedBaseModel
from features.languages import Language
from features.levels import Level
from pydantic import BaseModel

_log = logging.getLogger(__name__)


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
    image_name: str | None = None


class TopicCreate(BaseModel):
    language: Language
    level: Level
    type: TopicType
    title: str
    description: str
    image_name: str | None = None
    private: bool = True


class Topic(VersionedBaseModel):
    CURRENT_VERSION = 2
    id: UUID
    username: str | None = None
    content_id: UUID | None = None
    content_type: str | None = None
    language: Language
    level: Level
    type: TopicType = TopicType.VOCABULARY
    title: str
    description: str
    image_name: str | None = None
    private: bool = True
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, value_create: TopicCreate, username: str | None = None) -> "Topic":
        return cls(
            id=uuid4(),
            username=username,
            language=value_create.language,
            level=value_create.level,
            type=value_create.type,
            title=value_create.title,
            description=value_create.description,
            image_name=value_create.image_name,
            private=value_create.private,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def from_storage(cls, data: dict):
        return cls.model_validate(data)

    def to_storage(self):
        self.v = self.CURRENT_VERSION
        return self.model_dump(by_alias=True, exclude_none=True)
