from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import (
    AppStateDep,
    AudioFileServiceDep,
    PageServiceDep,
    PromptServiceDep,
    TranslatorAIModelDep,
    get_topic_for_user,
)
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativePage, NativePageHeader
from features.native_pages.native_page_service import NativePageService
from features.native_pages.native_page_translator import NativePageTranslator

router = APIRouter(tags=["Topic pages translations"], dependencies=[Depends(get_topic_for_user)])
ITEM_PATH = "/{id}"


def get_native_page_service(
    app_state: AppStateDep,
    audio_file_service: AudioFileServiceDep,
    target_language: Language,
    level: Level,
    native_language: Language,
    topic_id: UUID,
):
    return NativePageService(app_state.factory, audio_file_service, target_language, level, native_language, topic_id)


NativePageServiceDep = Annotated[NativePageService, Depends(get_native_page_service)]


def get_native_topic_page_translator(
    translator_ai_model: TranslatorAIModelDep, prompt_service: PromptServiceDep, page_service: PageServiceDep
) -> NativePageTranslator:
    return NativePageTranslator(translator_ai_model, prompt_service, page_service)


NativePageTranslatorDep = Annotated[NativePageTranslator, Depends(get_native_topic_page_translator)]


@router.post(ITEM_PATH)
async def post(
    translator: NativePageTranslatorDep,
    service: NativePageServiceDep,
    target_language: Language,
    native_language: Language,
    id: UUID,
) -> NativePage:
    native_page = await translator.translate_page_to_native(target_language, native_language, id)
    return await service.create(native_page)


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
