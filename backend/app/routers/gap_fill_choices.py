from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import AppStateDep, AudioFileServiceDep
from fastapi import APIRouter, Depends
from features.gap_fill_choice.gap_fill_choice_model import (
    GapFillChoiceExercise,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExerciseHeader,
    GapFillChoiceExercisePatch,
)
from features.gap_fill_choice.gap_fill_choice_service import GapFillChoiceService
from features.languages import Language
from features.levels import Level

router = APIRouter(tags=["Gap Fill Choice Exercises"])
ITEM_PATH = "/{id}"


def get_gap_fill_choice_service(
    app_state: AppStateDep, audio_file_service: AudioFileServiceDep, target_language: Language, level: Level, topic_id: UUID
):
    return GapFillChoiceService(app_state.factory, audio_file_service, target_language, level, topic_id)


GapFillChoiceServiceDep = Annotated[GapFillChoiceService, Depends(get_gap_fill_choice_service)]


@router.post("")
async def post(service: GapFillChoiceServiceDep, value_create: GapFillChoiceExerciseCreate) -> GapFillChoiceExercise:
    return await service.post(value_create)


@router.get("")
async def get_all(
    service: GapFillChoiceServiceDep,
) -> List[GapFillChoiceExerciseHeader]:
    return JsonStreamingResponse(service.get_all())  # type: ignore


@router.get(ITEM_PATH)
async def get(service: GapFillChoiceServiceDep, id: UUID) -> GapFillChoiceExercise:
    return await service.get(id)


@router.patch(ITEM_PATH)
async def patch(
    service: GapFillChoiceServiceDep, id: UUID, value_patch: GapFillChoiceExercisePatch
) -> GapFillChoiceExercise:
    return await service.patch(id, value_patch)


@router.delete(ITEM_PATH)
async def delete(service: GapFillChoiceServiceDep, id: UUID) -> None:
    await service.delete(id)
