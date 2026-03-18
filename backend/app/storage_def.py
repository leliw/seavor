from ampf.base import CollectionDef
from core.user_settings.user_settings_model import UserSettings
from core.users.user_model import UserInDB
from features.repetitions.repetition_model import LanguageStatus, LevelStatus, RepetitionCard

# fmt: off
STORAGE_DEF = [
    CollectionDef("users", UserInDB, "username", subcollections=[
        CollectionDef("settings", UserSettings, key="id"),
        CollectionDef("languages", LanguageStatus, subcollections=[
            CollectionDef("levels", LevelStatus, subcollections=[
                CollectionDef("repetitions", RepetitionCard, "id"),
            ]),
        ]),
    ])
]
# fmt: on
