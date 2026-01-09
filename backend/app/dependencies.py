import logging
from typing import Annotated

from app_config import AppConfig
from app_state import AppState
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from integrations.gtts.gtts_service import GttsService
from integrations.image_gen.base_image_gen_service import BaseImageGenService
from integrations.image_gen.openai_image_gen_service import OpenAIImageGenService
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService

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
