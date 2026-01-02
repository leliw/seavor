import pytest
from ampf.base import BaseAsyncFactory
from ampf.in_memory import InMemoryAsyncFactory
from integrations.gtts.gtts_service import GttsService
from shared.audio_files.audio_file_service import AudioFileService


@pytest.fixture
def factory():
    return InMemoryAsyncFactory()


@pytest.mark.asyncio
async def test_generate(factory: BaseAsyncFactory):
    # Given: A service instance
    service = AudioFileService(factory, GttsService())
    # When: Generate audio file
    audio_file_name = await service.generate_and_upload("Hello world!", "en")
    # Then: Audio file is generated and uploaded
    blob = await service.download(audio_file_name)
    assert blob
    assert blob.name == audio_file_name
    assert blob.metadata
    assert blob.metadata.text == "Hello world!"
    assert blob.metadata.language == "en"
