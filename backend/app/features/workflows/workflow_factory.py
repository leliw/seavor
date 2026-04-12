from dataclasses import dataclass

from features.native_pages.native_page_service import NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_service import PageServiceFactory
from features.repetitions.repetition_service import RepetitionService
from features.teacher.teacher_service import TeacherServiceFactory
from features.teacher.verifier_service import VerifierService
from features.workflows.definition_guess_workflow import DefinitionGuessWorkflow
from features.topics.topic_service import TopicService


@dataclass
class WorkflowFactory:
    topic_service: TopicService
    topic_translator: NativeTopicTranslator
    native_topic_service: NativeTopicService
    page_service_factory: PageServiceFactory
    page_translator: NativePageTranslator
    native_page_service_factory: NativePageServiceFactory
    teacher_service_factory: TeacherServiceFactory
    verifier_service: VerifierService
    repetition_service: RepetitionService

    def create_definition_guess_workflow(self) -> DefinitionGuessWorkflow:
        return DefinitionGuessWorkflow(**{k: v for k, v in self.__dict__.items() if not k.startswith("_")})
