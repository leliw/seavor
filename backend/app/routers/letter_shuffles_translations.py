from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import AppStateDep, AudioFileServiceDep
from fastapi import APIRouter, Depends
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
    LetterShuffleSetTranslationUpdate,
)
from features.letter_shuffles.letter_shuffle_translation_service import LetterShuffleTranslationService

router = APIRouter(tags=["Letter shuffles translations"])
ITEM_PATH = "/{code}"


def get_letter_shuffle_translation_service(
    app_state: AppStateDep, audio_file_service: AudioFileServiceDep, id: UUID
) -> LetterShuffleTranslationService:
    return LetterShuffleTranslationService(app_state.factory, audio_file_service, id)


LetterShuffleTranslationServiceDep = Annotated[
    LetterShuffleTranslationService, Depends(get_letter_shuffle_translation_service)
]


@router.get("", response_model=List[LetterShuffleSetTranslationHeader])
async def get_all(service: LetterShuffleTranslationServiceDep):
    return JsonStreamingResponse(service.get_all())


@router.post("")
async def post(
    service: LetterShuffleTranslationServiceDep, value_create: LetterShuffleSetTranslationCreate
) -> LetterShuffleSetTranslation:
    return await service.post(value_create)


@router.get(ITEM_PATH)
async def get(service: LetterShuffleTranslationServiceDep, code: str) -> LetterShuffleSetTranslation:
    return await service.get(code)


@router.put(ITEM_PATH)
async def put(
    service: LetterShuffleTranslationServiceDep, code: str, value_update: LetterShuffleSetTranslationUpdate
) -> LetterShuffleSetTranslation:
    return await service.put(code, value_update)


@router.delete(ITEM_PATH)
async def delete(service: LetterShuffleTranslationServiceDep, code: str):
    await service.delete(code)
