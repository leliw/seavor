from ampf.base import KeyNotExistsException

from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_service import PageServiceFactory
from features.repetitions.repetition_model import RepetitionCardCreate
from features.repetitions.repetition_service import RepetitionService
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.teacher.teacher_service import TeacherServiceFactory
from features.topics.topic_service import TopicService


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


    async def create_definition_guess_workflow(self, body: TeacherDefinitionGuessCreate, username: str):
        topic = await self.topic_service.get_or_create_default_topic(body.language, body.level, username)
        try:
            native_topic = await self.native_topic_service.get(body.language, body.level, body.native_language, topic.id)
        except KeyNotExistsException:
            native_topic = await self.topic_translator.translate_topic_to_native(
                body.language, body.level, body.native_language, topic.id
            )
            await self.native_topic_service.create(native_topic)
        teacher_service = self.teacher_service_factory.create(body.language, body.level)
        definition_guess_create = teacher_service.create_definition_guess(topic.title, body.phrase)
        page_service = self.page_service_factory.create(body.language, body.level, topic.id)
        page = await page_service.post_definition_guess(definition_guess_create)
        native_page = await self.page_translator.translate_page_to_native(body.language, body.native_language, page)
        native_page_service = self.native_page_service_factory.create(body.language, body.level, body.native_language, topic.id)
        await native_page_service.create(native_page)
        repetition_card_create = RepetitionCardCreate(
            language=body.language,
            level=body.level,
            topic_id=topic.id,
            page_id=page.id,
        )
        return await self.repetition_service.create(repetition_card_create)
