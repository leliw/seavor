import pytest
from app_config import AppConfig
from dependencies import lifespan
from fastapi.testclient import TestClient
from main import app as main_app


@pytest.fixture
def config() -> AppConfig:
    config = AppConfig()
    return config


@pytest.fixture
def client(config: AppConfig) -> TestClient:  # type: ignore
    app = main_app
    # Reconfigure the lifespan to use the test server config
    app.router.lifespan_context = lifespan(config)
    with TestClient(app) as client:
        yield client  # type: ignore
