from ampf.base import CollectionDef
from core.users.user_model import UserInDB
from features.repetitions.repetition_model import LanguageStatus, LevelStatus, RepetitionCard

# fmt: off
STORAGE_DEF = [
    CollectionDef("users", UserInDB, "username", subcollections=[
        CollectionDef("languages", LanguageStatus, subcollections=[
            CollectionDef("levels", LevelStatus, subcollections=[
                CollectionDef("repetitions", RepetitionCard, "id"),
            ]),
        ]),
    ])
]
# fmt: on
