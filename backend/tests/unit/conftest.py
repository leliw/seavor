import pytest
from ampf.base import BaseAsyncFactory
from ampf.testing import ApiTestClient
from app_config import AppConfig
from dependencies import lifespan
from main import app as main_app


@pytest.fixture
def config(tmp_path) -> AppConfig:
    config = AppConfig(
        data_dir=str(tmp_path),
    )
    return config


@pytest.fixture
def client(config: AppConfig) -> ApiTestClient:  # type: ignore
    app = main_app
    # Reconfigure the lifespan to use the test server config
    app.router.lifespan_context = lifespan(config)
    with ApiTestClient(app) as client:
        yield client  # type: ignore


@pytest.fixture
def factory(client: ApiTestClient) -> BaseAsyncFactory:
    return client.app.state.app_state.factory  # type: ignore
