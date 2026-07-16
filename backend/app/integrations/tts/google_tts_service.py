from io import BytesIO

from google.api_core.client_options import ClientOptions
from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SsmlVoiceGender,
    SynthesisInput,
    TextToSpeechAsyncClient,
    VoiceSelectionParams,
)

from .base_tts_service import BaseTTSService


class GoogleTTSService(BaseTTSService):
    def __init__(self):
        self.client = TextToSpeechAsyncClient(client_options=ClientOptions())

    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        synthesis_input = SynthesisInput(text=text)
        voice = VoiceSelectionParams(language_code=lang, ssml_gender=SsmlVoiceGender.NEUTRAL)
        audio_config = AudioConfig(audio_encoding=AudioEncoding.MP3)
        response = await self.client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        return BytesIO(response.audio_content)
