from uuid import UUID

from ampf.base import KeyNotExistsException
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_model import NativeTopic
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_model import Page
from features.pages.page_service import PageServiceFactory
from features.repetitions.repetition_model import RepetitionCard, RepetitionCardCreate
from features.repetitions.repetition_service import RepetitionService
from features.teacher.teacher_service import TeacherServiceFactory
from features.teacher.verifier_service import VerifierService
from features.topics.topic_model import Topic
from features.topics.topic_service import TopicService
from haintech.ai.prompts import PromptExecutor
from pydantic import BaseModel


class BaseWorkflowContext(BaseModel):
    language: Language
    level: Level
    native_language: Language
    username: str

    topic: Topic | None = None
    page: Page | None = None

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


class BaseWorkflow:
    def __init__(
        self,
        topic_service: TopicService,
        topic_translator: NativeTopicTranslator,
        native_topic_service: NativeTopicService,
        page_service_factory: PageServiceFactory,
        page_translator: NativePageTranslator,
        native_page_service_factory: NativePageServiceFactory,
        teacher_service_factory: TeacherServiceFactory,
        verifier_service: VerifierService,
        repetition_service: RepetitionService,
        prompt_executor: PromptExecutor | None = None,
    ):
        self.topic_service = topic_service
        self.topic_translator = topic_translator
        self.native_topic_service = native_topic_service
        self.page_service_factory = page_service_factory
        self.page_translator = page_translator
        self.native_page_service_factory = native_page_service_factory
        self.teacher_service_factory = teacher_service_factory
        self.verifier_service = verifier_service
        self.repetition_service = repetition_service
        self.prompt_executor = prompt_executor or verifier_service.prompt_executor

    async def _ensure_topic(self, ctx: BaseWorkflowContext) -> Topic:
        return await self.topic_service.get_or_create_default_topic(
            ctx.language, ctx.level, ctx.username
        )

    async def _ensure_native_topic(self, ctx: BaseWorkflowContext, topic_id: UUID) -> NativeTopic:
        try:
            return await self.native_topic_service.get(
                ctx.language, ctx.level, ctx.native_language, topic_id
            )
        except KeyNotExistsException:
            native_topic = await self.topic_translator.translate_topic_to_native(
                ctx.language, ctx.level, ctx.native_language, topic_id
            )
            return await self.native_topic_service.create(native_topic)

    async def _create_repetition_card(self, ctx: BaseWorkflowContext) -> RepetitionCard:
        repetition_card_create = RepetitionCardCreate(
            language=ctx.language,
            level=ctx.level,
            topic_id=ctx.required_topic.id,
            page_id=ctx.required_page.id,
        )
        return await self.repetition_service.create(repetition_card_create)
