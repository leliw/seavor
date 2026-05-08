from enum import StrEnum
from typing import Any
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, KeyNotExistsException
from ampf.dependency import DependencyRegistry
from ampf.tasks import BaseTask, TaskRunner
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativePage
from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_model import NativeTopic
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_model import Page
from features.pages.page_service import PageServiceFactory
from features.repetitions.repetition_model import RepetitionCard, RepetitionCardCreate
from features.repetitions.repetition_service import RepetitionServiceFactory
from features.teacher.teacher_service import TeacherServiceFactory
from features.teacher.verifier_service import VerifierService
from features.topics.topic_model import Topic
from features.topics.topic_service import TopicService
from haintech.ai.prompts import PromptExecutor
from pydantic import computed_field


class TaskType(StrEnum):
    DEFINITION_GUESS = "definition-guess"
    OTHER_TASK = "other-task"


class BaseWorkflowContext(BaseTask):
    current_step: int = 0
    total_steps: int = 1

    language: Language
    level: Level
    native_language: Language
    username: str

    topic: Topic | None = None
    page: Page | None = None
    native_page: NativePage | None = None
    repetition_card: RepetitionCard | None = None

    @computed_field
    @property
    def progress(self) -> int | None:
        return 100 * self.current_step // self.total_steps if self.total_steps else None

    @property
    def required_topic(self) -> Topic:
        if self.topic is None:
            raise ValueError("Topic is required")
        return self.topic

    @property
    def required_page(self) -> Page:
        if self.page is None:
            raise ValueError("Page is required")
        return self.page

    def model_post_init(self, __context: Any) -> None:
        self.__pydantic_fields_set__.add("type")


class BaseWorkflow[T: BaseWorkflowContext]:
    def __init__(
        self,
        storage: BaseAsyncCollectionStorage[T],
        task_runner: TaskRunner | None = None,
        prompt_executor: PromptExecutor | None = None,
    ):
        self.storage = storage
        self.task_runner = task_runner or DependencyRegistry.get(TaskRunner)
        self.topic_service = DependencyRegistry.get(TopicService)
        self.topic_translator = DependencyRegistry.get(NativeTopicTranslator)
        self.native_topic_service = DependencyRegistry.get(NativeTopicService)
        self.page_service_factory = DependencyRegistry.get(PageServiceFactory)
        self.page_translator = DependencyRegistry.get(NativePageTranslator)
        self.native_page_service_factory = DependencyRegistry.get(NativePageServiceFactory)
        self.teacher_service_factory = DependencyRegistry.get(TeacherServiceFactory)
        self.verifier_service = DependencyRegistry.get(VerifierService)
        self.repetition_service_factory = DependencyRegistry.get(RepetitionServiceFactory)
        self.prompt_executor = prompt_executor or self.verifier_service.prompt_executor

    async def _ensure_topic(self, ctx: BaseWorkflowContext) -> Topic:
        return await self.topic_service.get_or_create_default_topic(ctx.language, ctx.level, ctx.username)

    async def _ensure_native_topic(self, ctx: BaseWorkflowContext, topic_id: UUID) -> NativeTopic:
        try:
            return await self.native_topic_service.get(ctx.language, ctx.level, ctx.native_language, topic_id)
        except KeyNotExistsException:
            native_topic = await self.topic_translator.translate_topic_to_native(
                ctx.language, ctx.level, ctx.native_language, topic_id
            )
            return await self.native_topic_service.create(native_topic)

    async def _create_repetition_card(self, ctx: BaseWorkflowContext) -> RepetitionCard:
        repetition_service = self.repetition_service_factory.create(ctx.username)
        repetition_card_create = RepetitionCardCreate(
            language=ctx.language,
            level=ctx.level,
            topic_id=ctx.required_topic.id,
            page_id=ctx.required_page.id,
        )
        return await repetition_service.create(repetition_card_create)
