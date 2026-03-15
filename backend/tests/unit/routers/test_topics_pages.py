from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import AnswerOption, DefinitionGuess, DefinitionGuessCreate, DefinitionGuessPatch, Sentence
from features.pages.page_base_model import BasePage
from features.pages.page_model import (

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
        language=Language.EN,
        sentence="Hello [___]!",
        gap_marker="[___]",
        options=["World", "Earth", "Moon"],
        correct_index=0,
        explanation="The common greeting.",
        distractors_explanation={"1": "Not a planet.", "2": "Also not a planet."},
        hint="Starts with W",
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


def test_post_get_put_delete(client: ApiTestClient, endpoint: str, gap_fill_choice_exercise_create: GapFillChoiceExerciseCreate):
    # POST
    posted_exercise = client.post_typed(endpoint, 200, GapFillChoiceExercise, json=gap_fill_choice_exercise_create.model_dump())
    exercise_id = posted_exercise.id

    # GET
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise)
    assert r.id == exercise_id
    assert r.sentence == "Hello [___]!"
    assert r.correct_index == 0

    # PATCH
    updated_sentence = "Hi [___]!"
    gfce_patch = GapFillChoiceExercisePatch(
        level=Level.A1,
        sentence=updated_sentence,
        correct_index=1,  # Change correct answer
    )
    r = client.patch_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise, json=gfce_patch.model_dump())
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, GapFillChoiceExercise)
    assert r.sentence == updated_sentence
    assert r.correct_index == 1

    # DELETE
    client.delete(f"{endpoint}/{exercise_id}", 200)
    client.get(f"{endpoint}/{exercise_id}", 404)


@pytest.fixture
def definition_guess_create() -> DefinitionGuessCreate:
    return DefinitionGuessCreate(
        level=Level.A1,
        order=1,
        language=Language.EN,
        phrase="Hello",
        definition="The common greeting.",
        sentences=[
            Sentence(
                text_with_gap="Hello [___]!",
                gap_filler_form="World",
                audio_file_name="xxx",
            ),
        ],
        alternatives=[
            AnswerOption(
                value="World",
                explanation="The common greeting.",
                audio_file_name="xxx",
            ),
        ],
        distractors=[
            AnswerOption(
                value="Earth",
                explanation="Not a planet.",
                audio_file_name="xxx",
            ),
            AnswerOption(
                value="Moon",
                explanation="Also not a planet.",
                audio_file_name="xxx",
            ),
        ],
        hint="Starts with W",
        explanation="The common greeting.",
    )


def test_post_get_put_delete_definition_guess(
    client: ApiTestClient, endpoint: str, definition_guess_create: DefinitionGuessCreate
):
    # POST
    posted_exercise = client.post_typed(endpoint, 200, DefinitionGuess, json=definition_guess_create.model_dump(mode="json"))
    exercise_id = posted_exercise.id

    # GET
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, DefinitionGuess)
    assert r.id == exercise_id
    assert r.phrase == "Hello"
    assert r.definition == "The common greeting."


    # PATCH
    updated_phrase = "Hi"
    value_patch = DefinitionGuessPatch(
        phrase=updated_phrase,
    )
    r = client.patch_typed(f"{endpoint}/{exercise_id}", 200, DefinitionGuess, json=value_patch)
    r = client.get_typed(f"{endpoint}/{exercise_id}", 200, DefinitionGuess)
    assert r.phrase == updated_phrase

    # DELETE
    client.delete(f"{endpoint}/{exercise_id}", 200)
    client.get(f"{endpoint}/{exercise_id}", 404)
