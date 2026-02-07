from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from features.languages import Language

from .letter_shuffle_model import LetterShuffleItem, LetterShuffleSetHeader
from features.levels import Level



class LetterShuffleSetTranslationHeader(LetterShuffleSetHeader):
    native_language_code: Language
    native_title: str
    native_description: str


class LetterShuffleItemTranslation(LetterShuffleItem):
    native_phrase: str
    native_description: str
    native_phrase_audio_file_name: Optional[str] = None
    native_description_audio_file_name: Optional[str] = None


class LetterShuffleSetTranslationCreate(BaseModel):
    id: UUID
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    native_language_code: Language
    native_title: str
    native_description: str
    items: List[LetterShuffleItemTranslation]


class LetterShuffleSetTranslationUpdate(BaseModel):
    native_title: str
    native_description: str
    items: List[LetterShuffleItemTranslation]



class LetterShuffleSetTranslation(BaseModel):
    id: UUID
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    native_language_code: Language
    native_title: str
    native_description: str
    created_at: datetime
    updated_at: datetime
    items: List[LetterShuffleItemTranslation]

    @classmethod
    def create(cls, value: LetterShuffleSetTranslationCreate) -> "LetterShuffleSetTranslation":
        return cls(
            **value.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def update(self, value: LetterShuffleSetTranslationUpdate) -> None:
        self.native_title = value.native_title
        self.native_description = value.native_description
        self.items = value.items
        self.updated_at = datetime.now()
