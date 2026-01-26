from ampf.base import BaseBlobMetadata, Blob


class AudioFileMetadata(BaseBlobMetadata):
    text: str
    language: str


AudioFileBlob = Blob[AudioFileMetadata]
