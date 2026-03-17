
from ampf.fastapi import JsonStreamingResponse
from dependencies import RepetitionServiceDep
from fastapi import APIRouter
from features.repetitions.repetition_model import RepetitionCardHeader

router = APIRouter(tags=["Repetitions"])
ITEM_PATH = "/{id}"


@router.get("")
async def get_all(service: RepetitionServiceDep) -> list[RepetitionCardHeader]:
    return JsonStreamingResponse(service.get_all())  # type: ignore
