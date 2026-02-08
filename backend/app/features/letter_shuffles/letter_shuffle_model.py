from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from features.languages import Language
from features.levels import Level
from pydantic import BaseModel

from .letter_shuffle_translation_model import LetterShuffleSetTranslationPatch


class LetterShuffleSetHeader(BaseModel):
    id: UUID
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    created_at: datetime
    updated_at: datetime


class LetterShuffleItem(BaseModel):
    target_phrase: str
    target_description: str
    target_phrase_audio_file_name: Optional[str] = None
    target_description_audio_file_name: Optional[str] = None
    phrase_image_name: Optional[str] = None


class LetterShuffleSetCreate(BaseModel):
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    items: List[LetterShuffleItem]
    image_name: Optional[str] = None


class LetterShuffleSetUpdate(BaseModel):
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    items: List[LetterShuffleItem]
    image_name: Optional[str] = None


class LetterShuffleSetPatch(BaseModel):
    levels: Optional[List[Level]] = None
    target_title: Optional[str] = None
    target_description: Optional[str] = None
    image_name: Optional[str] = None

    def to_translation_patch(self) -> "LetterShuffleSetTranslationPatch":
        return LetterShuffleSetTranslationPatch(
            levels=self.levels,
            target_title=self.target_title,
            target_description=self.target_description,
            image_name=self.image_name,
        )


class LetterShuffleSet(BaseModel):
    id: UUID
    target_language_code: Language
    levels: Optional[List[Level]] = None
    target_title: str
    target_description: str
    created_at: datetime
    updated_at: datetime
    items: List[LetterShuffleItem]
    image_name: Optional[str] = None

    @classmethod
    def create(cls, value: LetterShuffleSetCreate) -> "LetterShuffleSet":
        return cls(
            id=uuid4(),
            **value.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def update(self, value: LetterShuffleSetUpdate) -> None:
        self.levels = value.levels
        self.target_title = value.target_title
        self.target_description = value.target_description
        self.items = value.items
        self.image_name = value.image_name
        self.updated_at = datetime.now()

    def patch(self, patch_value: LetterShuffleSetPatch) -> None:
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict)
