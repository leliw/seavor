from app_config import ClientConfig
from dependencies import AppConfigDep
from fastapi import APIRouter

router = APIRouter(tags=["Client config"])


@router.get("")
async def get_client_config(config: AppConfigDep) -> ClientConfig:
    return ClientConfig(**config.model_dump())
