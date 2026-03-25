from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory, BaseAsyncStorage
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate


class TopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    def _get_storage(self, language: Language, level: Level) -> BaseAsyncStorage[Topic]:
        return self.factory.create_storage(f"target-languages/{language}/levels/{level}/topics", Topic)

    async def get_list(self, language: Language, level: Level) -> AsyncGenerator[Topic]:
        storage = self._get_storage(language, level)
        async for topic in storage.get_all():
            yield topic

    async def save(self, value: Topic, level: Optional[Level] = None) -> None:
        storage = self._get_storage(value.language, value.level)
        await storage.save(value)

    async def create(self, value_create: TopicCreate, username: str | None = None) -> Topic:
        value = Topic.create(value_create, username)
        language = value.language
        level = value_create.level
        storage = self._get_storage(language, level)
        await storage.create(value)
        return value

    async def get(self, language: Language, level: Level, id: UUID) -> Topic:
        storage = self._get_storage(language, level)
        return await storage.get(id)
