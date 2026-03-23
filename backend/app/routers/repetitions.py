
from ampf.fastapi import JsonStreamingResponse
from dependencies import RepetitionServiceDep
from fastapi import APIRouter
from features.repetitions.repetition_model import RepetitionCardHeader, RepetitionSchedule

router = APIRouter(tags=["Repetitions"])
ITEM_PATH = "/{id}"


@router.get("")
async def get_all(service: RepetitionServiceDep) -> list[RepetitionCardHeader]:
    return JsonStreamingResponse(service.get_all())  # type: ignore

@router.get("/schedule")
async def get_schedule(service: RepetitionServiceDep) -> RepetitionSchedule:
    return await service.get_schedule()
