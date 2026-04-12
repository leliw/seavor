from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory, BaseAsyncQueryStorage
from fastapi import HTTPException
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate, TopicType


class TopicService:
    def __init__(self, factory: BaseAsyncFactory):
        self.factory = factory

    def _get_storage(self, language: Language, level: Level) -> BaseAsyncQueryStorage[Topic]:
        return self.factory.create_storage(f"target-languages/{language}/levels/{level}/topics", Topic)

    async def get_list(self, language: Language, level: Level, username: str | None = None) -> AsyncGenerator[Topic]:
        storage = self._get_storage(language, level)
        async for topic in storage.get_all():
            if topic.private and topic.username != username:
                continue
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
        topic = await storage.get(id)
        return topic

    async def get_for_user(self, language: Language, level: Level, id: UUID, username: str | None = None) -> Topic:
        topic = await self.get(language, level, id)
        if topic.private and topic.username != username:
            raise HTTPException(status_code=403, detail="Forbidden")
        return topic

    async def get_or_create_default_topic(self, language: Language, level: Level, username: str) -> Topic:
        storage = self._get_storage(language, level)
        async for topic in storage.where("username", "==", username).get_all():
            if topic.private and topic.title == "Default":
                return topic
        value = Topic.create(
            TopicCreate(
                language=language,
                level=level,
                title="Default",
                description="Various words and phrases",
                type=TopicType.VOCABULARY,
                private=True,
            ),
            username,
        )
        await storage.create(value)
        return value
