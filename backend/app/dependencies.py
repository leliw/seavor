import logging
from typing import Annotated

from app_config import AppConfig
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.concurrency import asynccontextmanager

from app_state import AppState

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
