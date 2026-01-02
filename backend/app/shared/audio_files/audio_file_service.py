from uuid import NAMESPACE_DNS, uuid5

from ampf.base import BaseAsyncFactory
from integrations.gtts.gtts_service import GttsService
from shared.audio_files.audio_file_model import AudioFileBlob, AudioFileMetadata


class AudioFileService:
    def __init__(self, factory: BaseAsyncFactory, tts_service: GttsService):
        self.storage = factory.create_blob_storage("audio-files", clazz=AudioFileMetadata, content_type="audio/mpeg")
        self.tts_service = tts_service

    async def upload(self, blob: AudioFileBlob) -> None:
        await self.storage.upload_async(blob)

    async def download(self, name: str) -> AudioFileBlob:
        return await self.storage.download_async(name)

    def delete(self, name: str):
        return self.storage.delete(name)

    async def generate_and_upload(self, text: str, language: str) -> str:
        audio = await self.tts_service.text_to_speech_async(text, language)
        name = uuid5(NAMESPACE_DNS, f"{language}-{text}").hex
        blob = AudioFileBlob(
            name=name, data=audio, metadata=AudioFileMetadata(text=text, language=language), content_type="audio/mpeg"
        )
        await self.upload(blob)
        return name
