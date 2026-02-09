from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import AppStateDep, AudioFileServiceDep, TopicServiceDep, not_production
from fastapi import APIRouter, Depends
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
    LetterShuffleSetTranslationPatch,
    LetterShuffleSetTranslationUpdate,
)
from features.letter_shuffles.letter_shuffle_translation_service import LetterShuffleTranslationService

router = APIRouter(tags=["Letter shuffles translations"])
ITEM_PATH = "/{native_language_code}"


def get_letter_shuffle_translation_service(
    app_state: AppStateDep, audio_file_service: AudioFileServiceDep, target_language_code: str, id: UUID
) -> LetterShuffleTranslationService:
    return LetterShuffleTranslationService(app_state.factory, audio_file_service, target_language_code, id)


LetterShuffleTranslationServiceDep = Annotated[
    LetterShuffleTranslationService, Depends(get_letter_shuffle_translation_service)
]


@router.get("", response_model=List[LetterShuffleSetTranslationHeader])
async def get_all(service: LetterShuffleTranslationServiceDep):
    return JsonStreamingResponse(service.get_all())


@router.post("", dependencies=[Depends(not_production)])
async def post(
    service: LetterShuffleTranslationServiceDep, topic_service: TopicServiceDep, value_create: LetterShuffleSetTranslationCreate
) -> LetterShuffleSetTranslation:
    return await service.post(topic_service, value_create)


@router.get(ITEM_PATH)
async def get(service: LetterShuffleTranslationServiceDep, native_language_code: str) -> LetterShuffleSetTranslation:
    return await service.get(native_language_code)


@router.put(ITEM_PATH, dependencies=[Depends(not_production)])
async def put(
    service: LetterShuffleTranslationServiceDep,
    native_language_code: str,
    value_update: LetterShuffleSetTranslationUpdate,
) -> LetterShuffleSetTranslation:
    return await service.put(native_language_code, value_update)

@router.patch(ITEM_PATH, dependencies=[Depends(not_production)])
async def patch(
    service: LetterShuffleTranslationServiceDep,
    native_language_code: str,
    value_patch: LetterShuffleSetTranslationPatch,
) -> LetterShuffleSetTranslation:
    return await service.patch(native_language_code, value_patch)

@router.delete(ITEM_PATH, dependencies=[Depends(not_production)])
async def delete(service: LetterShuffleTranslationServiceDep, native_language_code: str):
    await service.delete(native_language_code)
