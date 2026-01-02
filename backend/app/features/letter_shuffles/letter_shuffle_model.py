from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class LetterShuffleSetHeader(BaseModel):
    id: UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime


class LetterShuffleItem(BaseModel):
    question: str
    description: str
    question_audio_file_name: Optional[str] = None
    description_audio_file_name: Optional[str] = None


class LetterShuffleSetCreate(BaseModel):
    title: str
    description: str
    items: List[LetterShuffleItem]


class LetterShuffleSetUpdate(BaseModel):
    title: str
    description: str
    items: List[LetterShuffleItem]


class LetterShuffleSetPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class LetterShuffleSet(BaseModel):
    id: UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    items: List[LetterShuffleItem]

    @classmethod
    def create(cls, value: LetterShuffleSetCreate) -> "LetterShuffleSet":
        return cls(
            id=uuid4(),
            **value.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def update(self, value: LetterShuffleSetUpdate) -> None:
        self.title = value.title
        self.description = value.description
        self.items = value.items
        self.updated_at = datetime.now()

    def patch(self, patch_value: LetterShuffleSetPatch) -> None:
        patch_dict = patch_value.model_dump(exclude_unset=True, exclude_none=True)
        self.__dict__.update(patch_dict)
