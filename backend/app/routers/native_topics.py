from typing import Annotated, List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import NativeTopicServiceDep, TopicServiceDep, TranslatorAIModelDep
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic, NativeTopicHeader
from features.native_topics.native_topic_translator import NativeTopicTranslator

router = APIRouter(tags=["Topic translations"])
ITEM_PATH = "/{topic_id}"


def get_native_topic_translator(
    translator_ai_model: TranslatorAIModelDep, topic_service: TopicServiceDep
) -> NativeTopicTranslator:
    return NativeTopicTranslator(translator_ai_model, topic_service)


NativeTopicTranslatorDep = Annotated[NativeTopicTranslator, Depends(get_native_topic_translator)]


@router.get("", response_model=List[NativeTopicHeader])
async def get_all(service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language):
    return JsonStreamingResponse(service.get_list(target_language, level, native_language))


@router.post(ITEM_PATH)
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


@router.get(ITEM_PATH)
async def get(
    service: NativeTopicServiceDep, target_language: Language, level: Level, native_language: Language, topic_id: UUID
) -> NativeTopic:
    return await service.get(target_language, level, native_language, topic_id)


# router.include_router(topics_pages.router, prefix=f"{ITEM_PATH}/pages")
