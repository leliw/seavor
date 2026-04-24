from typing import Any, AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativePage, NativePageHeader
from shared.audio_files.audio_file_service import AudioFileService


class NativePageServiceFactory:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService):
        self.factory = factory
        self.audio_file_service = audio_file_service

    def create(
        self, target_language: Language, level: Level, native_language: Language, topic_id: UUID
    ) -> "NativePageService":
        return NativePageService(
            factory=self.factory,
            audio_file_service=self.audio_file_service,
            target_language=target_language,
            level=level,
            native_language=native_language,
            topic_id=topic_id,
        )


class NativePageService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        audio_file_service: AudioFileService,
        target_language: Language,
        level: Level,
        native_language: Language,
        topic_id: UUID,
    ):
        self.storage = (
            factory.get_collection("target-languages")
            .get_collection(target_language, "levels")
            .get_collection(level, "native-languages")
            .get_collection(native_language, "topics")
            .get_collection(topic_id, NativePage)
        )

        self.audio_file_service = audio_file_service
        self.target_language_code = target_language

    async def get_all(self) -> AsyncGenerator[NativePageHeader]:
        async for value in self.storage.get_all():
            yield NativePageHeader(**value.model_dump())

    async def get(self, key: UUID) -> NativePage:
        return await self.storage.get(key)

    async def create(self, value: NativePage) -> NativePage:
        await self.storage.create(value)
        return value

    async def patch(self, key: UUID, value_patch: dict[str, Any]) -> NativePage:
        return await self.storage.patch(key, value_patch)

    async def delete(self, key: UUID) -> None:
        await self.storage.delete(key)
