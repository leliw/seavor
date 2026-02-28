from enum import StrEnum


class Level(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    ALL = "all"

    def to_list(self) -> list["Level"]:
        if self != Level.ALL:
            return [self]
        else:
            return [level for level in Level if level != Level.ALL]
