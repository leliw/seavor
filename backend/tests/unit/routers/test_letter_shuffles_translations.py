from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
    LetterShuffleSetPatch,
)
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
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
def endpoint(client: ApiTestClient, id: UUID) -> str:
    return f"/api/target-languages/en/letter-shuffles/{id}"

@pytest.fixture()
def letter_shuffle_set_translation(id: UUID) -> LetterShuffleSetTranslation:
    return LetterShuffleSetTranslation.create(
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


def test_get_all(client: ApiTestClient, endpoint: str):
    r = client.get_typed_list(f"{endpoint}/translations", 200, LetterShuffleSetTranslationHeader)
    assert 0 == len(r)


def test_post_get_put_patch_delete(client: ApiTestClient, endpoint: str, letter_shuffle_set_translation: LetterShuffleSetTranslation):

    # POST
    p = client.post_typed(f"{endpoint}/translations", 200, LetterShuffleSetTranslation, json=letter_shuffle_set_translation)

    # GET ALL
    r = client.get_typed_list(f"{endpoint}/translations", 200, LetterShuffleSetTranslationHeader)
    assert 1 == len(r)
    assert r[0].target_title == letter_shuffle_set_translation.target_title
    assert r[0].native_title == letter_shuffle_set_translation.native_title

    # GET
    r = client.get_typed(f"{endpoint}/translations/pl", 200, LetterShuffleSetTranslation)
    assert r.target_title == letter_shuffle_set_translation.target_title
    assert r.native_title == letter_shuffle_set_translation.native_title
    assert len(r.items) > 0
    assert isinstance(r.items[0].native_phrase_audio_file_name, str)

    # PUT
    p.native_title = "Updated title"
    client.put(f"{endpoint}/translations/pl", 200, json=p)
    r = client.get_typed(f"{endpoint}/translations/pl", 200, LetterShuffleSetTranslation)
    assert r.native_title == "Updated title"

    # DELETE
    client.delete(f"{endpoint}/translations/pl", 200)
    client.get(f"{endpoint}/translations/pl", 404)


def test_patch_set(client: ApiTestClient, endpoint: str, letter_shuffle_set_translation: LetterShuffleSetTranslation):
    # Given: A saved translation
    client.post_typed(f"{endpoint}/translations", 200, LetterShuffleSetTranslation, json=letter_shuffle_set_translation)
    # When: A set is patched
    client.patch_typed(endpoint, 200, LetterShuffleSet, json=LetterShuffleSetPatch(image_name="xxx"))
    # Then: The translation is patched as well
    t = client.get_typed(f"{endpoint}/translations/pl", 200, LetterShuffleSetTranslation)
    assert t.image_name=="xxx"
    # And: The topics are patched as well
    for level in list(Level):
        r = client.get_typed_list(f"/api/topics/en/{level}/pl", 200, Topic)
        assert 1 == len(r)
        assert r[0].image_name == "xxx"
