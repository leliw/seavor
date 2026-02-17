import logging
from typing import AsyncIterator, Iterator

import httpx
from ampf.base import BlobCreate
from openai import AsyncOpenAI, OpenAI

from .base_image_gen_service import BaseImageGenService

_log = logging.getLogger(__name__)


class OpenAIImageGenService(BaseImageGenService):
    def __init__(self):
        self.client = OpenAI()
        self.async_openai = AsyncOpenAI()
        self.model = "dall-e-3"

    def generate(self, prompt: str) -> Iterator[BlobCreate]:
        result = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        if result.data and result.data[0].url:
            with httpx.Client() as client:
                response = client.get(result.data[0].url)

            yield BlobCreate.from_content(
                content_type=response.headers.get("Content-Type"),
                content=response.content,
            )

    async def generate_async(self, prompt: str) -> AsyncIterator[BlobCreate]:
        result = await self.async_openai.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        if result.data and result.data[0].url:
            async with httpx.AsyncClient() as client:
                response = await client.get(result.data[0].url)

            yield BlobCreate.from_content(
                content_type=response.headers.get("Content-Type"),
                content=response.content,
            )
