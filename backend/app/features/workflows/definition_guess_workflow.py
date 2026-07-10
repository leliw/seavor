import logging
from typing import Awaitable, Callable, Literal, Self
from uuid import NAMESPACE_DNS, UUID, uuid5

from ampf.dependency import DependencyRegistry
from ampf.tasks.pubsub_runner import PubsubRunner
from ampf.tasks import TaskRunner, TaskStatus
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_base_model import PageType
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from pydantic import computed_field

from shared.images.image_model import ImageBlob, ImageMetadata
from shared.images.image_service import ImageService
from shared.prompts.prompt_executor_image import PromptExecutorImage

from .base_workflow import BaseWorkflow, BaseWorkflowContext, TaskType

_log = logging.getLogger(__name__)


class DefinitionGuessWorkflowContext(BaseWorkflowContext):
    type: Literal[TaskType.DEFINITION_GUESS] = TaskType.DEFINITION_GUESS

    phrase: str
    content: DefinitionGuessCreate | None = None
    image_name: str | None = None

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str) -> Self:
        return cls(**body.model_dump(), username=username, name=f"Definition guess for '{body.phrase}'")

    @computed_field
    @property
    def result_id(self) -> str | None:
        return str(self.repetition_card.id) if self.repetition_card else None


class DefinitionGuessWorkflow(BaseWorkflow[DefinitionGuessWorkflowContext]):
    def __init__(self, storage, task_runner: TaskRunner | None = None):
        super().__init__(storage, task_runner)
        self._steps: list[Callable[[DefinitionGuessWorkflowContext], Awaitable[DefinitionGuessWorkflowContext]]] = [
            self.ensure_topics,
            self.generate_content,
            self.create_page,
            self.translate_page,
            self.generate_image,
            self.create_repetition_card,
        ]
        self._checkpoint_steps = {1, 3}

    async def create(self, body: TeacherDefinitionGuessCreate, username: str) -> DefinitionGuessWorkflowContext:
        snapshot = DefinitionGuessWorkflowContext.create(body, username)
        snapshot.total_steps = len(self._steps)
        snapshot.status = TaskStatus.PENDING
        await self.storage.create(snapshot)
        return snapshot

    async def run(self, ctx_id: UUID) -> DefinitionGuessWorkflowContext:
        ctx = await self.storage.get(ctx_id)
        if ctx.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED]:
            return ctx
        try:
            ctx.status = TaskStatus.RUNNING
            await self.storage.patch(ctx_id, {"status": ctx.status})
            while ctx.current_step < ctx.total_steps:
                ctx = await self.execute_step(ctx.current_step, ctx)
                ctx.current_step += 1
                await self.storage.save(ctx)
                if isinstance(self.task_runner, PubsubRunner):
                    if self.should_checkpoint(ctx):
                        await self.task_runner.run_async("teacher", ctx)
                        return ctx
            ctx.status = TaskStatus.COMPLETED
            await self.storage.patch(ctx_id, {"status": ctx.status})
            return ctx
        except Exception as e:
            ctx.status = TaskStatus.FAILED
            ctx.error_message = str(e)
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
        page_service = self.page_service_factory.create(ctx.required_topic.id)
        page = await page_service.post(ctx.content)
        ctx.page = page
        return ctx

    async def translate_page(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.native_page is not None:
            return ctx
        native_page_service = self.native_page_service_factory.create(ctx.native_language, ctx.required_topic.id)
        native_page = await self.page_translator.translate_page_to_native(ctx.native_language, ctx.required_page)
        await native_page_service.create(native_page)
        ctx.native_page = native_page
        return ctx

    async def create_repetition_card(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.repetition_card is not None:
            return ctx
        ctx.repetition_card = await self._create_repetition_card(ctx)
        return ctx

    async def generate_image(self, ctx: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflowContext:
        if ctx.image_name is not None:
            return ctx

        if ctx.content is None:
            raise ValueError("Content is required")
        prompt_executor_image = DependencyRegistry.get(PromptExecutorImage)
        blob_create = await prompt_executor_image.execute_image_prompt_async(
            "picture_generator", topic=ctx.required_topic, content=ctx.required_page
        )
        if not blob_create:
            return ctx
        name = uuid5(NAMESPACE_DNS, f"{ctx.language.value}-{ctx.phrase}").hex
        blob = ImageBlob(
            name=name,
            content=blob_create.content,
            metadata=ImageMetadata(
                **blob_create.metadata.model_dump(),
                language=ctx.language.value,
                text=ctx.phrase,
                description=ctx.content.definition,
            ),
        )
        image_service = DependencyRegistry.get(ImageService)
        await image_service.upload(blob)
        if ctx.required_page.type != PageType.DEFINITION_GUESS:
            raise ValueError(f"Unsupported page type: {ctx.required_page.type}")
        ctx.image_name = blob.name
        page_service = self.page_service_factory.create(ctx.required_topic.id)
        await page_service.add_image_name(ctx.required_page.id, blob.name)
        return ctx
