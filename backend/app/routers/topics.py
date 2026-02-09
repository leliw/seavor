from typing import List

from ampf.fastapi import JsonStreamingResponse
from dependencies import TopicServiceDep
from fastapi import APIRouter
from features.topics.topic_model import Topic

router = APIRouter(tags=["Topics"])


@router.get("/{target_language_code}/{level}/{native_language_code}", response_model=List[Topic])
async def get_all(service: TopicServiceDep, target_language_code: str, level: str, native_language_code: str):
    return JsonStreamingResponse(service.get_list(target_language_code, level, native_language_code))
