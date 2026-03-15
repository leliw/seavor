from io import BytesIO
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from ampf.auth import AuthConfig, DefaultUser, TokenExp
from ampf.base import BaseAsyncFactory, BlobCreate
from ampf.testing import ApiTestClient
from app_config import AppConfig
from dependencies import get_tts_service, lifespan
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import TopicCreate, TopicType
from haintech.ai import BaseImageGenerator
from integrations.gtts.gtts_service import GttsService
from main import app as main_app


@pytest.fixture
def config(tmp_path) -> AppConfig:
    config = AppConfig(
        data_dir=str(tmp_path),
        gcp_root_storage=None,
        gcp_bucket_name=None,
        production=False,
        default_user=DefaultUser(username="test", password="test"),
        auth=AuthConfig(jwt_secret_key="test"),
    )
    return config


class TtsServiceMock(GttsService):
    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        return BytesIO(b"xxx")


class ImageGenServiceMock(BaseImageGenerator):
    async def generate_async(self, text: str) -> AsyncGenerator[BlobCreate]:
        yield BlobCreate.from_content(b"yyy", "image/png")


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


@pytest.fixture()
def topic_create() -> TopicCreate:
    return TopicCreate(
        language=Language.EN,
        level=Level.A1,
        title="Semi-modals",
        description="Semi-modals vs. pure modal verbs",
        type=TopicType.GRAMMAR,
    )


@pytest_asyncio.fixture
async def tokens(factory: BaseAsyncFactory, client: ApiTestClient):
    # Clear token_black_list
    await factory.create_compact_storage("token_black_list", TokenExp, "token").drop()
    # Login
    response = client.post(
        "/api/login",
        data={"username": "test", "password": "test"},
    )
    r = response.json()
    return r
