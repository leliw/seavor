from typing import Optional
from uuid import NAMESPACE_DNS, uuid5

from ampf.base import BaseAsyncFactory
from integrations.image_gen.base_image_gen_service import BaseImageGenService

from .image_model import ImageBlob, ImageMetadata


class ImageService:
    def __init__(self, factory: BaseAsyncFactory, image_gen_service: Optional[BaseImageGenService] = None):
        self.storage = factory.create_blob_storage("images", clazz=ImageMetadata)
        self.image_gen_service = image_gen_service

    async def upload(self, blob: ImageBlob) -> None:
        await self.storage.upload_async(blob)

    async def download(self, name: str) -> ImageBlob:
        return await self.storage.download_async(name)

    def delete(self, name: str):
        return self.storage.delete(name)

    async def generate_and_upload(self, text: str, language_code: str) -> str:
        if not self.image_gen_service:
            raise Exception("No image generation service")
        async for blob_create in self.image_gen_service.generate_async(text):
            name = uuid5(NAMESPACE_DNS, f"{language_code}-{text}").hex
            blob = ImageBlob(
                name=name,
                data=blob_create.data,
                metadata=ImageMetadata(text=text, language=language_code),
                content_type=blob_create.content_type,
            )
            await self.upload(blob)
            return name
        raise Exception("No images generated")
