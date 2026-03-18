from pydantic import BaseModel

USER_SETTINGS_ID = "settings"


class UserSettingsPatch(BaseModel):
    ui_language: str | None = None
    learning_language: str | None = None
    learning_level: str | None = None


class UserSettings(UserSettingsPatch):
    @property
    def id(self) -> str:
        return USER_SETTINGS_ID
