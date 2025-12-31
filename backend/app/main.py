from dependencies import lifespan
from dotenv import load_dotenv
from fastapi import FastAPI
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
