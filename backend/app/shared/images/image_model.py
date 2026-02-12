from typing import Optional
from ampf.base import Blob, BaseBlobMetadata


class ImageMetadata(BaseBlobMetadata):
    text: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None


ImageBlob = Blob[ImageMetadata]
