from ampf.base import Blob
from pydantic import BaseModel


class AudioFileMetadata(BaseModel):
    text: str
    language: str


AudioFileBlob = Blob[AudioFileMetadata]
