import logging
from typing import Annotated

from app_config import AppConfig
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager

load_dotenv()

_log = logging.getLogger(__name__)


def lifespan(config: AppConfig = AppConfig()):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.config = config
        yield

    return lifespan


def get_app(request: Request) -> FastAPI:
    return request.app


AppDep = Annotated[FastAPI, Depends(get_app)]


def get_server_config(app: AppDep) -> AppConfig:
    return app.state.config


ConfigDep = Annotated[AppConfig, Depends(get_server_config)]
