from ampf.base import BaseAsyncFactory
from ampf.testing import ApiTestClient
import pytest

from shared.audio_files.audio_file_service import AudioFileService
from tests.unit.conftest import TtsServiceMock

@pytest.mark.asyncio
async def test_get_audio_file(factory: BaseAsyncFactory, client: ApiTestClient):
    # Given: A stored audio file
    service = AudioFileService(factory, TtsServiceMock())
    audio_file_name = await service.generate_and_upload("Hello world!", "en")
    # When: Download the audio file
    ret = client.get(f"/api/audio-files/{audio_file_name}", 200)
    # Then: It is downloaded
    assert ret
    assert ret.headers["Content-Type"] == "audio/mpeg"

