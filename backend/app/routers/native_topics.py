from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import NativeTopicServiceDep
from fastapi import APIRouter
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic, NativeTopicCreate, NativeTopicHeader

router = APIRouter(tags=["Topic translations"])
ITEM_PATH = "/{topic_id}"


@router.get("", response_model=List[NativeTopicHeader])
async def get_all(service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language):
    return JsonStreamingResponse(service.get_list(target_language, level, native_language))


@router.post("")
async def post(service: NativeTopicServiceDep, value_create: NativeTopicCreate) -> NativeTopic:
    return await service.create(value_create)


@router.get(ITEM_PATH)
async def get(
    service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language, topic_id: UUID
) -> NativeTopic:
    return await service.get(target_language, level, native_language, topic_id)


# router.include_router(topics_pages.router, prefix=f"{ITEM_PATH}/pages")
