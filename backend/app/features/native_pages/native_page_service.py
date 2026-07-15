import logging
from typing import Any, AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory, KeyNotExistsException
from features.languages import Language
from features.native_pages.native_page_model import NativePage, NativePageHeader
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService

_log = logging.getLogger(__name__)


class NativePageServiceFactory:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService, image_service: ImageService):
        self.factory = factory
        self.audio_file_service = audio_file_service
        self.image_service = image_service

    def create(self, native_language: Language, topic_id: UUID) -> "NativePageService":
        return NativePageService(
            factory=self.factory,
            audio_file_service=self.audio_file_service,
            image_service=self.image_service,
            native_language=native_language,
            topic_id=topic_id,
        )


class NativePageService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        audio_file_service: AudioFileService,
        image_service: ImageService,
        native_language: Language,
        topic_id: UUID,
    ):
        self.storage = (
            factory.get_collection("translations")
            .get_collection(native_language, "topics")
            .get_collection(topic_id, NativePage)
        )
        self.audio_file_service = audio_file_service
        self.image_service = image_service

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
        """Delete a page and all associated audio files and images.

        Args:
            key: The key of the page to delete.

        Returns:
            None
        """
        page = await self.storage.get(key)
        for audio_file_name in page.get_audio_file_names():
            try:
                await self.audio_file_service.delete(audio_file_name)
            except KeyNotExistsException:
                pass
        for image_file_name in page.get_image_file_names():
            try:
                await self.image_service.delete(image_file_name)
            except KeyNotExistsException:
                pass
        await self.storage.delete(key)
