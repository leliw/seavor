from io import BytesIO
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from ampf.auth import AuthConfig, DefaultUser, TokenExp, Tokens
from ampf.base import BaseAsyncFactory, BlobCreate
from ampf.testing import ApiTestClient
from app_config import AppConfig
from app_state import AppState
from core.users.user_model import User
from dependencies import get_tts_service, lifespan
from fastapi import FastAPI
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.pages.page_service import PageServiceFactory
from features.topics.topic_model import Topic, TopicCreate, TopicType
from haintech.ai import BaseImageGenerator
from haintech.ai.google_genai import GenAIImageGenerator, GoogleAIModel
from haintech.ai.prompts import PromptExecutor, PromptService
from features.topics.topic_service import TopicService
from integrations.gtts.gtts_service import GttsService
from main import app as main_app
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService
from shared.prompts.prompt_executor_image import PromptExecutorImage


@pytest.fixture
def config(tmp_path) -> AppConfig:
    config = AppConfig(
        data_dir=str(tmp_path),
        gcp_root_storage=None,
        gcp_bucket_name=None,
        production=False,
        default_user=DefaultUser(username="test", email="test@test.com", password="test"),
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
def app(config: AppConfig) -> FastAPI:
    app = main_app
    # Reconfigure the lifespan to use the test server config
    app.router.lifespan_context = lifespan(config)
    app.dependency_overrides[get_tts_service] = lambda: TtsServiceMock()
    return app


@pytest.fixture
def client(app: FastAPI) -> ApiTestClient:  # type: ignore
    with ApiTestClient(app) as client:
        yield client  # type: ignore

@pytest.fixture
def app_state(client: ApiTestClient) -> AppState:
    return client.app.state.app_state  # type: ignore



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
        private=False,
    )


@pytest.fixture
def topic_id(client: ApiTestClient, headers: dict[str, str], topic_create: TopicCreate) -> UUID:
    r = client.post_typed("/api/topics", 200, Topic, json=topic_create, headers=headers)
    return r.id


@pytest_asyncio.fixture
async def tokens(factory: BaseAsyncFactory, client: ApiTestClient) -> Tokens:
    # Clear token_black_list
    await factory.create_compact_storage("token_black_list", TokenExp, "token").drop()
    # Login
    return client.post_typed("/api/login", 200, Tokens, data={"username": "test", "password": "test"})


@pytest.fixture
def headers(tokens: Tokens) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def second_user_headers(client: ApiTestClient, headers: dict[str, str]) -> dict[str, str]:
    user = User(username="test2", email="tes2@test.com", password="test2")
    client.post("/api/users", 200, json=dict(user), headers=headers)
    tokens = client.post_typed("/api/login", 200, Tokens, data={"username": "test2", "password": "test2"})
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest.fixture
def topic_service(app_state: AppState) -> TopicService:
    return app_state.topic_service

@pytest.fixture
def page_service_factory(app_state: AppState) -> PageServiceFactory:
    return PageServiceFactory(app_state.factory, AudioFileService(app_state.factory, TtsServiceMock()))

@pytest.fixture
def native_page_service_factory(app_state: AppState) -> NativePageServiceFactory:
    return NativePageServiceFactory(app_state.factory, AudioFileService(app_state.factory, TtsServiceMock()))

@pytest.fixture
def image_service(app_state: AppState) -> ImageService:
    return ImageService(app_state.factory, None)


@pytest.fixture
def prompt_executor() -> PromptExecutor:
    return PromptExecutor(
        ai_model=GoogleAIModel(parameters={"temperature": 0.1}),
        prompt_service=PromptService("./app/prompts"),
    )

@pytest.fixture
def prompt_executor_image() -> PromptExecutorImage:
    return PromptExecutorImage(
        ai_model=GoogleAIModel(parameters={"temperature": 0.5}),
        image_generator=GenAIImageGenerator(model_name="gemini-3.1-flash-image-preview"),
        prompt_service=PromptService("./app/prompts"),
    )
