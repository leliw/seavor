from io import BytesIO
from typing import Optional

from ampf.base import Blob, BlobData
from pydantic import BaseModel


class AudioFileMetadata(BaseModel):
    text: str
    language: str


class AudioFileBlob(Blob[AudioFileMetadata]):
    def __init__(self, name: str, data: BlobData, metadata: Optional[AudioFileMetadata] = None):
        if isinstance(data, BytesIO):
            data = data.read()
        super().__init__(name=name, data=data, content_type="audio/mpeg", metadata=metadata)
