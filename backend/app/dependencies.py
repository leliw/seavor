import logging
from typing import Annotated
from uuid import UUID

from app_config import AppConfig
from app_state import AppState
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_service import NativeTopicService
from features.pages.page_service import PageService
from features.topics.topic_service import TopicService
from haintech.ai import BaseAIModel
from integrations.gtts.gtts_service import GttsService
from integrations.image_gen.base_image_gen_service import BaseImageGenService
from integrations.image_gen.openai_image_gen_service import OpenAIImageGenService
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService
from shared.prompts.prompt_service import PromptService

load_dotenv()

_log = logging.getLogger(__name__)


def lifespan(config: AppConfig = AppConfig()):
    app_state = AppState.create(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.app_state = app_state
        yield

    return lifespan


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state


AppStateDep = Annotated[AppState, Depends(get_app_state)]


def get_app_config(app_state: AppStateDep) -> AppConfig:
    return app_state.config


ConfigDep = Annotated[AppConfig, Depends(get_app_config)]


def get_prompt_service(app_state: AppStateDep) -> PromptService:
    return app_state.prompt_service


PromptServiceDep = Annotated[PromptService, Depends(get_prompt_service)]


def get_tts_service() -> GttsService:
    return GttsService()


GttsServiceDep = Annotated[GttsService, Depends(get_tts_service)]


def get_audio_file_service(app_state: AppStateDep, tts_service: GttsServiceDep) -> AudioFileService:
    return AudioFileService(app_state.factory, tts_service)


AudioFileServiceDep = Annotated[AudioFileService, Depends(get_audio_file_service)]


def get_image_gen_service() -> BaseImageGenService | None:
    try:
        return OpenAIImageGenService()
    except Exception:
        return None


ImageGenServiceDep = Annotated[BaseImageGenService | None, Depends(get_image_gen_service)]


def get_image_service(app_state: AppStateDep, image_gen_service: ImageGenServiceDep) -> ImageService:
    return ImageService(app_state.factory, image_gen_service)


ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]


def not_production(app_state: AppStateDep) -> bool:
    if app_state.config.production:
        raise HTTPException(status_code=404, detail="Not found")
    return not app_state.config.production


def get_topic_service(app_state: AppStateDep) -> TopicService:
    return TopicService(app_state.factory)


TopicServiceDep = Annotated[TopicService, Depends(get_topic_service)]


def get_topic_translation_service(app_state: AppStateDep) -> NativeTopicService:
    return NativeTopicService(app_state.factory)


NativeTopicServiceDep = Annotated[NativeTopicService, Depends(get_topic_translation_service)]


def get_translator_ai_model(app_state: AppStateDep):
    from haintech.ai.google_generativeai import GoogleAIModel

    return GoogleAIModel(model_name="gemini-2.5-flash-lite", parameters={"temperature": 0.0})


TranslatorAIModelDep = Annotated[BaseAIModel, Depends(get_translator_ai_model)]


def get_page_service(
    app_state: AppStateDep,
    audio_file_service: AudioFileServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
):
    return PageService(app_state.factory, audio_file_service, target_language, level, topic_id)


PageServiceDep = Annotated[PageService, Depends(get_page_service)]
