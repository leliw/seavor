import asyncio
import logging
from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory, KeyNotExistsException
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
        self.new_storage = self.factory.get_collection(Topic)
        self.page_service_factory = page_service_factory
        self.native_topic_service = native_topic_service

    def _get_old_storage(self, language: Language, level: Level) -> BaseAsyncCollectionStorage[Topic]:
        return (
            self.factory.get_collection("target-languages")
            .get_collection(language, "levels")
            .get_collection(level, Topic)
        )

    async def get_list(self, language: Language, level: Level, username: str | None = None) -> AsyncGenerator[Topic]:
        storage = self.new_storage
        async for topic in storage.where("language", "==", language).where("level", "==", level).get_all():
            if topic.private and topic.username != username:
                continue
            yield topic

    async def save(self, value: Topic, level: Optional[Level] = None) -> None:
        storage = self._get_old_storage(value.language, value.level)
        await storage.save(value)
        try:
            await self.new_storage.save(value)
        except Exception as e:
            _log.error(f"Error saving in new storage: {e}")
            pass

    async def create(self, value_create: TopicCreate, username: str | None = None) -> Topic:
        value = Topic.create(value_create, username)
        language = value.language
        level = value_create.level
        storage = self._get_old_storage(language, level)
        await storage.create(value)
        try:
            await self.new_storage.create(value)
        except Exception as e:
            _log.error(f"Error creating in new storage: {e}")
            pass
        return value

    async def get(self, language: Language, level: Level, id: UUID) -> Topic:
        try:
            topic = await self.new_storage.get(id)
        except KeyNotExistsException:
            storage = self._get_old_storage(language, level)
            topic = await storage.get(id)
        return topic

    async def get_for_user(self, language: Language, level: Level, id: UUID, username: str | None = None) -> Topic:
        topic = await self.get(language, level, id)
        if topic.private and topic.username != username:
            raise HTTPException(status_code=403, detail="Forbidden")
        return topic

    async def get_or_create_default_topic(self, language: Language, level: Level, username: str) -> Topic:
        storage = self.new_storage
        async for topic in storage.where("username", "==", username).where("language", "==", language).where("level", "==", level).get_all():
            if topic.private and topic.title == "Default":
                return topic
        value = TopicCreate(
            language=language,
            level=level,
            title="Default",
            description="Various words and phrases",
            type=TopicType.VOCABULARY,
            private=True,
        )
        return await self.create(value, username)

    async def delete(self, language: Language, level: Level, id: UUID) -> None:
        # Delete native topics
        delete_ntopic_tasks = []
        for native_language in Language:
            delete_ntopic_tasks.append(self.native_topic_service.delete(language, level, native_language, id))
        await asyncio.gather(*delete_ntopic_tasks, return_exceptions=True)
        # Delete pages
        page_service = self.page_service_factory.create(language, level, id)
        delete_page_tasks = []
        async for page in page_service.get_all():
            delete_page_tasks.append(page_service.delete(page.id))
        await asyncio.gather(*delete_page_tasks, return_exceptions=True)
        # Delete topic itself
        storage = self._get_old_storage(language, level)
        await storage.delete(id)
        try:
            await self.new_storage.delete(id)
        except Exception as e:
            _log.error(f"Error deleting in new storage: {e}")
            pass
