from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

class LetterShuffleSetTranslationHeader(BaseModel):
    id: UUID
    language: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

class LetterShuffleItemTranslation(BaseModel):
    question: str
    description: str
    question_audio_file_name: Optional[str] = None
    description_audio_file_name: Optional[str] = None


class LetterShuffleSetTranslationCreate(BaseModel):
    id: UUID
    language: str
    title: str
    description: str
    items: List[LetterShuffleItemTranslation]


class LetterShuffleSetTranslationUpdate(BaseModel):
    id: UUID
    language: str
    title: str
    description: str
    items: List[LetterShuffleItemTranslation]


class LetterShuffleSetTranslation(BaseModel):
    id: UUID
    language: str
    title: str
    description: str
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
        self.title = value.title
        self.description = value.description
        self.items = value.items
        self.updated_at = datetime.now()
