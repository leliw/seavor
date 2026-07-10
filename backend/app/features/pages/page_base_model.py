from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from ampf.base import VersionedBaseModel
from features.languages import Language
from features.levels import Level
from pydantic import BaseModel, ConfigDict


class PageType(StrEnum):
    LETTER_SHUFFLE = "letter-shuffle"
    GAP_FILL_CHOICE = "gap-fill-choice"
    DEFINITION_GUESS = "definition-guess"
    INFO = "info"


class PageHeader(BaseModel):
    id: UUID
    order: int
    type: PageType
    created_at: datetime
    updated_at: datetime


class BasePageCreate(BaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    language: Language
    level: Level
    order: int = 0
    type: PageType  # literal below will override this

    def model_post_init(self, __context):
        self.__pydantic_fields_set__.add("type")


class BasePage(VersionedBaseModel, ABC):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    language: Language
    level: Level
    order: int
    type: PageType  # subclasses will override this
    created_at: datetime
    updated_at: datetime

    def model_post_init(self, __context):
        """Enforce default type value as sent by user (for patch() methods)"""
        super().model_post_init(__context)
        self.__pydantic_fields_set__.add("type")

    @abstractmethod
    def get_audio_file_names(self) -> set[str]:
        """Returns all audio file names used in the page"""
        pass

    @abstractmethod
    def get_image_file_names(self) -> set[str]:
        """Returns all image file names used in the page"""
        pass

    @classmethod
    def from_storage(cls, data: dict[str, Any]):
        """Convert the data from storage format to the model instance.

        Args:
            data: The data to convert.
        Returns:
            The converted data.
        """
        return cls.model_validate(data)

    def to_storage(self) -> dict[str, Any]:
        """Convert the data to storage format.

        Returns:
            The converted data.
        """
        return self.model_dump(by_alias=True, exclude_none=True)
