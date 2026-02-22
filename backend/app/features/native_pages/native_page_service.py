from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativePage
from features.pages.page_model import BasePage
from pydantic import TypeAdapter
from shared.audio_files.audio_file_service import AudioFileService

NativePageAdapter = TypeAdapter(NativePage)


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
        self.storage = factory.create_storage(
            f"target-languages/{target_language}/levels/{level}/native-languages/{native_language}/topics/{topic_id}/pages",
            NativePageAdapter,  # type: ignore
            "id",
        )
        self.storage.from_storage = lambda value: NativePageAdapter.validate_python(value)  # type: ignore

        self.audio_file_service = audio_file_service
        self.target_language_code = target_language

    async def get_all(self) -> AsyncGenerator[BasePage]:
        async for value in self.storage.get_all():
            yield BasePage(**value.model_dump())

    async def get(self, key: UUID) -> NativePage:
        return await self.storage.get(key)

    async def create(self, value: NativePage) -> NativePage:
        await self.storage.create(value)
        return value

    async def delete(self, key: UUID) -> None:
        await self.storage.delete(key)
