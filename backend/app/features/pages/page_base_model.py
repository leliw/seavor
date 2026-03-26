from datetime import datetime
from enum import StrEnum
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


class BasePage_v1(BaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    target_language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this
    created_at: datetime
    updated_at: datetime


class BasePage_v2(VersionedBaseModel):
    """Common fields for ALL page types"""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    language: Language
    level: Level
    order: int
    type: PageType  # literal below will override this
    created_at: datetime
    updated_at: datetime


BasePage = BasePage_v2
