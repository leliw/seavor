import logging
from dataclasses import dataclass

from ampf.base import BaseAsyncFactory
from app_config import AppConfig
from core.users.user_model import UserInDB
from core.users.user_service import UserService
from shared.prompts.prompt_service import PromptService
from storage_def import STORAGE_DEF

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig
    factory: BaseAsyncFactory
    prompt_service: PromptService
    user_service: UserService

    _initialised = False
    
    @classmethod
    def create(cls, config: AppConfig):
        if config.gcp_root_storage:
            from ampf.gcp import GcpAsyncFactory

            factory = GcpAsyncFactory(root_storage=config.gcp_root_storage, bucket_name=config.gcp_bucket_name)
            _log.info(f"GCP storage root: {config.gcp_root_storage}")
            _log.info(f"GCP storage bucket: {config.gcp_bucket_name}")
        elif config.data_dir:
            from ampf.local import LocalAsyncFactory

            factory = LocalAsyncFactory(config.data_dir)
            _log.info(f"Local storage: {config.data_dir}")
        else:
            raise ValueError("No factory setup!")

        user_storage = factory.create_storage_tree(STORAGE_DEF[0], UserInDB)
        return cls(
            config=config,
            factory=factory,
            prompt_service=PromptService(config.prompt_dir),
            user_service=UserService(user_storage),
        )

    async def __aenter__(self):
        if not self._initialised:
            await self.user_service.initialise_storage(self.config.default_user)
            self._initialised = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
