from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import TopicServiceDep
from fastapi import APIRouter
from features.topics.topic_model import Topic, TopicCreate

router = APIRouter(tags=["Topics"])
ITEM_PATH = "/{target_language_code}/{level}/{id}"

@router.get("/{target_language_code}/{level}/native-languages/{native_language_code}", response_model=List[Topic])
async def get_all(service: TopicServiceDep, target_language_code: str, level: str, native_language_code: str):
    return JsonStreamingResponse(service.get_list(target_language_code, level, native_language_code))

@router.post("")
async def post(service: TopicServiceDep, value_create: TopicCreate) -> Topic:
    return await service.create(value_create)

@router.get(ITEM_PATH)
async def get(service: TopicServiceDep, target_language_code: str, level: str, id: UUID) -> Topic:
    return await service.get(target_language_code, level, id)