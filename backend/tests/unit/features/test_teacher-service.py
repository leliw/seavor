import pytest
from features.languages import Language
from features.levels import Level
from features.pages.page_model import GapFillChoiceExerciseCreate, InfoPageCreate
from features.teacher.teacher_service import TeacherService
from haintech.testing import MockerAIModel
from shared.prompts.prompt_service import PromptService


@pytest.fixture
def teacher_service() -> TeacherService:
    return TeacherService(PromptService("./app/prompts"), Language.EN, Level.A1)


def test_generate_word_list(teacher_service: TeacherService, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="Prepare a set of 3 words and short (2-3 words) phrases related to Springtime.",
        response='[\n  "Daffodils",\n  "Lambing season",\n  "April showers"\n]',
    )
    # Given: A teacher service
    assert teacher_service is not None
    # When: Generate word list
    words = teacher_service.generate_word_list("Springtime", 3)
    # Then: Words are generated
    assert len(words) > 0
    assert isinstance(words, list)
    assert all(isinstance(word, str) for word in words)


def test_get_word_definition(teacher_service: TeacherService, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="**Daffodils**",
        response="A vibrant, typically yellow or white flower, characterized by its distinctive trumpet-shaped central cup and six surrounding petals, widely recognized as one of the earliest heralds of the new growing season.",
    )
    # Given: A teacher service
    assert teacher_service is not None
    # When: Generate word list
    definition = teacher_service.get_word_definition("Springtime", "Daffodils")
    # Then: A definition is returned
    assert len(definition) > 0
    assert isinstance(definition, str)


def test_create_gap_fill_choice_exercises(teacher_service: TeacherService, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="Semi-modal verbs",
        response="""[{
        "language": "en",
        "level": "A2",
        "order": 1,
        "sentence": "When in Britain, visitors _____ remember to drive on the left-hand side of the road, come rain or shine.",
        "gap_marker": "_____",
        "options": ["have to", "used to", "ought to"],
        "correct_index": 0,
        "explanation": "The semi-modal verb 'have to' expresses a strong obligation or necessity, which is certainly the case when driving in a country with different road rules. It's a legal requirement, not merely a suggestion.",
        "distractors_explanation": {
            "used to": "This refers to a past habit or state that no longer exists, which isn't applicable here as driving on the left is a current rule.",
            "ought to": "This suggests a recommendation or moral duty, but driving on the left is a legal requirement, not just a suggestion or a matter of good manners."
        }
    }]""",
    )
    # Given: A teacher service
    assert teacher_service is not None
    # When: Create excercises

    pages = teacher_service.create_gap_fill_choice_excercises("Semi-modal verbs", 1)
    # Then: Excercises are created
    assert len(pages) > 0
    assert isinstance(pages, list)
    assert all(isinstance(page, GapFillChoiceExerciseCreate) for page in pages)


def test_create_info_pages(teacher_service: TeacherService, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="Verb to be (am / is / are)",
        response="""[  {
        "language": "en",
        "level": "A1",
        "order": 1,
        "type": "info",
        "title": "To Be or Not To Be?",
        "content": "Hello there! Today, we learn about 'to be'. It's a very important verb in English!"
    }]""",
    )
    # Given: A teacher service
    assert teacher_service is not None
    # When: Create excercises
    pages = teacher_service.create_info_pages("Verb to be (am / is / are)")
    # Then: Excercises are created
    assert len(pages) > 0
    assert isinstance(pages, list)
    assert all(isinstance(page, InfoPageCreate) for page in pages)


def test_create_topic_description(teacher_service: TeacherService, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="Verb to be (am / is / are)",
        response="Master 'am, is, are' \u2013 the heart of English sentences. Easy peasy!",
    )
    # Given: A teacher service
    assert teacher_service is not None
    # When: Create description
    ret = teacher_service.create_topic_description("Verb to be (am / is / are)")
    # Then: Description is created
    assert isinstance(ret, str)
