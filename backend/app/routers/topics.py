from typing import List

from ampf.fastapi import JsonStreamingResponse
from dependencies import OptionalTokenPayloadDep, TokenPayloadDep, AuthorizedTopicDep, TopicServiceDep
from fastapi import APIRouter
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate
from routers import topics_pages

router = APIRouter(tags=["Topics"])
ITEM_PATH = "/{target_language}/{level}/{topic_id}"


@router.get("/{target_language}/{level}", response_model=List[Topic])
async def get_all(
    service: TopicServiceDep, target_language: Language, level: Level, token_payload: OptionalTokenPayloadDep
):
    username = token_payload.sub if token_payload else None
    return JsonStreamingResponse(service.get_list(target_language, level, username))


@router.post("")
async def post(service: TopicServiceDep, value_create: TopicCreate, token_payload: TokenPayloadDep) -> Topic:
    return await service.create(value_create, token_payload.sub)


@router.get(ITEM_PATH)
async def get(topic: AuthorizedTopicDep) -> Topic:
    return topic


router.include_router(topics_pages.router, prefix=f"{ITEM_PATH}/pages")
