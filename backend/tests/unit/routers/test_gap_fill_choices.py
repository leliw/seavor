import pytest
from ampf.testing import ApiTestClient
from features.gap_fill_choice.gap_fill_choice_model import (
    GapFillChoiceExercise,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExerciseHeader,
    GapFillChoiceExercisePatch,
)
from features.languages import Language
from features.levels import Level


@pytest.fixture
def gap_fill_choice_exercise_create() -> GapFillChoiceExerciseCreate:
    return GapFillChoiceExerciseCreate(
        min_level=Level.A1,
        max_level=Level.A2,
        target_language_code=Language.EN,
        target_sentence="Hello [___]!",
        gap_marker="[___]",
        options=["World", "Earth", "Moon"],
        correct_index=0,
        target_explanation="The common greeting.",
        target_distractors_explanation={"1": "Not a planet.", "2": "Also not a planet."},
        target_hint="Starts with W",
    )


endpoint = "/api/target-languages/en/gap-fill-choices"


def test_get_all(client: ApiTestClient):
    r = client.get_typed_list(endpoint, 200, GapFillChoiceExerciseHeader)
    assert isinstance(r, list)
    assert 0 == len(r)


def test_post_get_put_delete(client: ApiTestClient, gap_fill_choice_exercise_create):
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
        min_level=Level.A1,
        max_level=Level.A2,
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
