from datetime import datetime
from uuid import uuid4

import pytest
from features.languages import Language
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleItemTranslationPatch,
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationPatch,
)

@pytest.fixture()
def letter_shuffle_set_translation() -> LetterShuffleSetTranslation:
    return LetterShuffleSetTranslation(
        id=uuid4(),
        target_language_code=Language.EN,
        target_title="test",
        target_description="test",
        native_language_code=Language.PL,
        native_title="test",
        native_description="test",
        items=[
            LetterShuffleItemTranslation(
                target_phrase="test1",
                target_description="test1",
                native_phrase="test1",
                native_description="test1",
            ),
            LetterShuffleItemTranslation(
                target_phrase="test2",
                target_description="test2",
                native_phrase="test2",
                native_description="test2",
            ),
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_path_modify_item(letter_shuffle_set_translation: LetterShuffleSetTranslation):
    # Given: A letter shuffle set translation with two items
    assert letter_shuffle_set_translation
    # And: A path with an existing item
    patch = LetterShuffleSetTranslationPatch(
        items=[
            LetterShuffleItemTranslationPatch(target_phrase="test1", phrase_image_name="test"),
        ]
    )
    # When: The translation is patched
    letter_shuffle_set_translation.patch(patch)
    # Then: The item is patched
    assert len(letter_shuffle_set_translation.items) == 2
    assert letter_shuffle_set_translation.items[0].phrase_image_name == "test"


def test_path_add_item(letter_shuffle_set_translation: LetterShuffleSetTranslation):
    # Given: A letter shuffle set translation with two items
    assert letter_shuffle_set_translation
    # And: A path with an existing item
    patch = LetterShuffleSetTranslationPatch(
        items=[
            LetterShuffleItemTranslationPatch(
                target_phrase="test3",
                target_description="test3",
                native_phrase="test3",
                native_description="test3",
                phrase_image_name="test3",
            ),
        ]
    )
    # When: The translation is patched
    letter_shuffle_set_translation.patch(patch)
    # Then: The item is patched
    assert len(letter_shuffle_set_translation.items) == 3
    assert any(item.target_phrase == "test3" for item in letter_shuffle_set_translation.items)


def test_path_delete_item(letter_shuffle_set_translation: LetterShuffleSetTranslation):
    # Given: A letter shuffle set translation with two items
    assert letter_shuffle_set_translation
    # And: A path with an existing item
    patch = LetterShuffleSetTranslationPatch(deleted_items=["test2"])
    # When: The translation is patched
    letter_shuffle_set_translation.patch(patch)
    # Then: The item is patched
    assert len(letter_shuffle_set_translation.items) == 1
    assert any(item.target_phrase == "test1" for item in letter_shuffle_set_translation.items)
