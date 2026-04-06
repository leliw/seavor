from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import NativeTopicServiceDep, NativeTopicTranslatorDep, OptionalTokenPayloadDep, get_topic_for_user
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic, NativeTopicHeader
from routers import native_topics_pages

router = APIRouter(tags=["Topic translations"])
ITEM_PATH = "/{topic_id}"



@router.get("", response_model=List[NativeTopicHeader])
async def get_all(service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language, token_payload: OptionalTokenPayloadDep):
    username = token_payload.sub if token_payload else None
    return JsonStreamingResponse(service.get_list(target_language, level, native_language, username))

@router.post(ITEM_PATH, dependencies=[Depends(get_topic_for_user)])
async def translate_topic(
    translator: NativeTopicTranslatorDep,
    native_topic_service: NativeTopicServiceDep,
    target_language: Language,
    level: Level,
    native_language: Language,
    topic_id: UUID,
) -> NativeTopic:
    native_topic = await translator.translate_topic_to_native(target_language, level, native_language, topic_id)
    return await native_topic_service.create(native_topic)


@router.get(ITEM_PATH, dependencies=[Depends(get_topic_for_user)])
async def get(
    service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language, topic_id: UUID) -> NativeTopic:
    return await service.get(target_language, level, native_language, topic_id)


router.include_router(native_topics_pages.router, prefix=f"{ITEM_PATH}/pages")
