from abc import ABC, abstractmethod
from io import BytesIO


class BaseTTSService(ABC):
    @abstractmethod
    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        pass
