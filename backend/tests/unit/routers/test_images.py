from ampf.base import BaseAsyncFactory
from ampf.testing import ApiTestClient
import pytest

from shared.images.image_service import ImageService
from tests.unit.conftest import ImageGenServiceMock

@pytest.mark.asyncio
async def test_get_images(factory: BaseAsyncFactory, client: ApiTestClient):
    # Given: A stored audio file
    service = ImageService(factory, ImageGenServiceMock())
    image_name = await service.generate_and_upload("Hello world!", "en")
    # When: Download the audio file
    ret = client.get(f"/api/images/{image_name}", 200)
    # Then: It is downloaded
    assert ret
    assert ret.headers["Content-Type"] == "image/png"

