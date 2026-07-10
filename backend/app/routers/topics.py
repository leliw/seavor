from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from core.roles import Role
from dependencies import Authorize, AuthorizedTopicDep, OptionalTokenPayloadDep, TokenPayloadDep, TopicServiceDep
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic, TopicCreate
from routers import topics_pages

router = APIRouter(tags=["Topics"])
ITEM_PATH = "/{topic_id}"


@router.get("", response_model=List[Topic])
async def get_all(service: TopicServiceDep, language: Language, level: Level, token_payload: OptionalTokenPayloadDep):
    username = token_payload.sub if token_payload else None
    return JsonStreamingResponse(service.get_list(language, level, username))


@router.post("")
async def post(service: TopicServiceDep, value_create: TopicCreate, token_payload: TokenPayloadDep) -> Topic:
    return await service.create(value_create, token_payload.sub)


@router.get(ITEM_PATH)
async def get(topic: AuthorizedTopicDep) -> Topic:
    return topic


@router.delete(ITEM_PATH, dependencies=[Depends(Authorize(Role.ADMIN))], status_code=204)
async def delete(service: TopicServiceDep, topic_id: UUID) -> None:
    await service.delete(topic_id)


router.include_router(topics_pages.router, prefix=f"{ITEM_PATH}/pages")
