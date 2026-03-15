from typing import Optional
from uuid import uuid4
from ampf.auth import DefaultUser
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.feature_flags import FeatureFlags
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

    default_user: DefaultUser = DefaultUser(username="admin", password=uuid4().hex, email="admin@admin.admin")

class ClientConfig(BaseModel):
    version: str
