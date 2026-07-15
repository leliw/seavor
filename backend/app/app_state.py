import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Type

from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory
from ampf.gcp import GcpAsyncFactory
from ampf.tasks import ManagedTaskRunner, TaskRunner
from ampf.tasks.pubsub_push_runner import PubsubRunner
from core.app_config import AppConfig
from core.users.user_model import UserInDB
from core.users.user_service import UserService
from fastapi import FastAPI
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
    task_runner: TaskRunner | Type[TaskRunner]
    _initialised = False

    @classmethod
    def create(cls, config: AppConfig):
        factory = cls.create_factory(config)
        user_storage = factory.get_collection(UserInDB)
        if issubclass(config.task_runner_type, PubsubRunner):
            if not isinstance(factory, GcpAsyncFactory):
                raise RuntimeError(
                    f"{config.task_runner_type.__name__} requires GcpAsyncFactory, but got {type(factory).__name__}"
                )
            task_runner = config.task_runner_type.create(factory, config)  # pyright: ignore[reportArgumentType]
        else:
            task_runner = config.task_runner_type
        return cls(
            config=config,
            factory=factory,
            prompt_service=PromptService(config.prompt_dir),
            user_storage=user_storage,
            user_service=UserService(user_storage),
            task_runner=task_runner,
        )

    @staticmethod
    def create_factory(config: AppConfig) -> BaseAsyncFactory:
        if config.gcp_root_storage:
            factory = GcpAsyncFactory(root_storage=config.gcp_root_storage, bucket_name=config.gcp_bucket_name)
            _log.info(f"GCP storage root: {config.gcp_root_storage}")
            _log.info(f"GCP storage bucket: {config.gcp_bucket_name}")
        elif config.data_dir:
            from ampf.local import LocalAsyncFactory

            factory = LocalAsyncFactory(config.data_dir)
            _log.info(f"Local storage: {config.data_dir}")
        else:
            raise ValueError("No factory setup!")
        factory.register_collections(STORAGE_DEF)
        return factory

    @asynccontextmanager
    async def manage_lifecycle(self, app: FastAPI):
        if not self._initialised:
            await self.user_service.initialise_storage(self.config.default_user)
            self._initialised = True

        if isinstance(self.task_runner, ManagedTaskRunner):
            async with self.task_runner.manage_lifecycle(app):
                yield self
        else:
            yield self
