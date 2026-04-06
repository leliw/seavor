from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import (
    NativePageServiceDep,
    NativePageTranslatorDep,
    PageServiceDep,
    get_topic_for_user,
)
from fastapi import APIRouter, Depends
from features.languages import Language
from features.native_pages.native_page_model import NativePage, NativePageHeader

router = APIRouter(tags=["Topic pages translations"], dependencies=[Depends(get_topic_for_user)])
ITEM_PATH = "/{id}"


@router.post(ITEM_PATH)
async def post(
    page_service: PageServiceDep,
    translator: NativePageTranslatorDep,
    native_page_service: NativePageServiceDep,
    target_language: Language,
    native_language: Language,
    id: UUID,
) -> NativePage:
    page = await page_service.get(id)
    native_page = await translator.translate_page_to_native(target_language, native_language, page)
    return await native_page_service.create(native_page)


@router.get("")
async def get_all(
    service: NativePageServiceDep,
) -> List[NativePageHeader]:
    return JsonStreamingResponse(service.get_all())  # type: ignore


@router.get(ITEM_PATH)
async def get(service: NativePageServiceDep, id: UUID) -> NativePage:
    return await service.get(id)


@router.delete(ITEM_PATH)
async def delete(service: NativePageServiceDep, id: UUID) -> None:
    await service.delete(id)
