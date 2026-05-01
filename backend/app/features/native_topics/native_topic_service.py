import asyncio
from typing import AsyncGenerator, Optional
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_topics.native_topic_model import NativeTopic


class NativeTopicService:
    def __init__(self, factory: BaseAsyncFactory, native_page_service_factory: NativePageServiceFactory):
        self.factory = factory
        self.native_page_service_factory = native_page_service_factory

    def _get_storage(
        self, language: Language, level: Level, native_language: Language
    ) -> BaseAsyncCollectionStorage[NativeTopic]:
        return (
            self.factory.get_collection("target-languages")
            .get_collection(language, "levels")
            .get_collection(level, "native-languages")
            .get_collection(native_language, NativeTopic)
        )

    async def get_list(
        self, language: Language, level: Level, native_language: Language, username: str | None = None
    ) -> AsyncGenerator[NativeTopic]:
        storage = self._get_storage(language, level, native_language)
        async for topic in storage.get_all():
            if topic.private and topic.username != username:
                continue
            yield topic

    async def save(self, value: NativeTopic, level: Optional[Level] = None) -> None:
        if not level and value.level:
            level = value.level
        elif not level:
            raise ValueError("Level is required")
        storage = self._get_storage(value.language, level, value.native_language)
        await storage.save(value)

    async def create(self, value: NativeTopic) -> NativeTopic:
        storage = self._get_storage(value.language, value.level, value.native_language)
        await storage.create(value)
        return value

    async def get(self, language: Language, level: Level, native_language: Language, id: UUID) -> NativeTopic:
        storage = self._get_storage(language, level, native_language)
        return await storage.get(id)

    async def delete(self, language: Language, level: Level, native_language: Language, id: UUID) -> None:
        """Delete a native topic and all associated native pages.
        
        Args:
            language: The language of the topic.
            level: The level of the topic.
            native_language: The native language of the topic.
            id: The id of the topic.

        Returns:
            None
        """
        native_page_service = self.native_page_service_factory.create(language, level, native_language, id)
        delete_page_tasks = []
        async for page in native_page_service.get_all():
            delete_page_tasks.append(native_page_service.delete(page.id))
        await asyncio.gather(*delete_page_tasks, return_exceptions=True)
        storage = self._get_storage(language, level, native_language)
        await storage.delete(id)
