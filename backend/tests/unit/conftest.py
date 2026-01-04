from io import BytesIO
from typing import AsyncGenerator

import pytest
from ampf.base import BaseAsyncFactory, BlobCreate
from ampf.testing import ApiTestClient
from app_config import AppConfig
from dependencies import get_tts_service, lifespan
from integrations.gtts.gtts_service import GttsService
from integrations.image_gen.base_image_gen_service import BaseImageGenService
from main import app as main_app


@pytest.fixture
def config(tmp_path) -> AppConfig:
    config = AppConfig(
        data_dir=str(tmp_path),
    )
    return config


class TtsServiceMock(GttsService):
    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        return BytesIO(b"xxx")


class ImageGenServiceMock(BaseImageGenService):
    async def generate_async(self, text: str) -> AsyncGenerator[BlobCreate]:
        yield BlobCreate(content_type="image/png", data=b"yyy")


@pytest.fixture
def client(config: AppConfig) -> ApiTestClient:  # type: ignore
    app = main_app
    # Reconfigure the lifespan to use the test server config
    app.router.lifespan_context = lifespan(config)
    app.dependency_overrides[get_tts_service] = lambda: TtsServiceMock()
    with ApiTestClient(app) as client:
        yield client  # type: ignore


@pytest.fixture
def factory(client: ApiTestClient) -> BaseAsyncFactory:
    return client.app.state.app_state.factory  # type: ignore
