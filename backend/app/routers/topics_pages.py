from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import PageServiceDep
from fastapi import APIRouter
from features.pages.page_base_model import BasePage
from features.pages.page_model import (
    Page,
    PageCreate,
    PagePatch,
)

router = APIRouter(tags=["Topic pages"])
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
