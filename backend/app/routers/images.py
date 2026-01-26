from ampf.fastapi import BlobStreamingResponse
from dependencies import ImageServiceDep
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from shared.images.image_optimizer import ImageOptimizerDep

router = APIRouter(tags=["Images"])
ITEM_PATH = "/{name}"


@router.get(f"{ITEM_PATH}/raw")
async def get_raw(service: ImageServiceDep, name: str) -> StreamingResponse:
    blob = await service.download(name)
    return BlobStreamingResponse(blob, "public, max-age=86400, stale-while-revalidate=3600")


@router.get(ITEM_PATH)
async def get(service: ImageServiceDep, optymizer: ImageOptimizerDep, name: str) -> StreamingResponse:
    blob = await service.download(name)
    return await optymizer.get_optimized_response(blob)
