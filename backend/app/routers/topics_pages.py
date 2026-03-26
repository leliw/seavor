from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import PageServiceDep, RepetitionServiceDep, get_topic_for_user
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.pages.page_base_model import BasePage
from features.pages.page_model import (
    Page,
    PageCreate,
    PagePatch,
)
from features.repetitions.repetition_model import PageEvaluation, RepetitionCard

router = APIRouter(tags=["Topic pages"], dependencies=[Depends(get_topic_for_user)])
ITEM_PATH = "/{id}"


@router.post("")
async def post(service: PageServiceDep, value_create: PageCreate) -> Page:
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
async def patch(service: PageServiceDep, id: UUID, value_patch: PagePatch) -> Page:
    return await service.patch(id, value_patch)


@router.delete(ITEM_PATH)
async def delete(service: PageServiceDep, id: UUID) -> None:
    await service.delete(id)


@router.post(f"{ITEM_PATH}/evaluate")
async def evaluate(
    service: RepetitionServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
    id: UUID,
    page_evaluation: PageEvaluation,
) -> RepetitionCard:
    return await service.evaluate(target_language, level, topic_id, id, page_evaluation)
