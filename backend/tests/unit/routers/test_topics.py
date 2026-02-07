from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
)
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
)
from features.levels import Level
from features.topics.topic_model import Topic

from tests.unit.routers.test_letter_shuffles import letter_shuffle_set


@pytest.fixture()
def id(client: ApiTestClient) -> UUID:
    value = LetterShuffleSet.create(letter_shuffle_set)
    p = client.post_typed("/api/target-languages/en/letter-shuffles", 200, LetterShuffleSet, json=value)
    return p.id


@pytest.fixture()
def endpoint(client: ApiTestClient, id) -> str:
    return f"/api/target-languages/en/letter-shuffles/{id}/translations"


def test_post_get_put_patch_delete(client: ApiTestClient, id: UUID, endpoint: str):
    # Given: A set translation
    value = LetterShuffleSetTranslation.create(
        LetterShuffleSetTranslationCreate(
            id=id,
            target_language_code=Language.EN,
            target_title="Christmas",
            target_description="Words and phrases related to Christmas",
            native_language_code=Language.PL,
            native_title="Boże Narodzenie",
            native_description="Słowa i wyrażenia związane z Bożym Narodzeniem",
            items=[
                LetterShuffleItemTranslation(
                    target_phrase="Carols",
                    target_description="Traditional Christmas songs sung during the festive season.",
                    native_phrase="Kolenda",
                    native_description="Tradycyjna pieśń spiewana w okresie Bożego Narodzenia.",
                ),
            ],
        )
    )

    # When: The set transaltion is saved
    client.post_typed(endpoint, 200, LetterShuffleSetTranslation, json=value)
    # Then: Topics are stored
    for level in list(Level):
        r = client.get_typed_list(f"/api/topics/en/{level}/pl", 200, Topic)
        assert 1 == len(r)
        assert r[0].target_title == value.target_title
        assert r[0].native_title == value.native_title
        assert r[0].level == level
        assert r[0].native_language_code == value.native_language_code
        assert r[0].target_language_code == value.target_language_code