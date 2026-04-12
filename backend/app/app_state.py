import logging
from dataclasses import dataclass

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory
from app_config import AppConfig
from core.users.user_model import UserInDB
from core.users.user_service import UserService
from features.native_topics.native_topic_service import NativeTopicService
from features.topics.topic_service import TopicService
from haintech.ai.prompts.prompt_service import PromptService
from storage_def import STORAGE_DEF

_log = logging.getLogger(__name__)


@dataclass
class AppState:
    config: AppConfig
    factory: BaseAsyncFactory
    prompt_service: PromptService
    user_storage: BaseAsyncCollectionStorage[UserInDB]
    user_service: UserService
    topic_service: TopicService
    native_topic_service: NativeTopicService

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

        user_storage = factory.create_storage_tree(STORAGE_DEF[0])
        native_topic_service = NativeTopicService(factory)
        topic_service = TopicService(factory)
        return cls(
            config=config,
            factory=factory,
            prompt_service=PromptService(config.prompt_dir),
            user_storage=user_storage,
            user_service=UserService(user_storage),
            topic_service=topic_service,
            native_topic_service=native_topic_service,
        )

    async def __aenter__(self):
        if not self._initialised:
            await self.user_service.initialise_storage(self.config.default_user)
            self._initialised = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
