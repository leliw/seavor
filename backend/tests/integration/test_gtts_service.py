import pytest
from app.integrations.gtts.gtts_service import GttsService


def test_gtts(tmp_path):
    # Given: A TTS service
    gtts_service = GttsService()
    # When: Converting text to speech
    ret = gtts_service.text_to_speech("Hello world!", "en")
    # Then: An audio stream is returned
    file = tmp_path / "test.mp3"
    with open(file, "wb") as f:
        f.write(ret.read())
    print(file)
    assert file.exists()

@pytest.mark.asyncio
async def test_gtts_async(tmp_path):
    # Given: A TTS service
    gtts_service = GttsService()
    # When: Converting text to speech
    ret = await gtts_service.text_to_speech_async("Hello world!", "en")
    # Then: An audio stream is returned
    file = tmp_path / "test_async.mp3"
    with open(file, "wb") as f:
        f.write(ret.read())
    print(file)
    assert file.exists()