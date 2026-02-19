from datetime import datetime, timezone
from typing import Self
from uuid import uuid4, uuid5

from pydantic import BaseModel

from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate, TopicHeader


class NativeTopicBase(BaseModel):
    native_language: Language
    native_title: str
    native_description: str

class NativeTopicCreate(TopicCreate, NativeTopicBase):
    pass

class NativeTopicHeader(TopicHeader, NativeTopicBase):
    pass

class NativeTopic(Topic, NativeTopicBase):
    pass

    @classmethod
    def create(cls, value_create: NativeTopicCreate) -> Self:
        return cls(
            id=uuid4(),
            target_language=value_create.target_language,
            levels=[value_create.level],
            target_title=value_create.target_title,
            target_description=value_create.target_description,
            native_language=value_create.native_language,
            native_title=value_create.native_title,
            native_description=value_create.native_description,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    @classmethod
    def from_letter_shuffle_translation(cls, level: Level, value: LetterShuffleSetTranslation) -> Self:
        return cls(
            id=uuid5(value.id, level),
            content_id=value.id,
            content_type="letter-shuffle",
            target_language=value.target_language_code,
            levels=value.levels,
            target_title=value.target_title,
            target_description=value.target_description,
            native_language=value.native_language_code,
            native_title=value.native_title,
            native_description=value.native_description,
            image_name=value.image_name,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )
