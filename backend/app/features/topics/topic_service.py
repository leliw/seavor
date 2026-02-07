from typing import AsyncGenerator
from ampf.base import BaseAsyncFactory

from features.topics.topic_model import Topic


class TopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    async def get_list(self, target_language_code: str, level: str, native_language_code: str) -> AsyncGenerator[Topic]:
        storage = self.factory.create_storage(f"target-languages/{target_language_code}/levels/{level}/native-languages/{native_language_code}/topics", Topic)
        async for topic in storage.get_all():
            yield topic
        
    async def save(self, value: Topic) -> None:
        target_language_code = value.target_language_code
        level = value.level
        native_language_code = value.native_language_code
        storage = self.factory.create_storage(f"target-languages/{target_language_code}/levels/{level}/native-languages/{native_language_code}/topics", Topic)
        await storage.save(value)

