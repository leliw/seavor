from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = __version__


class ClientConfig(BaseModel):
    version: str
