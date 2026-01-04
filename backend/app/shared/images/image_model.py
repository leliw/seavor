from typing import Optional
from ampf.base import Blob
from pydantic import BaseModel


class ImageMetadata(BaseModel):
    text: str
    description: Optional[str] = None
    language: Optional[str] = None


ImageBlob = Blob[ImageMetadata]
