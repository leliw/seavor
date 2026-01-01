import pytest
from ampf.base import BaseAsyncFactory
from ampf.in_memory import InMemoryAsyncFactory
from shared.audio_files.audio_file_servce import AudioFileService


@pytest.fixture
def factory():
    return InMemoryAsyncFactory()


@pytest.mark.asyncio
async def test_generate(factory: BaseAsyncFactory):
    # Given: A service instance
    service = AudioFileService(factory)
    # When: Generate audio file
    blob_location = await service.generate_and_upload("Hello world!", "en")
    # Then: Audio file is generated and uploaded
    blob = await service.download(blob_location.name)
    assert blob
    assert blob.name == blob_location.name
    assert blob.metadata
    assert blob.metadata.text == "Hello world!"
    assert blob.metadata.language == "en"
