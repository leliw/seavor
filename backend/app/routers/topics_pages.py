from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import AppStateDep, AudioFileServiceDep
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.pages.page_model import (
    BasePage,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExercisePatch,
    Page,
)
from features.pages.page_service import PageService

router = APIRouter(tags=["Topic pages"])
ITEM_PATH = "/{id}"


def get_page_service(
    app_state: AppStateDep,
    audio_file_service: AudioFileServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
):
    return PageService(app_state.factory, audio_file_service, target_language, level, topic_id)


PageServiceDep = Annotated[PageService, Depends(get_page_service)]


@router.post("")
async def post(service: PageServiceDep, value_create: GapFillChoiceExerciseCreate) -> Page:
    return await service.post(value_create)


@router.get("")
async def get_all(
    service: PageServiceDep,
) -> List[BasePage]:
    return JsonStreamingResponse(service.get_all())  # type: ignore


@router.get(ITEM_PATH)
async def get(service: PageServiceDep, id: UUID) -> Page:
    return await service.get(id)


@router.patch(ITEM_PATH)
async def patch(service: PageServiceDep, id: UUID, value_patch: GapFillChoiceExercisePatch) -> Page:
    return await service.patch(id, value_patch)


@router.delete(ITEM_PATH)
async def delete(service: PageServiceDep, id: UUID) -> None:
    await service.delete(id)
