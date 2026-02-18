from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.levels import Level
from features.pages.page_model import (
    BasePage,
    GapFillChoiceExercise,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExercisePatch,
)
from features.topics.topic_model import Topic, TopicCreate


@pytest.fixture
def gap_fill_choice_exercise_create() -> GapFillChoiceExerciseCreate:
    return GapFillChoiceExerciseCreate(
        level=Level.A1,
        order=1,
        target_language=Language.EN,
        target_sentence="Hello [___]!",
        gap_marker="[___]",
        options=["World", "Earth", "Moon"],
        correct_index=0,
        target_explanation="The common greeting.",
        target_distractors_explanation={"1": "Not a planet.", "2": "Also not a planet."},
        target_hint="Starts with W",
    )


@pytest.fixture
def topic_id(client: ApiTestClient, topic_create: TopicCreate) -> UUID:
    r = client.post_typed("/api/topics", 200, Topic, json=topic_create)
    return r.id


@pytest.fixture
def endpoint(topic_id: UUID) -> str:
    return f"/api/topics/en/A1/{topic_id}/pages"


def test_get_all(client: ApiTestClient, endpoint: str):
    r = client.get_typed_list(endpoint, 200, BasePage)
    assert isinstance(r, list)
    assert 0 == len(r)


def test_post_get_put_delete(client: ApiTestClient, endpoint: str, gap_fill_choice_exercise_create):
    # POST
    posted_exercise = client.post_typed(endpoint, 200, GapFillChoiceExercise, json=gap_fill_choice_exercise_create)
    exercise_id = posted_exercise.id

    # GET
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise)
    assert r.id == exercise_id
    assert r.target_sentence == "Hello [___]!"
    assert r.correct_index == 0

    # PATCH
    updated_sentence = "Hi [___]!"
    gfce_patch = GapFillChoiceExercisePatch(
        level=Level.A1,
        target_sentence=updated_sentence,
        correct_index=1,  # Change correct answer
    )
    r = client.patch_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise, json=gfce_patch.model_dump())
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise)
    assert r.target_sentence == updated_sentence
    assert r.correct_index == 1

    # DELETE
    client.delete(f"{endpoint}/{exercise_id}", 200)
    client.get(f"{endpoint}/{exercise_id}", 404)
