from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import AppStateDep, AudioFileServiceDep
from fastapi import APIRouter, Depends
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
    LetterShuffleSetCreate,
    LetterShuffleSetHeader,
    LetterShuffleSetPatch,
    LetterShuffleSetUpdate,
)
from features.letter_shuffles.letter_shuffle_service import LetterShuffleService

router = APIRouter(tags=["Letter shuffles"])
ITEM_PATH = "/{id}"


def get_letter_shuffle_service(app_state: AppStateDep, audio_file_service: AudioFileServiceDep) -> LetterShuffleService:
    return LetterShuffleService(app_state.factory, audio_file_service)


LetterShuffleServiceDep = Annotated[LetterShuffleService, Depends(get_letter_shuffle_service)]


@router.get("", response_model=List[LetterShuffleSetHeader])
async def get_all(service: LetterShuffleServiceDep):
    return JsonStreamingResponse(service.get_all())


@router.post("")
async def post(service: LetterShuffleServiceDep, value_create: LetterShuffleSetCreate) -> LetterShuffleSet:
    return await service.post(value_create)


@router.get(ITEM_PATH)
async def get(service: LetterShuffleServiceDep, id: UUID) -> LetterShuffleSet:
    return await service.get(id)


@router.put(ITEM_PATH)
async def put(service: LetterShuffleServiceDep, id: UUID, value_update: LetterShuffleSetUpdate) -> LetterShuffleSet:
    return await service.put(id, value_update)


@router.patch(ITEM_PATH)
async def patch(service: LetterShuffleServiceDep, id: UUID, value_patch: LetterShuffleSetPatch) -> LetterShuffleSet:
    return await service.patch(id, value_patch)


@router.delete(ITEM_PATH)
async def delete(service: LetterShuffleServiceDep, id: UUID):
    await service.delete(id)
