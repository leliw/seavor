from typing import Annotated

from ampf.auth import ExchangeCodePayload, GoogleOAuthConfig, GoogleOAuthService
from dependencies import AppConfigDep, FactoryDep, AuthServiceDep
from fastapi import APIRouter, Depends, Request, Query

router = APIRouter(tags=["Google authentication"])


def get_oauth(factory: FactoryDep, auth_service: AuthServiceDep, app_config: AppConfigDep) -> GoogleOAuthService:
    storage = factory.create_storage("google_oauth", ExchangeCodePayload, "exchange_code")
    return GoogleOAuthService(auth_service, storage, GoogleOAuthConfig(**app_config.model_dump()))


GoogleOAuthServiceDep = Annotated[GoogleOAuthService, Depends(get_oauth)]


@router.get("/login")
async def login(service: GoogleOAuthServiceDep, request: Request, base_url: str | None = None, code: Annotated[str | None, Query(alias="exchange-code")] = None):
    if code:
        return await service.authorize_with_code(code)
    else:
        return await service.authorize_redirect(request, base_url)


@router.get("/callback")
async def auth_callback(service: GoogleOAuthServiceDep, request: Request):
    return await service.auth_callback(request)
