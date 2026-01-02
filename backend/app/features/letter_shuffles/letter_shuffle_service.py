import asyncio
from uuid import UUID
from ampf.base import BaseAsyncFactory
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
    LetterShuffleSetCreate,
    LetterShuffleSetHeader,
    LetterShuffleSetPatch,
    LetterShuffleSetUpdate,
)
from shared.audio_files.audio_file_service import AudioFileService


class LetterShuffleService:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService):
        self.storage = factory.create_storage("letter-shuffles", LetterShuffleSet)
        self.audio_file_service = audio_file_service


    async def get_all(self):
        async for set in self.storage.get_all():
            yield LetterShuffleSetHeader(**set.model_dump())

    async def post(self, value_create: LetterShuffleSetCreate) -> LetterShuffleSet:
        value = LetterShuffleSet.create(value_create)

        tasks = []
        for item in value.items:
            tasks.append(self.audio_file_service.generate_and_upload(item.question, "en"))
            tasks.append(self.audio_file_service.generate_and_upload(item.description, "en"))
        
        results = await asyncio.gather(*tasks)
        
        idx = 0
        for item in value.items:
            item.question_audio_file_name = results[idx]
            item.description_audio_file_name = results[idx + 1]
            idx += 2

        await self.storage.create(value)
        return value

    async def get(self, uid: UUID) -> LetterShuffleSet:
        return await self.storage.get(uid)

    async def put(self, uid: UUID, value_update: LetterShuffleSetUpdate) -> LetterShuffleSet:
        value = await self.storage.get(uid)
        value.update(value_update)
        await self.storage.put(uid, value)
        return value

    async def patch(self, uid: UUID, value_patch: LetterShuffleSetPatch) -> LetterShuffleSet:
        value = await self.storage.get(uid)
        value.patch(value_patch)
        await self.storage.put(uid, value)
        return value

    async def delete(self, uid: UUID) -> None:
        value = await self.storage.get(uid)
        for i in value.items:
            if i.question_audio_file_name:
                self.audio_file_service.delete(i.question_audio_file_name)
            if i.description_audio_file_name:
                self.audio_file_service.delete(i.description_audio_file_name)
        await self.storage.delete(uid)
