from datetime import datetime
from typing import List, Optional
from uuid import UUID

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel


class LetterShuffleSetTranslationHeader(BaseModel):
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


class LetterShuffleItemTranslation(BaseModel):
    target_phrase: str
    target_description: str
    target_phrase_audio_file_name: Optional[str] = None
    target_description_audio_file_name: Optional[str] = None
    native_phrase: str
    native_description: str
    native_phrase_audio_file_name: Optional[str] = None
    native_description_audio_file_name: Optional[str] = None
    phrase_image_name: Optional[str] = None


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
    image_name: Optional[str] = None


class LetterShuffleSetTranslationUpdate(BaseModel):
    native_title: str
    native_description: str
    items: List[LetterShuffleItemTranslation]
    image_name: Optional[str] = None


class LetterShuffleSetTranslationPatch(BaseModel):
    levels: Optional[List[Level]] = None
    target_title: Optional[str] = None
    target_description: Optional[str] = None
    native_title: Optional[str] = None
    native_description: Optional[str] = None
    image_name: Optional[str] = None


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
    image_name: Optional[str] = None

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
        self.image_name = value.image_name
        self.updated_at = datetime.now()

    def patch(self, patch_value: LetterShuffleSetTranslationPatch) -> None:
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict)
        self.updated_at = datetime.now()
