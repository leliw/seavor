from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate


class TopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    async def get_list(self, target_language_code: str, level: str, native_language_code: str) -> AsyncGenerator[Topic]:
        storage = self.factory.create_storage(
            f"target-languages/{target_language_code}/levels/{level}/native-languages/{native_language_code}/topics",
            Topic,
        )
        async for topic in storage.get_all():
            yield topic

    async def save(self, value: Topic, level: Optional[Level] = None) -> None:
        target_language_code = value.target_language_code
        if not level and value.levels and len(value.levels) == 1:
            level = value.levels[0]
        elif not level:
            raise ValueError("Level is required")
        native_language_code = value.native_language_code
        storage = self.factory.create_storage(
            f"target-languages/{target_language_code}/levels/{level}/native-languages/{native_language_code}/topics",
            Topic,
        )
        await storage.save(value)

    async def create(self, value_create: TopicCreate) -> Topic:
        value = Topic.create(value_create)
        target_language_code = value.target_language_code
        level = value_create.level
        storage = self.factory.create_storage(f"target-languages/{target_language_code}/levels/{level}/topics", Topic)
        await storage.create(value)
        return value

    async def get(self, target_language_code: str, level: str, id: UUID) -> Topic:
        storage = self.factory.create_storage(f"target-languages/{target_language_code}/levels/{level}/topics", Topic)
        return await storage.get(id)