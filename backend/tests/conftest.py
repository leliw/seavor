import pytest
from config import ServerConfig
from dependencies import get_server_config, lifespan
from fastapi import FastAPI


@pytest.fixture
def config() -> ServerConfig:
    config = ServerConfig()
    return config


@pytest.fixture
def app(config) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.dependency_overrides[get_server_config] = lambda: config

    return app
