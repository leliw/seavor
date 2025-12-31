from ampf.base import KeyNotExistsException
from ampf.fastapi import StaticFileResponse
from dependencies import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from log_config import setup_logging
from routers import (
    config,
    letter_shuffles,
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
app.include_router(letter_shuffles.router, prefix="/api/letter-shuffles")


@app.get("/api/ping")
async def ping() -> None:
    """Keep container alive."""


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """
    Catch-all route to serve static files for the Angular frontend.

    This route should be placed at the end of all other API routes.
    It checks if the path starts with "api/" to distinguish between
    frontend routes and backend API routes.

    Args:
        full_path: The full path requested by the client.

    Returns:
        A StaticFileResponse for frontend assets or raises HTTPException for API paths not found.
    """
    if not full_path.startswith("api/"):
        return StaticFileResponse("static/browser", full_path)
    else:
        raise HTTPException(status_code=404, detail="Not found")


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
