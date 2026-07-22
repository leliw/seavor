from ampf.base import Blob
from haintech.ai.prompts import ImageGeneratedMetadata


class ImageMetadata(ImageGeneratedMetadata):
    language: str | None = None
    text: str | None = None
    description: str | None = None


ImageBlob = Blob[ImageMetadata]
