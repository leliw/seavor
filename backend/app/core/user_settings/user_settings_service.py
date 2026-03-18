from ampf.base import BaseAsyncCollectionStorage, KeyNotExistsException

from .user_settings_model import USER_SETTINGS_ID, UserSettings, UserSettingsPatch


class UserSettingsService:
    """User settings service implementation"""

    def __init__(self, storage: BaseAsyncCollectionStorage[UserSettings]) -> None:
        self.storage = storage.decorated
        self._key = USER_SETTINGS_ID

    async def get(self) -> UserSettings:
        try:
            return await self.storage.get(self._key)
        except KeyNotExistsException:
            value = UserSettings()
            await self.storage.put(self._key, value)
            return value

    async def patch(self, value_patch: UserSettingsPatch) -> UserSettings:
        try:
            return await self.storage.patch(self._key, value_patch)
        except KeyNotExistsException:
            value = UserSettings()
            await self.storage.put(self._key, value)
            return await self.storage.patch(self._key, value_patch)
