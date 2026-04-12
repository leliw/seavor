from dependencies import (
    Authorize,
    TokenPayloadDep,
    WorkflowFactoryDep,
)
from fastapi import APIRouter, Depends
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate

router = APIRouter(tags=["Teacher features"], dependencies=[Depends(Authorize())])


@router.post("/definition-guess", status_code=201)
async def post(
    workflow_factory: WorkflowFactoryDep,
    token_payload: TokenPayloadDep,
    body: TeacherDefinitionGuessCreate,
) -> RepetitionCard:
    return await workflow_factory.create_definition_guess_workflow().execute(body, token_payload.sub)
