from typing import Optional

from ampf.auth import AuthConfig, DefaultUser
from core.feature_flags import FeatureFlags
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    feature_flags: FeatureFlags = FeatureFlags()
    version: str = __version__
    production: bool = True
    data_dir: str = "./data/"
    prompt_dir: str = "./app/prompts/"

    gcp_root_storage: Optional[str] = None
    gcp_bucket_name: Optional[str] = None

    auth: AuthConfig = AuthConfig(jwt_secret_key="")
    default_user: DefaultUser = DefaultUser(username="admin", password="")

    @field_validator("auth", mode="after")
    @classmethod
    def validate_jwt_secret_key(cls, v: AuthConfig) -> AuthConfig:
        if not v.jwt_secret_key:
            raise RuntimeError("Missing required configuration: AUTH__JWT_SECRET_KEY environment variable is not set.")
        return v

    @field_validator("default_user", mode="after")
    @classmethod
    def validate_default_user(cls, v: DefaultUser) -> DefaultUser:
        if not v.username:
            raise RuntimeError(
                "Missing required configuration: DEFAULT_USER__USERNAME environment variable is not set."
            )
        if not v.password:
            raise RuntimeError(
                "Missing required configuration: DEFAULT_USER__PASSWORD environment variable is not set."
            )
        return v


class ClientConfig(BaseModel):
    version: str
