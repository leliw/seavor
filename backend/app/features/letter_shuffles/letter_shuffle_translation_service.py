import asyncio
from uuid import UUID

from ampf.base import BaseAsyncFactory
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
    LetterShuffleSetTranslationUpdate,
)
from features.levels import Level
from features.topics.topic_model import Topic
from features.topics.topic_service import TopicService
from shared.audio_files.audio_file_service import AudioFileService


class LetterShuffleTranslationService:
    def __init__(
        self, factory: BaseAsyncFactory, audio_file_service: AudioFileService, target_language_code: str, id: UUID
    ):
        self.storage = factory.create_storage(
            f"target-languages/{target_language_code}/letter-shuffles/{id}/",
            LetterShuffleSetTranslation,
            key="native_language_code",
        )
        self.audio_file_service = audio_file_service
        self.target_language_code = target_language_code
        self.id = id

    async def get_all(self):
        async for set in self.storage.where("id", "==", self.id).get_all():
            yield LetterShuffleSetTranslationHeader(**set.model_dump())

    async def post(
        self, topic_service: TopicService, value_create: LetterShuffleSetTranslationCreate
    ) -> LetterShuffleSetTranslation:
        value = LetterShuffleSetTranslation.create(value_create)

        tasks = []
        for item in value.items:
            tasks.append(self.audio_file_service.generate_and_upload(item.native_phrase, value.native_language_code))
            tasks.append(
                self.audio_file_service.generate_and_upload(item.native_description, value.native_language_code)
            )

        results = await asyncio.gather(*tasks)

        idx = 0
        for item in value.items:
            item.native_phrase_audio_file_name = results[idx]
            item.native_description_audio_file_name = results[idx + 1]
            idx += 2

        await self.storage.create(value)
        calls = [
            topic_service.save(Topic.from_letter_shuffle_translation(level, value))
            for level in value.levels or list(Level)
        ]
        await asyncio.gather(*calls)
        return value

    async def get(self, code: str) -> LetterShuffleSetTranslation:
        return await self.storage.get(code)

    async def put(self, code: str, value_update: LetterShuffleSetTranslationUpdate) -> LetterShuffleSetTranslation:
        value = await self.storage.get(code)
        value.update(value_update)
        await self.storage.put(code, value)
        return value

    async def delete(self, code: str) -> None:
        value = await self.storage.get(code)
        for i in value.items:
            if i.native_phrase_audio_file_name:
                self.audio_file_service.delete(i.native_phrase_audio_file_name)
            if i.native_description_audio_file_name:
                self.audio_file_service.delete(i.native_description_audio_file_name)
        await self.storage.delete(code)
