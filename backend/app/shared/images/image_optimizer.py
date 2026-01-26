import io
import asyncio
from typing import Annotated, Optional

from ampf.base import Blob
from fastapi import Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pyvips import Image

ALLOWED_FORMATS = {"webp", "avif", "jpeg", "png"}


class ImageOptimizer:
    def __init__(self, width: Optional[int] = None, height: Optional[int] = None, quality: int = 75, fmt: str = "webp"):
        self.width = width
        self.height = height
        self.quality = quality
        self.fmt = fmt
        if fmt not in ALLOWED_FORMATS:
            raise HTTPException(400, detail=f"Format must be one of: {', '.join(ALLOWED_FORMATS)}")

    async def get_optimized_response(self, blob: Blob) -> StreamingResponse:
        image: Image = Image.new_from_buffer(blob.content, "")  # type: ignore
        w = self.width
        h = self.height
        q = self.quality
        fmt = self.fmt

        if w and h:
            image = await asyncio.to_thread(image.thumbnail_image, w, height=h, crop=True)  # type: ignore
        elif w:
            image = await asyncio.to_thread(image.resize, w / image.width)  # type: ignore
        elif h:
            image = await asyncio.to_thread(image.resize, h / image.height)  # type: ignore

        output = io.BytesIO()

        save_options = {
            "Q": q,  # quality
            "strip": True,  # remove metadata (EXIF itp.)
        }
        if fmt == "webp":
            buffer = await asyncio.to_thread(image.write_to_buffer, ".webp", **save_options, effort=6)  # effort=6 → max compression
            content_type = "image/webp"
        elif fmt == "avif":
            buffer = await asyncio.to_thread(image.write_to_buffer,".avif", **save_options)
            content_type = "image/avif"
        elif fmt == "jpeg":
            buffer = await asyncio.to_thread(image.write_to_buffer, ".jpg", **save_options, optimize_coding=True)
            content_type = "image/jpeg"
        else:  # png
            save_options.pop("Q")
            save_options["compression"] = 6
            buffer = await asyncio.to_thread(image.write_to_buffer,".png", **save_options)
            content_type = "image/png"

        output.write(buffer)  # type: ignore
        output.seek(0)

        return StreamingResponse(
            output,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=31536000, immutable", "Vary": "Accept, Accept-Encoding"},
        )


def get_image_optimizer(
    w: Optional[int] = Query(None, alias="width", ge=100, le=2000),
    h: Optional[int] = Query(None, alias="height", ge=100, le=2000),
    q: int = Query(75, alias="quality", ge=30, le=95),
    fmt: str = Query("webp", alias="format"),
) -> ImageOptimizer:
    return ImageOptimizer(w, h, q, fmt)


ImageOptimizerDep = Annotated[ImageOptimizer, Depends(get_image_optimizer)]
