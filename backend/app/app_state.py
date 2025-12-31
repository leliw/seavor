import logging
from dataclasses import dataclass

from ampf.base import BaseAsyncFactory
from app_config import AppConfig

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig
    factory: BaseAsyncFactory

    @classmethod
    def create(cls, config: AppConfig):
        if config.gcp_root_storage:
            from ampf.gcp import GcpAsyncFactory

            factory = GcpAsyncFactory(root_storage=config.gcp_root_storage)
            _log.info(f"GCP storage root: {config.gcp_root_storage}")
        elif config.data_dir:
            from ampf.local import LocalAsyncFactory

            factory = LocalAsyncFactory(config.data_dir)
            _log.info(f"Local storage: {config.data_dir}")
        else:
            raise ValueError("No factory setup!")

        return cls(
            config=config,
            factory=factory,
        )
