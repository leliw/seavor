from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import TopicServiceDep
from fastapi import APIRouter
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate
from routers import topics_pages

router = APIRouter(tags=["Topics"])
ITEM_PATH = "/{target_language}/{level}/{topic_id}"


@router.get("/{target_language}/{level}", response_model=List[Topic])
async def get_all(service: TopicServiceDep, target_language: Language, level: Level):
    return JsonStreamingResponse(service.get_list(target_language, level))


@router.post("")
async def post(service: TopicServiceDep, value_create: TopicCreate) -> Topic:
    return await service.create(value_create)


@router.get(ITEM_PATH)
async def get(service: TopicServiceDep, target_language: Language, level: Level, topic_id: UUID) -> Topic:
    return await service.get(target_language, level, topic_id)


router.include_router(topics_pages.router, prefix=f"{ITEM_PATH}/pages")
