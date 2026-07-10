from typing import Any, Self
from uuid import uuid5

from ampf.base import VersionedBaseModel
from core.translation_status import TranslationStatus
from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.topics.topic_model import Topic, TopicHeader, TopicType
from pydantic import BaseModel, model_validator


class NativeTopicBase(BaseModel):
    native_language: Language
    native_title: str
    native_description: str

    translation_status: TranslationStatus = "pending"
    error_message: str | None = None

    @model_validator(mode="before")
    @classmethod
    def infer_status_for_legacy_data(cls, data: Any) -> Any:
        if isinstance(data, dict) and "translation_status" not in data:
            data["translation_status"] = "ready"
        return data


class NativeTopicHeader(TopicHeader, NativeTopicBase):
    pass


class NativeTopic(Topic, NativeTopicBase, VersionedBaseModel):
    CURRENT_VERSION = 2

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
            v=2,
            id=uuid5(value.id, level),
            content_id=value.id,
            content_type="letter-shuffle",
            language=value.target_language_code,
            level=level,
            type=TopicType.LETTER_SHUFFLE,
            title=value.target_title,
            description=value.target_description,
            native_language=value.native_language_code,
            native_title=value.native_title,
            native_description=value.native_description,
            image_name=value.image_name,
            private=False,
            created_at=value.created_at,
            updated_at=value.updated_at,
        )
