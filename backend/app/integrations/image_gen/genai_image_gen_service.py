import logging
import os
from typing import AsyncGenerator, Generator

from ampf.base import BlobCreate
from google import genai
from google.genai import types

from .base_image_gen_service import BaseImageGenService

_log = logging.getLogger(__name__)


class GenAIImageGenService(BaseImageGenService):
    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ.get("GOOGLE_API_KEY"),
        )
        self.model = "gemini-2.5-flash-image"

    def generate(self, prompt: str) -> Generator[BlobCreate]:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="1:1")
        )
        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            if chunk.candidates[0].content.parts[0].inline_data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                if inline_data.data:
                    yield BlobCreate(
                        name=inline_data.display_name,
                        content_type=inline_data.mime_type,
                        data=inline_data.data,
                    )
                else:
                    _log.warning("No binary data!?")
            else:
                _log.info(chunk.text)

    async def generate_async(self, prompt: str) -> AsyncGenerator[BlobCreate]:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="1:1")
        )
        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue
            if chunk.candidates[0].content.parts[0].inline_data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                if inline_data.data:
                    yield BlobCreate(
                        name=inline_data.display_name,
                        content_type=inline_data.mime_type,
                        data=inline_data.data,
                    )
                else:
                    _log.warning("No binary data!?")
            else:
                _log.info(chunk.text)
