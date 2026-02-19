from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory, BaseAsyncStorage
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic


class NativeTopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    def _get_storage(
        self, target_language: Language, level: Level, native_language: Language
    ) -> BaseAsyncStorage[NativeTopic]:
        return self.factory.create_storage(
            f"target-languages/{target_language}/levels/{level}/native-languages/{native_language}/topics", NativeTopic
        )

    async def get_list(
        self, target_language: Language, level: Level, native_language: Language
    ) -> AsyncGenerator[NativeTopic]:
        storage = self._get_storage(target_language, level, native_language)
        async for topic in storage.get_all():
            yield topic

    async def save(self, value: NativeTopic) -> None:
        storage = self._get_storage(value.target_language, value.level, value.native_language)
        await storage.save(value)

    async def create(self, value: NativeTopic) -> NativeTopic:
        storage = self._get_storage(value.target_language, value.level, value.native_language)
        await storage.create(value)
        return value

    async def get(self, target_language: Language, level: Level, native_language: Language, id: UUID) -> NativeTopic:
        storage = self._get_storage(target_language, level, native_language)
        return await storage.get(id)
