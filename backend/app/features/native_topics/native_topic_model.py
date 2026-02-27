from datetime import datetime
from typing import List, Optional, Self
from uuid import UUID, uuid5

from ampf.base import VersionedBaseModel

from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.topics.topic_model import Topic, TopicHeader, TopicType
from pydantic import BaseModel, ValidationError


class NativeTopic_v1(BaseModel):
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
    image_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_letter_shuffle_translation(cls, level: Level, value: LetterShuffleSetTranslation) -> "NativeTopic_v1":
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


class NativeTopicBase(BaseModel):
    native_language: Language
    native_title: str
    native_description: str


class NativeTopicHeader(TopicHeader, NativeTopicBase):
    pass


class NativeTopic_v2(Topic, NativeTopicBase, VersionedBaseModel):
    CURRENT_VERSION = 2
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
    def from_v1(cls, v1: NativeTopic_v1) -> Self:
        return cls(
            v=1,
            id=v1.id,
            content_id=v1.content_id,
            content_type=v1.content_type,
            language=v1.target_language_code,
            levels=v1.levels,
            type=TopicType.LETTER_SHUFFLE if v1.content_type=="letter-shuffle" else TopicType.GRAMMAR,
            title=v1.target_title,
            description=v1.target_description,
            native_language=v1.native_language_code,
            native_title=v1.native_title,
            native_description=v1.native_description,
            image_name=v1.image_name,
            created_at=v1.created_at,
            updated_at=v1.updated_at,
        )

    @classmethod
    def from_letter_shuffle_translation(cls, level: Level, value: LetterShuffleSetTranslation) -> Self:
        return cls.from_v1(NativeTopic_v1.from_letter_shuffle_translation(level, value))

    @classmethod
    def from_storage(cls, data: dict) -> Self:
        try:
            return cls.model_validate(data)
        except ValidationError:
            v1 = NativeTopic_v1.model_validate(data)
            return cls.from_v1(v1)

    def to_storage(self):
        if self.FORMAT_FLAGS.save_new_format:
            return self.model_dump(by_alias=True, exclude_none=True)
        else:
            v2 = self
            v1 = NativeTopic_v1(
                id=v2.id,
                content_id=v2.content_id,
                content_type=v2.content_type,
                target_language_code=v2.language,
                levels=v2.levels,
                target_title=v2.title,
                target_description=v2.description,
                native_language_code=v2.native_language,
                native_title=v2.native_title,
                native_description=v2.native_description,
                image_name=v2.image_name,
                created_at=v2.created_at,
                updated_at=v2.updated_at,
            )
            return v1.model_dump(by_alias=True, exclude_none=True)


NativeTopic = NativeTopic_v2
