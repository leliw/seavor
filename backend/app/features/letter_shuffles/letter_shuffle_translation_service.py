import asyncio
from uuid import UUID
from ampf.base import BaseAsyncFactory
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
    LetterShuffleSetTranslationUpdate,
)
from shared.audio_files.audio_file_service import AudioFileService


class LetterShuffleTranslationService:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService, id: UUID):
        self.storage = factory.create_storage(
            "letter-shuffles-translations", LetterShuffleSetTranslation, key=lambda x: f"{x.id}-{x.language}"
        )
        self.audio_file_service = audio_file_service
        self.id = id

    async def get_all(self):
        async for set in self.storage.where("id", "==", self.id).get_all():
            yield LetterShuffleSetTranslationHeader(**set.model_dump())

    async def post(self, value_create: LetterShuffleSetTranslationCreate) -> LetterShuffleSetTranslation:
        value = LetterShuffleSetTranslation.create(value_create)

        tasks = []
        for item in value.items:
            tasks.append(self.audio_file_service.generate_and_upload(item.question, value.language))
            tasks.append(self.audio_file_service.generate_and_upload(item.description, value.language))

        results = await asyncio.gather(*tasks)

        idx = 0
        for item in value.items:
            item.question_audio_file_name = results[idx]
            item.description_audio_file_name = results[idx + 1]
            idx += 2

        await self.storage.create(value)
        return value

    async def get(self, code: str) -> LetterShuffleSetTranslation:
        return await self.storage.get(f"{self.id}-{code}")

    async def put(self, code: str, value_update: LetterShuffleSetTranslationUpdate) -> LetterShuffleSetTranslation:
        value = await self.storage.get(f"{self.id}-{code}")
        value.update(value_update)
        await self.storage.put(f"{self.id}-{code}", value)
        return value

    async def delete(self, code: str) -> None:
        value = await self.storage.get(f"{self.id}-{code}")
        for i in value.items:
            if i.question_audio_file_name:
                self.audio_file_service.delete(i.question_audio_file_name)
            if i.description_audio_file_name:
                self.audio_file_service.delete(i.description_audio_file_name)
        await self.storage.delete(f"{self.id}-{code}")
