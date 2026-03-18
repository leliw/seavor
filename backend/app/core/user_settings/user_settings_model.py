from pydantic import BaseModel

USER_SETTINGS_ID = "settings"


class UserSettingsPatch(BaseModel):
    native_language: str | None


class UserSettings(BaseModel):
    native_language: str = "en"

    @property
    def id(self) -> str:
        return USER_SETTINGS_ID
