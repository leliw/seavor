from ampf.base import KeyNotExistsException
from dependencies import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from log_config import setup_logging
from routers import (
    config,
)
from version import __version__

load_dotenv()
setup_logging()
app = FastAPI(
    title="Seavor",
    version=__version__,
    lifespan=lifespan(),
)


# Include the client config router
app.include_router(config.router, prefix="/api/config")


@app.exception_handler(KeyNotExistsException)
async def exception_not_found_callback(request: Request, exc: KeyNotExistsException):
    """
    Exception handler for KeyNotExistsException.

    Returns a 404 Not Found JSON response when a requested resource (e.g., chat session)
    does not exist.

    Args:
        request: The incoming FastAPI request.
        exc: The KeyNotExistsException that was raised.
    """
    return JSONResponse({"detail": "Not found"}, status_code=404)
