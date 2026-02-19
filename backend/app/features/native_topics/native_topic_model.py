from typing import Self
from uuid import uuid5

from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.topics.topic_model import Topic, TopicHeader
from pydantic import BaseModel


class NativeTopicBase(BaseModel):
    native_language: Language
    native_title: str
    native_description: str


class NativeTopicHeader(TopicHeader, NativeTopicBase):
    pass


class NativeTopic(Topic, NativeTopicBase):
    pass

    @classmethod
    def from_topic(cls, topic: Topic, native_language: Language, native_title: str, native_description: str) -> Self:
        return cls(
            native_language=native_language,
            native_title=native_title,
            native_description=native_description,
            **topic.model_dump(),
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
