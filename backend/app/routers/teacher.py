from dependencies import (
    Authorize,
    TeacherOrchestratorDep,
    TokenPayloadDep,
)
from fastapi import APIRouter, Depends
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate

router = APIRouter(tags=["Teacher features"], dependencies=[Depends(Authorize())])


@router.post("/definition-guess", status_code=201)
async def post(
    teacher_orchestrator: TeacherOrchestratorDep,
    token_payload: TokenPayloadDep,
    body: TeacherDefinitionGuessCreate,
) -> RepetitionCard:
    return await teacher_orchestrator.create_definition_guess_workflow(body, token_payload.sub)
