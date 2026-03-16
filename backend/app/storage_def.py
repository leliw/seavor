from ampf.base import CollectionDef
from pydantic import BaseModel
from core.users.user_model import UserInDB
from features.languages import Language
from features.levels import Level
from features.repetitions.repetition_model import RepetitionStatus

class LanguageStatus(BaseModel):
    language: Language

class LevelStatus(BaseModel):
    level: Level

# fmt: off
STORAGE_DEF = [
    CollectionDef("users", UserInDB, "username", subcollections=[
        CollectionDef("languages", LanguageStatus, subcollections=[
            CollectionDef("levels", LevelStatus, subcollections=[
                CollectionDef("repetitions", RepetitionStatus, "id"),
            ]),
        ]),
    ])
]
# fmt: on
