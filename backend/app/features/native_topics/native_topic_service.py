import asyncio
import logging
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_topics.native_topic_model import NativeTopic

_log = logging.getLogger(__name__)


class NativeTopicService:
    def __init__(self, factory: BaseAsyncFactory, native_page_service_factory: NativePageServiceFactory):
        self.factory = factory
        self.native_page_service_factory = native_page_service_factory

    def _get_storage(self, native_language: Language) -> BaseAsyncCollectionStorage[NativeTopic]:
        return self.factory.get_collection("translations").get_collection(native_language, NativeTopic)

    async def get_list(
        self, language: Language, level: Level, native_language: Language, username: str | None = None
    ) -> AsyncGenerator[NativeTopic]:
        storage = self._get_storage(native_language)
        levels_filter = list(dict.fromkeys([level, Level.ALL]))
        async for topic in storage.where("language", "==", language).where("level", "in", levels_filter).get_all():
            if topic.private and topic.username != username:
                continue
            yield topic

    async def save(self, value: NativeTopic) -> None:
        storage = self._get_storage(value.native_language)
        await storage.save(value)

    async def create(self, value: NativeTopic) -> NativeTopic:
        storage = self._get_storage(value.native_language)
        await storage.create(value)
        return value

    async def get(self, native_language: Language, id: UUID) -> NativeTopic:
        storage = self._get_storage(native_language)
        return await storage.get(id)

    async def delete(self, native_language: Language, id: UUID) -> None:
        """Delete a native topic and all associated native pages.

        Args:
            language: The language of the topic.
            level: The level of the topic.
            native_language: The native language of the topic.
            id: The id of the topic.

        Returns:
            None
        """
        native_page_service = self.native_page_service_factory.create(native_language, id)
        delete_page_tasks = []
        async for page in native_page_service.get_all():
            delete_page_tasks.append(native_page_service.delete(page.id))
        await asyncio.gather(*delete_page_tasks, return_exceptions=True)
        storage = self._get_storage(native_language)
        await storage.delete(id)
