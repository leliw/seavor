from dependencies import ImageServiceDep
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Images"])
ITEM_PATH = "/{name}"


@router.get(ITEM_PATH)
async def get(service: ImageServiceDep, name: str) -> StreamingResponse:
    blob = await service.download(name)
    return StreamingResponse(
        blob.data,
        headers={"Cache-Control": "public, max-age=86400, stale-while-revalidate=3600"},
        media_type=blob.content_type,
    )
