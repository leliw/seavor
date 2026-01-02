from io import BytesIO
import pytest
from ampf.base import BaseAsyncFactory
from ampf.testing import ApiTestClient
from app_config import AppConfig
from dependencies import lifespan, get_tts_service
from integrations.gtts.gtts_service import GttsService
from main import app as main_app


@pytest.fixture
def config(tmp_path) -> AppConfig:
    config = AppConfig(
        data_dir=str(tmp_path),
    )
    return config


class TtsServiceMock(GttsService):
    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        return BytesIO(b'xxx')


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
