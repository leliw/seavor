from ampf.base import CollectionDef, StorageFormatFlags
from core.feature_flags import FeatureFlags
from core.user_settings.user_settings_model import UserSettings
from core.users.user_model import UserInDB
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.native_pages.native_page_model import NativeGapFillChoiceExercise_v2, NativeInfoPage_v2, NativePage
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_model import GapFillChoiceExercise_v2, InfoPage_v2, Page
from features.repetitions.repetition_model import LanguageStatus, LevelStatus, RepetitionCard
from features.topics.topic_model import Topic, Topic_v2

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

def set_storage_formats(feature_flags: FeatureFlags):
    Topic_v2.FORMAT_FLAGS = StorageFormatFlags(
        save_new_format=feature_flags.topic_v2_storage,
        migrate_legacy_on_read=feature_flags.topic_v2_migrate,
    )
    page_sff = StorageFormatFlags(
        save_new_format=feature_flags.page_v2_storage,
        migrate_legacy_on_read=feature_flags.page_v2_migrate,
    )
    InfoPage_v2.FORMAT_FLAGS = page_sff
    NativeInfoPage_v2.FORMAT_FLAGS = page_sff
    GapFillChoiceExercise_v2.FORMAT_FLAGS = page_sff
    NativeGapFillChoiceExercise_v2.FORMAT_FLAGS = page_sff
