from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from version import __version__


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    version: str = __version__

    data_dir: str = "./data/"
    
    gcp_root_storage: Optional[str] = None
    gcp_bucket_name: Optional[str] = None


class ClientConfig(BaseModel):
    version: str
