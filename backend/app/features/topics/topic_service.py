from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory, BaseAsyncStorage
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate


class TopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    def _get_storage(self, target_language: Language, level: Level) -> BaseAsyncStorage[Topic]:
        return self.factory.create_storage(f"target-languages/{target_language}/levels/{level}/topics", Topic)

    async def get_list(self, target_language: Language, level: Level) -> AsyncGenerator[Topic]:
        storage = self._get_storage(target_language, level)
        async for topic in storage.get_all():
            yield topic

    async def save(self, value: Topic, level: Optional[Level] = None) -> None:
        target_language = value.target_language
        if not level and value.levels and len(value.levels) == 1:
            level = value.levels[0]
        elif not level:
            raise ValueError("Level is required")
        storage = self._get_storage(target_language, level)
        await storage.save(value)

    async def create(self, value_create: TopicCreate) -> Topic:
        value = Topic.create(value_create)
        target_language = value.target_language
        level = value_create.level
        storage = self._get_storage(target_language, level)
        await storage.create(value)
        return value

    async def get(self, target_language: Language, level: Level, id: UUID) -> Topic:
        storage = self._get_storage(target_language, level)
        return await storage.get(id)
