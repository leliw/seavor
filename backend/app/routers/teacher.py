import logging
from uuid import UUID

from ampf.tasks import TaskHeader, TaskRegistry
from dependencies import (
    Authorize,
    TaskRunnerDep,
    TokenPayloadDep,
    WorkflowFactoryDep,
)
from fastapi import APIRouter, Depends
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.workflows.definition_guess_workflow import DefinitionGuessWorkflowContext
from features.workflows.workflow_factory import WorkflowFactory

_log = logging.getLogger(__name__)
router = APIRouter(tags=["Teacher features"], dependencies=[Depends(Authorize())])


@TaskRegistry.register("teacher", DefinitionGuessWorkflowContext)
async def processor(workflow_factory: WorkflowFactory, payload: DefinitionGuessWorkflowContext) -> None:
    workflow = workflow_factory.create_for_context(payload)
    await workflow.run(payload.id)


@router.post("/definition-guess", status_code=202)
async def post(
    workflow_factory: WorkflowFactoryDep,
    task_runner: TaskRunnerDep,
    token_payload: TokenPayloadDep,
    body: TeacherDefinitionGuessCreate,
) -> TaskHeader:
    _log.debug("Payload: %s", body.model_dump())
    ctx = await workflow_factory.create_definition_guess_workflow(task_runner).create(body, token_payload.sub)
    await task_runner.run_async("teacher", ctx)
    return TaskHeader.from_task(ctx)


@router.get("/{id}")
async def get(workflow_factory: WorkflowFactoryDep, token_payload: TokenPayloadDep, id: UUID) -> TaskHeader:
    task = await workflow_factory.get(id)
    return TaskHeader.from_task(task)
