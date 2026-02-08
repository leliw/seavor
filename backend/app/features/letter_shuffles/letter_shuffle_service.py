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

from .letter_shuffle_translation_service import LetterShuffleTranslationService


class LetterShuffleService:
    def __init__(self, factory: BaseAsyncFactory, audio_file_service: AudioFileService, target_language_code: str):
        self.factory = factory
        self.storage = factory.create_storage(
            f"target-languages/{target_language_code}/letter-shuffles", LetterShuffleSet
        )
        self.audio_file_service = audio_file_service
        self.target_language_code = target_language_code

    async def get_all(self):
        async for set in self.storage.get_all():
            yield LetterShuffleSetHeader(**set.model_dump())

    async def post(self, value_create: LetterShuffleSetCreate) -> LetterShuffleSet:
        if value_create.target_language_code != self.target_language_code:
            raise ValueError("Target language code mismatch")
        value = LetterShuffleSet.create(value_create)

        tasks = []
        for item in value.items:
            tasks.append(self.audio_file_service.generate_and_upload(item.target_phrase, self.target_language_code))
            tasks.append(
                self.audio_file_service.generate_and_upload(item.target_description, self.target_language_code)
            )

        results = await asyncio.gather(*tasks)

        idx = 0
        for item in value.items:
            item.target_phrase_audio_file_name = results[idx]
            item.target_description_audio_file_name = results[idx + 1]
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
        translation_patch = value_patch.to_translation_patch()
        translation_service = LetterShuffleTranslationService(
            self.factory, self.audio_file_service, self.target_language_code, uid
        )
        calls = [
            translation_service.patch(t.native_language_code, translation_patch)
            async for t in translation_service.get_all()
        ]
        await asyncio.gather(*calls)
        return value

    async def delete(self, uid: UUID) -> None:
        value = await self.storage.get(uid)
        for i in value.items:
            if i.target_phrase_audio_file_name:
                self.audio_file_service.delete(i.target_phrase_audio_file_name)
            if i.target_description_audio_file_name:
                self.audio_file_service.delete(i.target_description_audio_file_name)
        await self.storage.delete(uid)
