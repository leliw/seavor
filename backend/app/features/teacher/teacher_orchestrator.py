from uuid import UUID

from ampf.base import KeyNotExistsException
from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_model import NativeTopic
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_model import Page
from features.pages.page_service import PageServiceFactory
from features.repetitions.repetition_model import RepetitionCard, RepetitionCardCreate
from features.repetitions.repetition_service import RepetitionService
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.teacher.teacher_service import TeacherServiceFactory
from features.teacher.workflows.base_workflow import BaseWorkflowSnapshot
from features.topics.topic_model import Topic
from features.topics.topic_service import TopicService


class DefinitionGuessWorkflowSnapshot(BaseWorkflowSnapshot):
    phrase: str

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str):
        return cls(
            language=body.language,
            level=body.level,
            native_language=body.native_language,
            phrase=body.phrase,
            username=username,
        )


class TeacherOrchestrator:
    def __init__(
        self,
        topic_service: TopicService,
        topic_translator: NativeTopicTranslator,
        native_topic_service: NativeTopicService,
        page_service_factory: PageServiceFactory,
        page_translator: NativePageTranslator,
        native_page_service_factory: NativePageServiceFactory,
        teacher_service_factory: TeacherServiceFactory,
        repetition_service: RepetitionService,
    ):
        self.topic_service = topic_service
        self.topic_translator = topic_translator
        self.native_topic_service = native_topic_service
        self.repetition_service = repetition_service
        self.page_service_factory = page_service_factory
        self.page_translator = page_translator
        self.native_page_service_factory = native_page_service_factory
        self.teacher_service_factory = teacher_service_factory

    async def create_definition_guess_workflow(
        self, body: TeacherDefinitionGuessCreate, username: str
    ) -> RepetitionCard:
        snapshot = DefinitionGuessWorkflowSnapshot.create(body, username)
        topic = await self._ensure_topic(snapshot)
        await self._ensure_native_topic(snapshot, topic.id)
        definition_guess_create = await self._generate_definition_guess(snapshot, topic.title)
        page = await self._create_page_with_translation(snapshot, topic.id, definition_guess_create)
        return await self._create_repetition_card(snapshot, topic.id, page.id)

    async def _ensure_topic(self, snapshot: BaseWorkflowSnapshot) -> Topic:
        return await self.topic_service.get_or_create_default_topic(
            snapshot.language, snapshot.level, snapshot.username
        )

    async def _ensure_native_topic(self, snapshot: BaseWorkflowSnapshot, topic_id: UUID) -> NativeTopic:
        try:
            return await self.native_topic_service.get(
                snapshot.language, snapshot.level, snapshot.native_language, topic_id
            )
        except KeyNotExistsException:
            native_topic = await self.topic_translator.translate_topic_to_native(
                snapshot.language, snapshot.level, snapshot.native_language, topic_id
            )
            return await self.native_topic_service.create(native_topic)

    async def _generate_definition_guess(
        self, snapshot: DefinitionGuessWorkflowSnapshot, topic_title: str
    ) -> DefinitionGuessCreate:
        teacher_service = self.teacher_service_factory.create(snapshot.language, snapshot.level)
        return teacher_service.create_definition_guess(topic_title, snapshot.phrase)

    async def _create_page_with_translation(
        self, snapshot: DefinitionGuessWorkflowSnapshot, topic_id: UUID, content: DefinitionGuessCreate
    ) -> Page:
        page_service = self.page_service_factory.create(snapshot.language, snapshot.level, topic_id)
        page = await page_service.post_definition_guess(content)

        native_page = await self.page_translator.translate_page_to_native(
            snapshot.language, snapshot.native_language, page
        )
        native_page_service = self.native_page_service_factory.create(
            snapshot.language, snapshot.level, snapshot.native_language, topic_id
        )
        await native_page_service.create(native_page)
        return page

    async def _create_repetition_card(
        self, snapshot: BaseWorkflowSnapshot, topic_id: UUID, page_id: UUID
    ) -> RepetitionCard:
        repetition_card_create = RepetitionCardCreate(
            language=snapshot.language,
            level=snapshot.level,
            topic_id=topic_id,
            page_id=page_id,
        )
        return await self.repetition_service.create(repetition_card_create)
