from ampf.testing import ApiTestClient
from features.native_pages.native_page_model import NativeGapFillChoiceExercise
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_model import GapFillChoiceExercise, GapFillChoiceExerciseCreate
from features.topics.topic_model import Topic, TopicCreate
from haintech.testing import MockerAIModel

# - add topic
# - add topic page
# - translate topic
# - translate topic page


def test_gap_fill_choice(client: ApiTestClient, headers: dict[str, str], topic_create: TopicCreate, mocker_ai_model: MockerAIModel):
    # Add topic
    t = client.post_typed("/api/topics", 200, Topic, json=topic_create, headers=headers)

    # Add topic page
    topic_page = GapFillChoiceExerciseCreate(
        level=t.level,
        order=1,
        language=t.language,
        sentence="Hello [___]!",
        gap_marker="[___]",
        options=["World", "Earth", "Moon"],
        correct_index=0,
        explanation="The common greeting.",
        distractors_explanation={"1": "Not a planet.", "2": "Also not a planet."},
        hint="Starts with W",
    )
    p = client.post_typed(
        f"/api/topics/{t.language}/{t.level}/{t.id}/pages",
        200,
        GapFillChoiceExercise,
        json=topic_page.model_dump(mode="json"),
    )

    # Translate topic
    mocker_ai_model.add(
        message_containing="Semi-modals",
        response='{"title": "Czasowniki półmodalne",  "description": "Czasowniki półmodalne a czyste czasowniki modalne"}',
    )
    client.post_typed(f"/api/native-topics/{t.language}/{t.level}/pl/{t.id}", 200, NativeTopic)
    mocker_ai_model.add(
        message_containing="Hello World!",
        response="""
        {\"sentence\": \"Witaj [___]!\", \"answer\": \"Witaj Świecie!\", \"explanation\": \"Powszechne powitanie.\", \"distractors_explanation\": {\"1\": \"Nie planeta.\", \"2\": \"Również nie planeta.\"}, \"hint\": \"Zaczyna się na W\"}
        """,
    )
    # Translate topic page
    np = client.post_typed(
        f"/api/native-topics/{t.language}/{t.level}/pl/{t.id}/pages/{p.id}", 200, NativeGapFillChoiceExercise
    )
    assert np.native_answer == "Witaj Świecie!"
    assert np.native_explanation == "Powszechne powitanie."
