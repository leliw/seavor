from uuid import UUID
import pytest
from ampf.testing import ApiTestClient
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleSet,
    LetterShuffleSetHeader,
)
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleItemTranslation,
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationCreate,
    LetterShuffleSetTranslationHeader,
)

from tests.unit.routers.test_letter_shuffles import letter_shuffle_set


@pytest.fixture()
def id(client: ApiTestClient) -> UUID:
    value = LetterShuffleSet.create(letter_shuffle_set)
    p = client.post_typed("/api/letter-shuffles", 200, LetterShuffleSet, json=value)
    return p.id


@pytest.fixture()
def endpoint(client: ApiTestClient, id) -> str:
    return f"/api/letter-shuffles/{id}/translations"


def test_get_all(client: ApiTestClient, endpoint: str):
    r = client.get_typed_list(endpoint, 200, LetterShuffleSetTranslationHeader)
    assert 0 == len(r)


def test_post_get_put_patch_delete(client: ApiTestClient, id: UUID, endpoint: str):
    value = LetterShuffleSetTranslation.create(
        LetterShuffleSetTranslationCreate(
            id=id,
            language="pl",
            title="Boże Narodzenie",
            description="Słowa i wyrażenia związane z Bożym Narodzeniem",
            items=[
                LetterShuffleItemTranslation(
                    question="Kolenda",
                    description="Tradycyjna pieśń spiewana w okresie Bożego Narodzenia.",
                ),
            ],
        )
    )

    # POST
    p = client.post_typed(endpoint, 200, LetterShuffleSetTranslation, json=value)

    # GET ALL
    r = client.get_typed_list(endpoint, 200, LetterShuffleSetTranslationHeader)
    assert 1 == len(r)
    assert r[0].title == value.title

    # GET
    r = client.get_typed(f"{endpoint}/pl", 200, LetterShuffleSetTranslation)
    assert r.title == value.title
    assert len(r.items) > 0
    assert isinstance(r.items[0].question_audio_file_name, str)

    # PUT
    p.title = "Updated title"
    client.put(f"{endpoint}/pl", 200, json=p)
    r = client.get_typed(f"{endpoint}/pl", 200, LetterShuffleSetTranslation)
    assert r.title == "Updated title"


    # DELETE
    client.delete(f"{endpoint}/pl", 200)
    client.get(f"{endpoint}/pl", 404)
