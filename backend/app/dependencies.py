import logging
from typing import Annotated
from uuid import UUID

from ampf.auth import AuthService, InsufficientPermissionsError, TokenPayload
from ampf.base import BaseEmailSender, EmailTemplate, SmtpEmailSender
from ampf.base.versioned_base_model import StorageFormatFlags
from app_config import AppConfig
from app_state import AppState
from core.roles import Role
from core.users.user_service import UserService
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeGapFillChoiceExercise_v2, NativeInfoPage_v2
from features.native_pages.native_page_translator import NativePageTranslator
from features.native_topics.native_topic_service import NativeTopicService
from features.native_topics.native_topic_translator import NativeTopicTranslator
from features.pages.page_model import GapFillChoiceExercise_v2, InfoPage_v2
from features.pages.page_service import PageService
from features.repetitions.repetition_service import RepetitionService
from features.topics.topic_model import Topic, Topic_v2
from features.topics.topic_service import TopicService
from haintech.ai import BaseAIModel, BaseImageGenerator
from haintech.ai.google_genai import GenAIImageGenerator
from integrations.gtts.gtts_service import GttsService
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService
from shared.prompts.prompt_service import PromptService

load_dotenv()

_log = logging.getLogger(__name__)


def lifespan(config: AppConfig):
    app_state = AppState.create(config)
    Topic_v2.FORMAT_FLAGS = StorageFormatFlags(
        save_new_format=config.feature_flags.topic_v2_storage,
        migrate_legacy_on_read=config.feature_flags.topic_v2_migrate,
    )
    page_sff = StorageFormatFlags(
        save_new_format=config.feature_flags.page_v2_storage,
        migrate_legacy_on_read=config.feature_flags.page_v2_migrate,
    )
    InfoPage_v2.FORMAT_FLAGS = page_sff
    NativeInfoPage_v2.FORMAT_FLAGS = page_sff
    GapFillChoiceExercise_v2.FORMAT_FLAGS = page_sff
    NativeGapFillChoiceExercise_v2.FORMAT_FLAGS = page_sff

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.app_state = app_state
        async with app_state:
            yield

    return lifespan


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state


AppStateDep = Annotated[AppState, Depends(get_app_state)]


def get_app_config(app_state: AppStateDep) -> AppConfig:
    return app_state.config


ConfigDep = Annotated[AppConfig, Depends(get_app_config)]


def get_user_service(app_state: AppStateDep) -> UserService:
    return app_state.user_service


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_prompt_service(app_state: AppStateDep) -> PromptService:
    return app_state.prompt_service


PromptServiceDep = Annotated[PromptService, Depends(get_prompt_service)]


def get_tts_service() -> GttsService:
    return GttsService()


GttsServiceDep = Annotated[GttsService, Depends(get_tts_service)]


def get_audio_file_service(app_state: AppStateDep, tts_service: GttsServiceDep) -> AudioFileService:
    return AudioFileService(app_state.factory, tts_service)


AudioFileServiceDep = Annotated[AudioFileService, Depends(get_audio_file_service)]


def get_image_generator() -> BaseImageGenerator | None:
    try:
        return GenAIImageGenerator()
    except Exception:
        return None


ImageGeneratorDep = Annotated[BaseImageGenerator | None, Depends(get_image_generator)]


def get_image_service(app_state: AppStateDep, image_generator: ImageGeneratorDep) -> ImageService:
    return ImageService(app_state.factory, image_generator)


ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]


def not_production(app_state: AppStateDep) -> bool:
    if app_state.config.production:
        raise HTTPException(status_code=404, detail="Not found")
    return not app_state.config.production


def get_topic_service(app_state: AppStateDep) -> TopicService:
    return app_state.topic_service


TopicServiceDep = Annotated[TopicService, Depends(get_topic_service)]


def get_native_topic_service(app_state: AppStateDep) -> NativeTopicService:
    return app_state.native_topic_service


NativeTopicServiceDep = Annotated[NativeTopicService, Depends(get_native_topic_service)]


def get_translator_ai_model(app_state: AppStateDep):
    from haintech.ai.google_genai import GoogleAIModel

    return GoogleAIModel(model_name="gemini-2.5-flash-lite", parameters={"temperature": 0.0})


TranslatorAIModelDep = Annotated[BaseAIModel, Depends(get_translator_ai_model)]


def get_native_topic_translator(
    translator_ai_model: TranslatorAIModelDep, topic_service: TopicServiceDep
) -> NativeTopicTranslator:
    return NativeTopicTranslator(translator_ai_model, topic_service)


NativeTopicTranslatorDep = Annotated[NativeTopicTranslator, Depends(get_native_topic_translator)]


def get_page_service(
    app_state: AppStateDep,
    audio_file_service: AudioFileServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
):
    return PageService(app_state.factory, audio_file_service, target_language, level, topic_id)


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


def get_repetition_service(app_state: AppStateDep, token_payload: TokenPayloadDep) -> RepetitionService:
    return RepetitionService(app_state.user_storage.get_collection(token_payload.sub, "languages"))


RepetitionServiceDep = Annotated[RepetitionService, Depends(get_repetition_service)]


def get_native_topic_page_translator(
    translator_ai_model: TranslatorAIModelDep, prompt_service: PromptServiceDep, page_service: PageServiceDep
) -> NativePageTranslator:
    return NativePageTranslator(translator_ai_model, prompt_service, page_service)


NativePageTranslatorDep = Annotated[NativePageTranslator, Depends(get_native_topic_page_translator)]


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
