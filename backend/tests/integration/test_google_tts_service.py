import pytest
from integrations.tts.google_tts_service import GoogleTTSService


@pytest.mark.asyncio
async def test_gtts_async(tmp_path):
    # Given: A TTS service
    gtts_service = GoogleTTSService()
    # When: Converting text to speech
    ret = await gtts_service.text_to_speech_async("Hello world!", "en")
    # Then: An audio stream is returned
    file = tmp_path / "test_async.mp3"
    with open(file, "wb") as f:
        f.write(ret.read())
    assert file.exists()
