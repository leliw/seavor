import asyncio
from ampf.base import BaseAsyncFactory, Blob
from ampf.testing import ApiTestClient
import pytest

from shared.images.image_model import ImageMetadata
from shared.images.image_service import ImageService
from tests.unit.conftest import ImageGenServiceMock


@pytest.mark.asyncio
async def test_get_images_raw(factory: BaseAsyncFactory, client: ApiTestClient):
    # Given: A stored image file
    service = ImageService(factory, ImageGenServiceMock())
    image_name = await service.generate_and_upload("Hello world!", "en")
    # When: Download the image file
    ret = client.get(f"/api/images/{image_name}/raw", 200)
    # Then: It is downloaded
    assert ret
    assert ret.headers["Content-Type"] == "image/png"


@pytest.mark.asyncio
async def test_get_images(factory: BaseAsyncFactory, client: ApiTestClient):
    # Given: A stored image file
    service = ImageService(factory, ImageGenServiceMock())
    f = await asyncio.to_thread(open, "./tests/data/blobs/test.png", "rb")
    src_image = Blob(name="test.png", data=f, metadata=ImageMetadata(text="Hello world!", language="en"))
    await service.upload(src_image)
    # When: Download the image file
    ret = client.get("/api/images/test.png", 200)
    # Then: It is downloaded
    assert ret
    assert ret.headers["Content-Type"] == "image/webp"
