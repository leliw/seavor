import logging
from typing import Annotated
from uuid import UUID

from ampf.auth import AuthService, InsufficientPermissionsError, TokenPayload
from ampf.base import BaseAsyncCollectionStorage, BaseAsyncFactory, BaseEmailSender, EmailTemplate, SmtpEmailSender
from ampf.dependency import DependencyRegistry, get_dependency
from ampf.tasks import ManagedTaskRunner, TaskRunner
from ampf.tasks.background_runner import BackgroundRunner
from app_state import AppState
from core.app_config import AppConfig
from core.roles import Role
from core.teacher_ai_model import TeacherAIModel
from core.translator_ai_model import TranslatorAIModel
from core.users.user_model import UserInDB
from core.users.user_service import UserService
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.concurrency import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageService, NativePageServiceFactory
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_service import PageService, PageServiceFactory
from features.repetitions.repetition_service import RepetitionService, RepetitionServiceFactory
from features.teacher.teacher_service import TeacherServiceFactory
from features.teacher.verifier_service import VerifierService
from features.topics.topic_model import Topic
from features.topics.topic_service import TopicService
from features.workflows.workflow_factory import WorkflowFactory
from haintech.ai import BaseImageGenerator
from haintech.ai.google_genai import GenAIImageGenerator, GoogleAIModel
from haintech.ai.prompts.prompt_service import PromptService
from integrations.gtts.gtts_service import GttsService
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService
from shared.prompts.prompt_executor_image import PromptExecutorImage

load_dotenv()

_log = logging.getLogger(__name__)


def lifespan(config: AppConfig):
    DependencyRegistry.clear()
    app_state = AppState.create(config)
    DependencyRegistry.add(app_state)
    DependencyRegistry.add_all(app_state)
    DependencyRegistry.add(app_state.user_storage, BaseAsyncCollectionStorage[UserInDB])
    DependencyRegistry.add(app_state.task_runner, TaskRunner)
    DependencyRegistry.register_class(GttsService)
    DependencyRegistry.register_class(AudioFileService)
    DependencyRegistry.register_class(TranslatorAIModel)
    DependencyRegistry.register_class(TeacherAIModel)
    DependencyRegistry.add(GenAIImageGenerator(), BaseImageGenerator)
    DependencyRegistry.register_class(ImageService)
    DependencyRegistry.register_class(TopicService)
    DependencyRegistry.register_class(PageServiceFactory)
    DependencyRegistry.register_class(NativeTopicService)
    DependencyRegistry.register_class(NativePageServiceFactory)
    DependencyRegistry.register_class(NativeTopicTranslator)
    DependencyRegistry.register_class(NativePageTranslator)
    DependencyRegistry.register_class(TeacherServiceFactory)
    DependencyRegistry.register_class(VerifierService)
    DependencyRegistry.register_class(RepetitionServiceFactory)
    DependencyRegistry.register_class(WorkflowFactory)
    DependencyRegistry.register(get_prompt_executor_image)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.app_state = app_state
        async with app_state.manage_lifecycle(app):
            yield

    return lifespan


AppStateDep = Annotated[AppState, Depends(get_dependency(AppState))]
AppConfigDep = Annotated[AppConfig, Depends(get_dependency(AppConfig))]
FactoryDep = Annotated[BaseAsyncFactory, Depends(get_dependency(BaseAsyncFactory))]
UserServiceDep = Annotated[UserService, Depends(get_dependency(UserService))]
AudioFileServiceDep = Annotated[AudioFileService, Depends(get_dependency(AudioFileService))]
ImageServiceDep = Annotated[ImageService, Depends(get_dependency(ImageService))]
TopicServiceDep = Annotated[TopicService, Depends(get_dependency(TopicService))]
PageServiceFactoryDep = Annotated[PageServiceFactory, Depends(get_dependency(PageServiceFactory))]
NativeTopicServiceDep = Annotated[NativeTopicService, Depends(get_dependency(NativeTopicService))]
NativeTopicTranslatorDep = Annotated[NativeTopicTranslator, Depends(get_dependency(NativeTopicTranslator))]
NativePageServiceFactoryDep = Annotated[NativePageServiceFactory, Depends(get_dependency(NativePageServiceFactory))]
NativePageTranslatorDep = Annotated[NativePageTranslator, Depends(get_dependency(NativePageTranslator))]
PromptServiceDep = Annotated[PromptService, Depends(get_dependency(PromptService))]
TeacherServiceFactoryDep = Annotated[TeacherServiceFactory, Depends(get_dependency(TeacherServiceFactory))]
RepetitionServiceFactoryDep = Annotated[RepetitionServiceFactory, Depends(get_dependency(RepetitionServiceFactory))]
WorkflowFactoryDep = Annotated[WorkflowFactory, Depends(get_dependency(WorkflowFactory))]
PromptExecutorImageDep = Annotated[PromptExecutorImage, Depends(get_dependency(PromptExecutorImage))]


def not_production(app_state: AppStateDep) -> bool:
    if app_state.config.production:
        raise HTTPException(status_code=404, detail="Not found")
    return not app_state.config.production


def get_page_service(topic_id: UUID):
    page_service_factory = DependencyRegistry.get(PageServiceFactory)
    return page_service_factory.create(topic_id)


PageServiceDep = Annotated[PageService, Depends(get_page_service)]


def get_email_sender(app_state: AppStateDep) -> BaseEmailSender:
    return SmtpEmailSender(
        host=app_state.config.smtp.host,
        port=app_state.config.smtp.port,
        username=app_state.config.smtp.username,
        password=app_state.config.smtp.password,
        use_ssl=app_state.config.smtp.use_ssl,
    )


EmailSenderDep = Annotated[BaseEmailSender, Depends(get_email_sender)]


def get_auth_service(app_state: AppStateDep) -> AuthService:
    reset_mail_template = EmailTemplate(
        sender=app_state.config.reset_password_mail.sender,
        subject=app_state.config.reset_password_mail.subject,
        body_template=app_state.config.reset_password_mail.body_template,
    )
    return AuthService(
        storage_factory=app_state.factory,
        user_service=app_state.user_service,
        auth_config=app_state.config.auth,
        email_sender_service=get_email_sender(app_state),
        reset_mail_template=reset_mail_template,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AuthTokenDep = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="api/login"))]
OptionalAuthTokenDep = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False))]


async def decode_token(auth_service: AuthServiceDep, token: AuthTokenDep) -> TokenPayload:
    return await auth_service.decode_token(token)


async def optional_decode_token(auth_service: AuthServiceDep, token: OptionalAuthTokenDep) -> TokenPayload | None:
    if not token:
        _log.debug("No token provided")
        return None
    return await auth_service.decode_token(token)


TokenPayloadDep = Annotated[TokenPayload, Depends(decode_token)]
OptionalTokenPayloadDep = Annotated[TokenPayload | None, Depends(optional_decode_token)]


class Authorize:
    """Dependency for authorizing users based on their role."""

    def __init__(self, required_role: Role | None = None):
        self.required_role = required_role

    def __call__(self, token_payload: TokenPayloadDep) -> bool:
        if not self.required_role or self.required_role in token_payload.roles:
            return True
        else:
            raise InsufficientPermissionsError()


def get_repetition_service_dep(
    repetition_service_factory: RepetitionServiceFactoryDep, token_payload: TokenPayloadDep
) -> RepetitionService:
    return repetition_service_factory.create(token_payload.sub)


RepetitionServiceDep = Annotated[RepetitionService, Depends(get_repetition_service_dep)]


async def get_topic_for_user(
    service: TopicServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
    token_payload: OptionalTokenPayloadDep,
) -> Topic:
    username = token_payload.sub if token_payload else None
    return await service.get_for_user(target_language, level, topic_id, username)


AuthorizedTopicDep = Annotated[Topic, Depends(get_topic_for_user)]


def get_native_page_service(
    target_language: Language,
    level: Level,
    native_language: Language,
    topic_id: UUID,
):
    native_page_service_factory = DependencyRegistry.get(NativePageServiceFactory)
    return native_page_service_factory.create(target_language, level, native_language, topic_id)


NativePageServiceDep = Annotated[NativePageService, Depends(get_native_page_service)]


def get_task_runner(app_state: AppStateDep, background_tasks: BackgroundTasks) -> TaskRunner:
    if isinstance(app_state.task_runner, ManagedTaskRunner):
        return app_state.task_runner
    elif app_state.task_runner == BackgroundRunner:
        return BackgroundRunner(background_tasks)
    else:
        return app_state.task_runner.create()


TaskRunnerDep = Annotated[TaskRunner, Depends(get_task_runner)]


def get_prompt_executor_image(app_config: AppConfigDep, prompt_service: PromptServiceDep) -> PromptExecutorImage:
    return PromptExecutorImage(
        ai_model=GoogleAIModel(parameters={"temperature": 0.5}, api_key=app_config.google_api_key),
        image_generator=GenAIImageGenerator(
            model_name="gemini-3.1-flash-image-preview", api_key=app_config.google_api_key
        ),
        prompt_service=prompt_service,
    )
