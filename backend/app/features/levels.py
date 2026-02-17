from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator


class Level(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class LevelRange(BaseModel):
    min_level: Level = Field(..., examples=["A1", "A2"])
    max_level: Level = Field(..., examples=["B2", "C1"])

    @model_validator(mode="after")
    def check_min_le_max(self) -> Self:
        if self.min_level > self.max_level:
            raise ValueError("min_level must be <= max_level")
        return self

    @classmethod
    def from_str(cls, s: str) -> Self:
        """Quick helper: 'B1-C2' → LevelRange"""
        if "-" not in s:
            level = Level(s.strip().upper())
            return cls(min_level=level, max_level=level)
        min_s, max_s = s.split("-", 1)
        return cls(
            min_level=Level(min_s.strip().upper()),
            max_level=Level(max_s.strip().upper()),
        )
