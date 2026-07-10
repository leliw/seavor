import asyncio
import logging
from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncFactory
from fastapi import HTTPException
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_service import NativeTopicService
from features.pages.page_service import PageServiceFactory
from features.topics.topic_model import Topic, TopicCreate, TopicType

_log = logging.getLogger(__name__)


class TopicService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        page_service_factory: PageServiceFactory,
        native_topic_service: NativeTopicService,
    ):
        self.factory = factory
        self.storage = self.factory.get_collection(Topic)
        self.page_service_factory = page_service_factory
        self.native_topic_service = native_topic_service

    async def get_list(self, language: Language, level: Level, username: str | None = None) -> AsyncGenerator[Topic]:
        storage = self.storage
        levels_filter = list(dict.fromkeys([level, Level.ALL]))
        async for topic in storage.where("language", "==", language).where("level", "in", levels_filter).get_all():
            if topic.private and topic.username != username:
                continue
            yield topic

    async def save(self, value: Topic, level: Optional[Level] = None) -> None:
        await self.storage.save(value)

    async def create(self, value_create: TopicCreate, username: str | None = None) -> Topic:
        value = Topic.create(value_create, username)
        await self.storage.create(value)
        return value

    async def get(self, id: UUID) -> Topic:
        return await self.storage.get(id)

    async def get_for_user(self, id: UUID, username: str | None = None) -> Topic:
        topic = await self.get(id)
        if topic.private and topic.username != username:
            raise HTTPException(status_code=403, detail="Forbidden")
        return topic

    async def get_or_create_default_topic(self, language: Language, username: str) -> Topic:
        async for topic in self.storage.where("username", "==", username).where("language", "==", language).get_all():
            if topic.private and topic.title == "Default":
                return topic
        value = TopicCreate(
            language=language,
            level=Level.ALL,
            title="Default",
            description="Various words and phrases",
            type=TopicType.VOCABULARY,
            private=True,
        )
        return await self.create(value, username)

    async def delete(self, id: UUID) -> None:
        # Delete native topics
        delete_ntopic_tasks = []
        for native_language in Language:
            delete_ntopic_tasks.append(self.native_topic_service.delete(native_language, id))
        await asyncio.gather(*delete_ntopic_tasks, return_exceptions=True)
        # Delete pages
        page_service = self.page_service_factory.create(id)
        delete_page_tasks = []
        async for page in page_service.get_all():
            delete_page_tasks.append(page_service.delete(page.id))
        await asyncio.gather(*delete_page_tasks, return_exceptions=True)
        # Delete topic itself
        await self.storage.delete(id)
