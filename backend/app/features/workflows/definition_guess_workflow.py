import logging
from typing import Awaitable, Callable, Self
from uuid import UUID

from ampf.processors.task_model import TaskRunner
from ampf.processors.pubsub_runner import PubsubRunner
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.workflows.base_workflow import BaseWorkflow, BaseWorkflowContext, WorkflowStatus, WorkflowType

_log = logging.getLogger(__name__)


class DefinitionGuessWorkflowContext(BaseWorkflowContext):
    type: WorkflowType = WorkflowType.DEFINITION_GUESS

    phrase: str
    content: DefinitionGuessCreate | None = None

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str) -> Self:
        return cls(**body.model_dump(), username=username)


class DefinitionGuessWorkflow(BaseWorkflow[DefinitionGuessWorkflowContext]):
    def __init__(self, storage, task_runner: TaskRunner | None = None):
        super().__init__(storage, task_runner)
        self._steps: list[Callable[[DefinitionGuessWorkflowContext], Awaitable[DefinitionGuessWorkflowContext]]] = [
            self.ensure_topics,
            self.generate_content,
            self.create_page,
            self.translate_page,
            self.create_repetition_card,
        ]
        self._checkpoint_steps = {1, 3}

    async def create(self, body: TeacherDefinitionGuessCreate, username: str) -> DefinitionGuessWorkflowContext:
        snapshot = DefinitionGuessWorkflowContext.create(body, username)
        snapshot.total_steps = len(self._steps)
        snapshot.status = WorkflowStatus.PENDING
        await self.storage.create(snapshot)
        return snapshot

    async def run(self, ctx_id: UUID) -> DefinitionGuessWorkflowContext:
        ctx = await self.storage.get(ctx_id)
        if ctx.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELED]:
            return ctx
        try:
            ctx.status = WorkflowStatus.RUNNING
            await self.storage.patch(ctx_id, {"status": ctx.status})
            while ctx.current_step < ctx.total_steps:
                ctx = await self.execute_step(ctx.current_step, ctx)
                ctx.current_step += 1
                await self.storage.save(ctx)
                if isinstance(self.task_runner, PubsubRunner):
                    if self.should_checkpoint(ctx):
                        await self.task_runner.run_async("teacher", ctx)
                        return ctx
            ctx.status = WorkflowStatus.COMPLETED
            await self.storage.patch(ctx_id, {"status": ctx.status})
            return ctx
        except Exception as e:
            ctx.status = WorkflowStatus.FAILED
            ctx.error = str(e)
            await self.storage.save(ctx)
            raise

    async def execute_step(self, step: int, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        step_fn = self._steps[step]
        return await step_fn(ctx)

    def should_checkpoint(self, ctx: DefinitionGuessWorkflowContext) -> bool:
        return ctx.current_step in self._checkpoint_steps

    async def execute(self, body: TeacherDefinitionGuessCreate, username: str) -> DefinitionGuessWorkflowContext:
        snapshot = await self.create(body, username)
        return await self.run(snapshot.id)

    async def ensure_topics(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.topic and ctx.page:
            return ctx
        topic = await self._ensure_topic(ctx)
        await self._ensure_native_topic(ctx, topic.id)
        ctx.topic = topic
        return ctx

    async def generate_content(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.content is not None:
            return ctx
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
        ctx.content = definition_guess_create
        return ctx

    async def create_page(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.page is not None:
            return ctx
        if ctx.content is None:
            raise ValueError("Content is required")
        page_service = self.page_service_factory.create(ctx.language, ctx.level, ctx.required_topic.id)
        page = await page_service.post(ctx.content)
        ctx.page = page
        return ctx

    async def translate_page(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.native_page is not None:
            return ctx
        native_page_service = self.native_page_service_factory.create(
            ctx.language, ctx.level, ctx.native_language, ctx.required_topic.id
        )
        native_page = await self.page_translator.translate_page_to_native(
            ctx.language, ctx.native_language, ctx.required_page
        )
        await native_page_service.create(native_page)
        ctx.native_page = native_page
        return ctx

    async def create_repetition_card(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.repetition_card is not None:
            return ctx
        ctx.repetition_card = await self._create_repetition_card(ctx)
        return ctx
