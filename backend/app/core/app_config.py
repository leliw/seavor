from functools import cached_property
from typing import Literal, Optional, Type

from ampf.auth import AuthConfig, DefaultUser, ResetPasswordMailConfig, SmtpConfig
from ampf.tasks import TaskRunner
from ampf.tasks.background_runner import BackgroundRunner
from ampf.tasks.pubsub_push_runner import PubsubPushRunner
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__

from .feature_flags import FeatureFlags


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    feature_flags_str: str = Field(default="", alias="FEATURE_FLAGS")
    version: str = __version__
    production: bool = True
    data_dir: str = "./data/"
    prompt_dir: str = "./prompts/"

    gcp_root_storage: Optional[str] = None
    gcp_bucket_name: Optional[str] = None

    auth: AuthConfig = AuthConfig(jwt_secret_key="")
    default_user: DefaultUser = DefaultUser(username="admin", password="")
    smtp: SmtpConfig = SmtpConfig()
    reset_password_mail: ResetPasswordMailConfig = ResetPasswordMailConfig()

    session_secret_key: str | None = None
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None

    google_api_key: str  # Google GenAI API key

    translator_ai_model_name: str = "gemini-2.5-flash-lite"
    teacher_ai_model_name: str = "gemini-2.5-flash"
    verifier_ai_model_name: str = "gemini-2.5-flash"

    task_runner: Literal["Background", "PubsubPush"] = "Background"
    teacher_topic: str = "teacher"

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

    @cached_property
    def feature_flags(self) -> FeatureFlags:
        if not self.feature_flags_str:
            return FeatureFlags()
        # "a, b , c " → {"a", "b", "c"}
        enabled = {f.strip() for f in self.feature_flags_str.split(",") if f.strip()}
        for f in enabled:
            if f not in FeatureFlags.model_fields:
                raise ValueError(f"Unknown feature flag: {f}")
        # Only fields defined in FeatureFlags are considered, others are ignored
        data = {field_name: field_name in enabled for field_name in FeatureFlags.model_fields}
        return FeatureFlags.model_validate(data)

    @cached_property
    def task_runner_type(self) -> Type[TaskRunner]:
        match self.task_runner:
            case "Background":
                return BackgroundRunner
            case "PubsubPush":
                return PubsubPushRunner
            case _:
                raise ValueError(f"Unknown task runner type: {self.task_runner}")
