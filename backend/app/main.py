import logging

from ampf.base import KeyNotExistsException
from app_config import AppConfig
from dependencies import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.localized_static_files import LocalizedStaticFiles
from log_config import setup_logging
from routers import (
    audio_files,
    config,
    images,
    letter_shuffles,
)
from version import __version__

_log = logging.getLogger(__name__)

load_dotenv()
setup_logging()
app_config = AppConfig()
app = FastAPI(
    title="Seavor",
    version=__version__,
    lifespan=lifespan(app_config),
    docs_url="/docs" if not app_config.production else None,
    redoc_url="/redoc" if not app_config.production else None,
    openapi_url="/openapi.json" if not app_config.production else None,
)


# Include the client config router
app.include_router(config.router, prefix="/api/config")
app.include_router(letter_shuffles.router, prefix="/api/target-languages/{target_language_code}/letter-shuffles")
app.include_router(audio_files.router, prefix="/api/audio-files")
app.include_router(images.router, prefix="/api/images")


@app.get("/api/ping")
async def ping() -> None:
    """Keep container alive."""


@app.get("/{full_path:path}")
async def catch_all(request: Request):
    return LocalizedStaticFiles("static/browser").get_static_page(request)


@app.exception_handler(KeyNotExistsException)
async def exception_not_found_callback(request: Request, exc: KeyNotExistsException):
    return JSONResponse({"detail": "Not found"}, status_code=404)
