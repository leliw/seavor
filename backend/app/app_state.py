import logging
from dataclasses import dataclass

from app_config import AppConfig

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig

    @classmethod
    def create(cls, config: AppConfig):
        return cls(
            config=config,
        )
