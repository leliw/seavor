from ampf.base import Blob
from shared.prompts.prompt_executor_image import ImageGeneratedMetadata


class ImageMetadata(ImageGeneratedMetadata):
    language: str | None = None
    text: str | None = None
    description: str | None = None


ImageBlob = Blob[ImageMetadata]
