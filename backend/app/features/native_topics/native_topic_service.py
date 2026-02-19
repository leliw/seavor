from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory, BaseAsyncStorage
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic, NativeTopicCreate


class NativeTopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    def _get_storage(self, target_language: Language, level: Level, native_language: Language) -> BaseAsyncStorage[NativeTopic]:
        return self.factory.create_storage(f"target-languages/{target_language}/levels/{level}/native-languages/{native_language}/topics", NativeTopic)
    
    async def get_list(
        self, target_language: Language, level: Level, native_language: Language
    ) -> AsyncGenerator[NativeTopic]:
        storage = self._get_storage(target_language, level, native_language)
        async for topic in storage.get_all():
            yield topic

    async def save(self, value: NativeTopic, level: Optional[Level] = None) -> None:
        target_language = value.target_language
        if not level and value.levels and len(value.levels) == 1:
            level = value.levels[0]
        elif not level:
            raise ValueError("Level is required")
        native_language = value.native_language
        storage = self._get_storage(target_language, level, native_language)
        await storage.save(value)

    async def create(self, value_create: NativeTopicCreate) -> NativeTopic:
        value = NativeTopic.create(value_create)
        target_language = value.target_language
        level = value_create.level
        native_language = value_create.native_language
        storage = self._get_storage(target_language, level, native_language)
        await storage.create(value)
        return value

    async def get(self, target_language: Language, level: Level, native_language: Language, id: UUID) -> NativeTopic:
        storage = self._get_storage(target_language, level, native_language)
        return await storage.get(id)
