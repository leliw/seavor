import logging
from typing import Self

from features.native_pages.native_page_model import NativePage
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_model import Page
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.workflows.base_workflow import BaseWorkflow, BaseWorkflowContext

_log = logging.getLogger(__name__)


class DefinitionGuessWorkflowContext(BaseWorkflowContext):
    phrase: str
    content: DefinitionGuessCreate | None = None

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str) -> Self:
        return cls(**body.model_dump(), username=username)


class DefinitionGuessWorkflow(BaseWorkflow):
    async def execute(self, body: TeacherDefinitionGuessCreate, username: str) -> RepetitionCard:
        snapshot = DefinitionGuessWorkflowContext.create(body, username)
        topic = await self._ensure_topic(snapshot)
        await self._ensure_native_topic(snapshot, topic.id)
        snapshot.topic = topic
        definition_guess_create = await self._generate_definition_guess(snapshot)
        snapshot.content = definition_guess_create
        page = await self._create_page(snapshot)
        snapshot.page = page
        await self._translate_page(snapshot)
        return await self._create_repetition_card(snapshot)

    async def _generate_definition_guess(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessCreate:
        teacher_service = self.teacher_service_factory.create(ctx.language, ctx.level)
        max_retries = 3
        for attempt in range(max_retries):
            definition_guess_create = await teacher_service.create_definition_guess(
                ctx.required_topic.title, ctx.phrase
            )
            evaluation = await self.verifier_service.verify_definition_guess(
                ctx.required_topic, definition_guess_create
            )
            if evaluation.score > 95:
                break
            elif attempt == max_retries - 1:
                raise ValueError(f"Failed to create and verify page after {max_retries} attempts.")
            else:
                _log.warning(f"Page verification failed. Retrying... ({attempt + 1}/{max_retries})")
        return definition_guess_create

    async def _create_page(self, ctx: DefinitionGuessWorkflowContext) -> Page:
        if ctx.content is None:
            raise ValueError("Content is required")
        page_service = self.page_service_factory.create(ctx.language, ctx.level, ctx.required_topic.id)
        page = await page_service.post_definition_guess(ctx.content)
        return page

    async def _translate_page(self, ctx: DefinitionGuessWorkflowContext) -> NativePage:
        native_page_service = self.native_page_service_factory.create(
            ctx.language, ctx.level, ctx.native_language, ctx.required_topic.id
        )
        native_page = await self.page_translator.translate_page_to_native(
            ctx.language, ctx.native_language, ctx.required_page
        )
        return await native_page_service.create(native_page)
