from typing import Optional
from ampf.base import BaseBlobMetadata, Blob


class AudioFileMetadata(BaseBlobMetadata):
    text: Optional[str] = None
    language: Optional[str] = None


AudioFileBlob = Blob[AudioFileMetadata]
