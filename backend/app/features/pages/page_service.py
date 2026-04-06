import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory
from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate
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

PageAdapter = TypeAdapter(Page)


class PageServiceFactory:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService):
        self.factory = factory
        self.audio_file_service = audio_file_service

    def create(self, language: Language, level: Level, topic_id: UUID) -> "PageService":
        return PageService(
            factory=self.factory,
            audio_file_service=self.audio_file_service,
            language=language,
            level=level,
            topic_id=topic_id,
        )


class PageService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        audio_file_service: AudioFileService,
        language: Language,
        level: Level,
        topic_id: UUID,
    ):
        self.storage = factory.create_storage(
            f"target-languages/{language}/levels/{level}/topics/{topic_id}/pages",
            Page,  # type: ignore
            "id",
        )
        # self.storage.from_storage = lambda value: PageAdapter.validate_python(value)  # type: ignore

        self.audio_file_service = audio_file_service
        self.language_code = language

    async def get_all(self) -> AsyncGenerator[PageHeader]:
        async for value in self.storage.get_all():
            yield PageHeader(**value.model_dump())

    async def post(self, value: PageCreate) -> Page:
        match value.type:
            case PageType.GAP_FILL_CHOICE:
                return await self.post_gap_fill_choice(value)
            case PageType.INFO:
                return await self.post_info(value)
            case PageType.DEFINITION_GUESS:
                return await self.post_definition_guess(value)

    async def post_gap_fill_choice(self, value_create: GapFillChoiceExerciseCreate) -> Page:
        texts_to_synthesize = value_create.get_texts_to_synthesize()
        audio_file_names = await asyncio.gather(
            *[
                self.audio_file_service.generate_and_upload(text=text, language=self.language_code)
                for text in texts_to_synthesize
            ]
        )
        text_to_audio = dict(zip(texts_to_synthesize, audio_file_names))
        value_create.set_audio_file_names(text_to_audio)

        value = GapFillChoiceExercise.create(value_create)
        await self.storage.create(value)
        return value

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
        await self.storage.create(value)
        return value

    async def post_definition_guess(self, value_create: DefinitionGuessCreate) -> Page:
        texts_to_synthesize = value_create.get_texts_to_synthesize()
        audio_file_names = await asyncio.gather(
            *[
                self.audio_file_service.generate_and_upload(text=text, language=self.language_code)
                for text in texts_to_synthesize
            ]
        )
        text_to_audio = dict(zip(texts_to_synthesize, audio_file_names))
        value_create.set_audio_file_names(text_to_audio)

        value = DefinitionGuess.create(value_create)
        await self.storage.create(value)
        return value

    async def get(self, key: UUID) -> Page:
        return await self.storage.get(key)

    async def put(self, key: UUID, value: GapFillChoiceExercisePut) -> None:
        if key != value.id:
            raise ValueError("The key in the path must match the id in the request body.")

        existing_exercise = await self.storage.get(key)
        updated_exercise = existing_exercise.model_copy(update=value.model_dump(exclude_unset=True))
        updated_exercise.updated_at = datetime.now(timezone.utc)

        # For simplicity, audio files are not regenerated on PUT.
        # If audio regeneration is needed, a more complex logic similar to POST would be required.

        await self.storage.put(key, updated_exercise)

    async def patch(self, uid: UUID, value_patch: PagePatch) -> Page:
        value = await self.storage.get(uid)
        value.patch(value_patch)
        await self.storage.put(uid, value)
        return value

    async def delete(self, key: UUID) -> None:
        exercise_to_delete = await self.storage.get(key)
        match exercise_to_delete.type:
            case PageType.GAP_FILL_CHOICE:
                audio_files_to_delete = []
                if exercise_to_delete.sentence_audio_file_name:
                    audio_files_to_delete.append(exercise_to_delete.sentence_audio_file_name)
                if exercise_to_delete.explanation_audio_file_name:
                    audio_files_to_delete.append(exercise_to_delete.explanation_audio_file_name)
                if exercise_to_delete.hint_audio_file_name:
                    audio_files_to_delete.append(exercise_to_delete.hint_audio_file_name)
                if exercise_to_delete.distractors_explanation_audio_file_name:
                    for distractor in exercise_to_delete.distractors_explanation_audio_file_name.items():
                        if distractor[1]:
                            audio_files_to_delete.append(distractor[1])

                for file_name in audio_files_to_delete:
                    self.audio_file_service.delete(name=file_name)
                # await asyncio.gather(
                #     *[self.audio_file_service.delete(name=file_name) for file_name in audio_files_to_delete]
                # )
        await self.storage.delete(key)
