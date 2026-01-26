
from ampf.fastapi import BlobStreamingResponse
from dependencies import AudioFileServiceDep
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Audio files"])
ITEM_PATH = "/{name}"


@router.get(ITEM_PATH)
async def get(service: AudioFileServiceDep, name: str) -> StreamingResponse:
    blob = await service.download(name)

    return BlobStreamingResponse(blob, "public, max-age=86400, stale-while-revalidate=3600")
