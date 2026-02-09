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


class LetterShuffleItemTranslationPatch(BaseModel):
    target_phrase: str
    target_description: Optional[str] = None
    target_phrase_audio_file_name: Optional[str] = None
    target_description_audio_file_name: Optional[str] = None
    native_phrase: Optional[str] = None
    native_description: Optional[str] = None
    native_phrase_audio_file_name: Optional[str] = None
    native_description_audio_file_name: Optional[str] = None
    phrase_image_name: Optional[str] = None


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

    @classmethod
    def from_patch(cls, patch_value: LetterShuffleItemTranslationPatch) -> "LetterShuffleItemTranslation":
        return cls(
            **patch_value.model_dump(),
        )

    def patch(self, patch_value: LetterShuffleItemTranslationPatch) -> None:
        if self.target_phrase != patch_value.target_phrase:
            raise ValueError("Target phrase mismatch")
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict)


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
    items: Optional[List[LetterShuffleItemTranslationPatch]] = None
    image_name: Optional[str] = None
    deleted_items: Optional[List[str]] = None


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
        item_patches = patch_value.items.copy() if patch_value.items else None
        deleted_items = patch_value.deleted_items or  []
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        if item_patches or patch_value.deleted_items:
            existing_items_map = {item.target_phrase: item for item in self.items}
            new_items_list = []
            for phrase_to_delete in deleted_items:
                existing_items_map.pop(phrase_to_delete, None) # Użyj .pop(key, None) aby uniknąć błędu jeśli klucz nie istnieje
            if item_patches:
                for item_patch in item_patches:
                    if item_patch.target_phrase in existing_items_map:
                        item_to_patch = existing_items_map.pop(item_patch.target_phrase)
                        item_to_patch.patch(item_patch)
                        new_items_list.append(item_to_patch)
                    else:
                        new_items_list.append(LetterShuffleItemTranslation.from_patch(item_patch))
            new_items_list.extend(existing_items_map.values())
            patch_dict["items"] = new_items_list
        self.__dict__.update(patch_dict)
        self.updated_at = datetime.now()
