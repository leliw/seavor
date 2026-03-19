from typing import Annotated

from core.user_settings.user_settings_model import UserSettings, UserSettingsPatch
from core.user_settings.user_settings_service import UserSettingsService
from dependencies import AppStateDep, Authorize, TokenPayloadDep
from fastapi import APIRouter, Depends

router = APIRouter(tags=["User settings"], dependencies=[Depends(Authorize())])


def get_user_service(app_state: AppStateDep, token_payload: TokenPayloadDep) -> UserSettingsService:
    return UserSettingsService(app_state.user_storage.get_collection(token_payload.sub, "settings"))


UserSettingsServiceDep = Annotated[UserSettingsService, Depends(get_user_service)]


@router.get("")
async def get(user_settings_service: UserSettingsServiceDep) -> UserSettings:
    return await user_settings_service.get()


@router.patch("")
async def create(user_settings_service: UserSettingsServiceDep, value_patch: UserSettingsPatch) -> UserSettings:
    return await user_settings_service.patch(value_patch)
