from typing import Annotated, Union
from uuid import UUID

from ampf.base import BaseAsyncFactory
from ampf.tasks import TaskRunner
from features.workflows.definition_guess_workflow import DefinitionGuessWorkflow, DefinitionGuessWorkflowContext
from pydantic import Field

WorkflowContext = Annotated[
    Union[DefinitionGuessWorkflowContext],
    Field(discriminator="type"),
]


class WorkflowFactory:
    def __init__(self, factory: BaseAsyncFactory, task_runner: TaskRunner | None = None):
        self.storage = factory.get_collection(WorkflowContext)
        self.task_runner = task_runner

    def create_definition_guess_workflow(self, task_runner: TaskRunner | None = None) -> DefinitionGuessWorkflow:
        return DefinitionGuessWorkflow(self.storage, task_runner or self.task_runner)

    def create_for_context(self, context: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflow:
        return self.create_definition_guess_workflow()

    async def get(self, id: UUID) -> WorkflowContext:
        return await self.storage.get(id)
