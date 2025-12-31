from uuid import UUID
from ampf.base import BaseAsyncFactory
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
    LetterShuffleSetCreate,
    LetterShuffleSetHeader,
    LetterShuffleSetPatch,
    LetterShuffleSetUpdate,
)


class LetterShuffleService:
    def __init__(self, factory: BaseAsyncFactory):
        self.storage = factory.create_storage("letter-shuffles", LetterShuffleSet)

    async def get_all(self):
        async for set in self.storage.get_all():
            yield LetterShuffleSetHeader(**set.model_dump())

    async def post(self, value_create: LetterShuffleSetCreate) -> LetterShuffleSet:
        value = LetterShuffleSet.create(value_create)
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
        await self.storage.delete(uid)
