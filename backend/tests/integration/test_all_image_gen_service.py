import pytest
from integrations.image_gen.base_image_gen_service import BaseImageGenService
from integrations.image_gen.openai_image_gen_service import OpenAIImageGenService
from integrations.image_gen.genai_image_gen_service import GenAIImageGenService


@pytest.fixture(scope="module", params=[OpenAIImageGenService, GenAIImageGenService])
def service(request) -> BaseImageGenService:
    return request.param()


def test_generate(service: BaseImageGenService):
    blob_create = next(service.generate("Big black dog."))

    assert blob_create.metadata
    assert blob_create.metadata.content_type
    assert blob_create.content


@pytest.mark.asyncio
async def test_generate_async(service: BaseImageGenService):
    async for blob_create in service.generate_async("Big black dog."):
        assert blob_create.metadata
        assert blob_create.metadata.content_type
        assert blob_create.content
