from ampf.base import CollectionDef
from core.user_settings.user_settings_model import UserSettings
from core.users.user_model import UserInDB
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.native_pages.native_page_model import NativePage
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_model import Page
from features.repetitions.repetition_model import LanguageStatus, LevelStatus, RepetitionCard
from features.topics.topic_model import Topic

# fmt: off
STORAGE_DEF = [
    CollectionDef("target-languages", LanguageStatus, subcollections=[
        CollectionDef("letter-shuffles", LetterShuffleSet, subcollections=[
            CollectionDef("native-languages", LetterShuffleSetTranslation, key="native_language_code")
        ]),
        CollectionDef("levels", LevelStatus, subcollections=[
            CollectionDef("topics", Topic, subcollections=[
                CollectionDef("pages", Page, "id")
            ]),
            CollectionDef("native-languages", LanguageStatus, subcollections=[
                CollectionDef("topics", NativeTopic, subcollections=[
                    CollectionDef("pages", NativePage, "id")
                ])
            ])
        ])
    ]),          
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
