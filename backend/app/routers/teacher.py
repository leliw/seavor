import logging

from dependencies import (
    Authorize,
    TokenPayloadDep,
    WorkflowFactoryDep,
)
from fastapi import APIRouter, Depends
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate

_log = logging.getLogger(__name__)
router = APIRouter(tags=["Teacher features"], dependencies=[Depends(Authorize())])


@router.post("/definition-guess", status_code=201)
async def post(
    workflow_factory: WorkflowFactoryDep,
    token_payload: TokenPayloadDep,
    body: TeacherDefinitionGuessCreate,
) -> RepetitionCard:
    _log.debug("Payload: %s", body.model_dump())
    return await workflow_factory.create_definition_guess_workflow().execute(body, token_payload.sub)
