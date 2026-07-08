import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory
from ampf.dependency import DependencyRegistry
from features.languages import Language
from features.native_pages.native_page_service import NativePageServiceFactory
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, DefinitionGuessPatch
from features.pages.page_base_model import PageHeader, PageType
from features.pages.page_model import (
    GapFillChoiceExercise,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExercisePut,
    InfoPage,
    InfoPageCreate,
    Page,
    PageCreate,
    PagePatch,
)
from pydantic import TypeAdapter
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService

PageAdapter = TypeAdapter(Page)

_log = logging.getLogger(__name__)


class PageServiceFactory:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService, image_service: ImageService):
        self.factory = factory
        self.audio_file_service = audio_file_service
        self.image_service = image_service

    def create(self, topic_id: UUID) -> "PageService":
        return PageService(
            factory=self.factory,
            audio_file_service=self.audio_file_service,
            image_service=self.image_service,
            topic_id=topic_id,
        )


class PageService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        audio_file_service: AudioFileService,
        image_service: ImageService,
        topic_id: UUID,
    ):
        self.new_storage: BaseAsyncCollectionStorage[Page] = factory.get_collection("topics").get_collection(
            topic_id, Page
        )
        self.audio_file_service = audio_file_service
        self.topic_id = topic_id
        self.image_service = image_service

        self.native_page_service_factory = DependencyRegistry.get(NativePageServiceFactory)

    async def get_all(self) -> AsyncGenerator[PageHeader]:
        async for value in self.new_storage.get_all():
            yield PageHeader(**value.model_dump())

    async def post(self, value: PageCreate) -> Page:
        match value.type:
            case PageType.GAP_FILL_CHOICE:
                page = await self.post_gap_fill_choice(value)
            case PageType.INFO:
                page = await self.post_info(value)
            case PageType.DEFINITION_GUESS:
                page = await self.post_definition_guess(value)
        await self.new_storage.create(page)
        return page

    async def post_gap_fill_choice(self, value_create: GapFillChoiceExerciseCreate) -> Page:
        texts_to_synthesize = value_create.get_texts_to_synthesize()
        audio_file_names = await asyncio.gather(
            *[
                self.audio_file_service.generate_and_upload(text=text, language=value_create.language)
                for text in texts_to_synthesize
            ]
        )
        text_to_audio = dict(zip(texts_to_synthesize, audio_file_names))
        value_create.set_audio_file_names(text_to_audio)
        return GapFillChoiceExercise.create(value_create)

    async def post_info(self, value_create: InfoPageCreate) -> Page:
        value = InfoPage.create(value_create)
        # texts_to_synthesize = []
        # texts_to_synthesize.append(value.title)
        # texts_to_synthesize.append(value.content)
        # audio_file_names = await asyncio.gather(
        #     *[
        #         self.audio_file_service.generate_and_upload(text=text, language=self.language_code)
        #         for text in texts_to_synthesize
        #     ]
        # )

        # audio_file_index = 0
        # value.title_audio_file_name = audio_file_names[audio_file_index]
        # audio_file_index += 1
        # value.definition_audio_file_name = audio_file_names[audio_file_index]
        return value

    async def post_definition_guess(self, value_create: DefinitionGuessCreate) -> Page:
        texts_to_synthesize = value_create.get_texts_to_synthesize()
        audio_file_names = await asyncio.gather(
            *[
                self.audio_file_service.generate_and_upload(text=text, language=value_create.language)
                for text in texts_to_synthesize
            ]
        )
        text_to_audio = dict(zip(texts_to_synthesize, audio_file_names))
        value_create.set_audio_file_names(text_to_audio)
        return DefinitionGuess.create(value_create)

    async def get(self, key: UUID) -> Page:
        return await self.new_storage.get(key)

    async def put(self, key: UUID, value: GapFillChoiceExercisePut) -> None:
        if key != value.id:
            raise ValueError("The key in the path must match the id in the request body.")

        existing_exercise = await self.new_storage.get(key)
        updated_exercise = existing_exercise.model_copy(update=value.model_dump(exclude_unset=True))
        updated_exercise.updated_at = datetime.now(timezone.utc)

        # For simplicity, audio files are not regenerated on PUT.
        # If audio regeneration is needed, a more complex logic similar to POST would be required.

        await self.new_storage.put(key, updated_exercise)

    async def patch(self, uid: UUID, value_patch: PagePatch) -> Page:
        value = await self.new_storage.get(uid)
        if value.type != value_patch.type:
            raise ValueError
        match value.type:
            case PageType.GAP_FILL_CHOICE:
                pass
            case PageType.DEFINITION_GUESS:
                pass
            case _:
                raise NotImplementedError
        value = await self.new_storage.patch(uid, value_patch)
        for native_language in Language:
            native_page_service = self.native_page_service_factory.create(
                target_language=value.language,
                level=value.level,
                native_language=native_language,
                topic_id=self.topic_id,
            )
            try:
                await native_page_service.patch(uid, value_patch.model_dump(exclude_unset=True))
            except Exception as e:
                _log.error(f"Error patching native page: {e}")
                pass
        return value

    async def delete(self, key: UUID) -> None:
        page = await self.new_storage.get(key)
        for file_name in page.get_audio_file_names():
            self.audio_file_service.delete(name=file_name)
        for image_name in page.get_image_file_names():
            self.image_service.delete(name=image_name)
        await self.new_storage.delete(key)

    async def add_image_name(self, page_id: UUID, image_name: str) -> Page | None:
        page = await self.get(page_id)
        if page.type != PageType.DEFINITION_GUESS:
            raise ValueError(f"Unsupported page type: {page.type}")
        if not page.image_names:
            page.image_names = []
        if image_name not in page.image_names:
            page.image_names.append(image_name)
            return await self.patch(page_id, DefinitionGuessPatch(image_names=page.image_names))
