import asyncio
from pathlib import Path

import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeDefinitionGuess
from features.native_topics.native_topic_model import NativeTopic
from features.pages.definition_guess_model import DefinitionGuess
from features.repetitions.repetition_model import RepetitionCard, RepetitionSchedule
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.topics.topic_model import Topic
from ampf.tasks import TaskHeader, TaskStatus
from haintech.testing import MockerAIModel
from tests.mocker_image_generator import *

# User can add their own private definition guess:


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_private_definition_guess(
    client: ApiTestClient,
    headers: dict[str, str],
    second_user_headers: dict[str, str],
    mocker_ai_model: MockerAIModel,
    mocker_image_generator: MockerImageGenerator,
    tmp_path: Path,
):
    mocker_ai_model.add(
        message_containing="Translate the topic",
        response='{\n  "title": "Domyślne",\n  "description": "Różne słowa"\n}',
    )
    mocker_ai_model.add(
        message_containing="Your task is to generate definition guess exercise",
        response='{\n  "level": "A1",\n  "definition": "A common spoken expression used to greet someone or to answer the telephone.",\n  "sentences": [\n    {\n      "text_with_gap": "She walked into the room and said, \'_____, everyone!\'",\n      "gap_filler_form": "Hello"\n    },\n    {\n      "text_with_gap": "When the phone rang, he picked it up and said, \'_____, who\'s speaking?\'",\n      "gap_filler_form": "Hello"\n    },\n    {\n      "text_with_gap": "As I passed my neighbour, I gave a friendly wave and a quick \'_____\' before continuing my stroll.",\n      "gap_filler_form": "Hello"\n    }\n  ],\n  "alternatives": [\n    {\n      "value": "Hi",\n      "explanation": "This is a more informal greeting, perfectly suitable for friends and casual acquaintances, whereas \'Hello\' can be used in a wider range of situations, both formal and informal."\n    },\n    {\n      "value": "Good morning/afternoon/evening",\n      "explanation": "These greetings are more formal and are specifically tied to the time of day. \'Hello\' is a general greeting that can be used at any time."\n    },\n    {\n      "value": "How do you do?",\n      "explanation": "A very traditional and formal greeting, often used in British English, which typically doesn\'t require a detailed answer, but rather a reciprocal \'How do you do?\' \'Hello\' is much more versatile and common."\n    }\n  ],\n  "distractors": [\n    {\n      "value": "Goodbye",\n      "explanation": "This phrase is used to express farewell when parting ways, not to initiate a conversation or acknowledge someone\'s presence."\n    },\n    {\n      "value": "Excuse me",\n      "explanation": "This is used to politely get someone\'s attention, ask for passage, or apologize, but it is not a greeting."\n    },\n    {\n      "value": "Please",\n      "explanation": "This word is used to make a request more polite or to express a polite invitation, not as a way to greet someone."\n    }\n  ],\n  "hint": "Think of the very first word you often say when you meet someone new or pick up the telephone. It\'s a universal way to acknowledge someone\'s presence."\n}',
    )
    mocker_ai_model.add(
        message_containing="Verify exercise",
        response='{"score": 100, "errors": []}',
    )
    mocker_ai_model.add(
        message_containing="Translate definition guess exercise to student's native language:",
        response='{\n  "native_phrase": "Witaj",\n  "native_definition": "Powszechne wyra\u017cenie u\u017cywane do powitania kogo\u015b lub, w j\u0119zyku angielskim, tak\u017ce do odebrania telefonu.",\n  "native_sentences": [\n    {\n      "text": "Wesz\u0142a do pokoju i powiedzia\u0142a: \'____, wszystkim!\'"\n    },\n    {\n      "text": "Kiedy zadzwoni\u0142 telefon, odebra\u0142 go i po prostu powiedzia\u0142: \'____?\'"\n    },\n    {\n      "text": "To dobre maniery, \u017ceby powiedzie\u0107 ____, kiedy poznajesz kogo\u015b nowego."\n    }\n  ],\n  "native_alternatives": [\n    {\n      "value": "Cze\u015b\u0107",\n      "explanation": "To bardziej nieformalne powitanie, cz\u0119sto u\u017cywane w\u015br\u00f3d przyjaci\u00f3\u0142 lub w swobodnych okoliczno\u015bciach, podczas gdy \'Witaj\' jest nieco bardziej formalne lub uroczyste, cho\u0107 r\u00f3wnie\u017c uniwersalne."\n    },\n    {\n      "value": "Dzie\u0144 dobry/popo\u0142udnie/wiecz\u00f3r",\n      "explanation": "Te powitania s\u0105 bardziej formalne i specyficzne dla pory dnia, zmieniaj\u0105 si\u0119 w zale\u017cno\u015bci od tego, jaka jest godzina, w przeciwie\u0144stwie do \'Witaj\', kt\u00f3re jest odpowiednie o ka\u017cdej porze."\n    },\n    {\n      "value": "Jak si\u0119 masz?",\n      "explanation": "To bardzo tradycyjne i formalne powitanie, szczeg\u00f3lnie powszechne przy pierwszym spotkaniu z kim\u015b, i cz\u0119sto nie oczekuje dos\u0142ownej odpowiedzi na pytanie \'jak\'."\n    }\n  ],\n  "native_distractors": [\n    {\n      "value": "Do widzenia",\n      "explanation": "To wyra\u017cenie jest u\u017cywane na po\u017cegnanie, czyli jest ca\u0142kowitym przeciwie\u0144stwem powitania."\n    },\n    {\n      "value": "Przepraszam",\n      "explanation": "U\u017cywa si\u0119 tego, aby uprzejmie zwr\u00f3ci\u0107 czyj\u0105\u015b uwag\u0119 lub przeprosi\u0107, a nie zainicjowa\u0107 powitanie."\n    },\n    {\n      "value": "Prosz\u0119",\n      "explanation": "To s\u0142owo jest u\u017cywane do uprzejmej pro\u015bby lub podkre\u015blenia zaproszenia, a nie jako samodzielne powitanie."\n    }\n  ],\n  "native_hint": "To, co m\u00f3wisz, kiedy po raz pierwszy kogo\u015b spotykasz lub odbierasz telefon, prosty spos\u00f3b na potwierdzenie czyjej\u015b obecno\u015bci.",\n  "native_explanation": null\n}',
    )
    mocker_ai_model.add(
        message_containing="Please generate an image prompt",
        response='{"image_prompt": "A person, gender-neutral, is navigating a dynamic and slightly unpredictable environment, like an obstacle course or a path with unexpected, playful elements. They are in an active, alert stance, perhaps on the balls of their feet, with a focused and ready expression. The scene should convey a sense of constant vigilance and readiness for minor surprises or changes, preventing them from becoming too relaxed. The background could be a vibrant, engaging setting, like a game show stage or a fantastical training ground. No text or words in the image."}',
    )
    mocker_image_generator.add(response=b"Mocked image bytes")
    # with mocker_ai_model.record():
    # Given: A phrase from user
    language = Language.EN
    level = Level.A1
    definition_guess_create = TeacherDefinitionGuessCreate(language=language, level=level, phrase="Hello")
    # When: Add the phrase
    ctx = client.post_typed(
        "/api/teacher/definition-guess", 202, TaskHeader, headers=headers, json=definition_guess_create
    )
    # And: Wait until it is processed
    while ctx.status != TaskStatus.COMPLETED:
        await asyncio.sleep(1)
        ctx = client.get_typed(f"/api/teacher/{ctx.id}", 200, TaskHeader, headers=headers)
    assert ctx.result_id is not None
    r = client.get_typed(f"/api/repetitions/{ctx.result_id}", 200, RepetitionCard, headers=headers)
    # Then: A private topic exists
    topic = client.get_typed(f"/api/topics/{r.topic_id}", 200, Topic, headers=headers)
    assert topic.private
    # And: A definition in this topic exists
    page = client.get_typed(f"/api/topics/{r.topic_id}/pages/{r.page_id}", 200, DefinitionGuess, headers=headers)
    # And: Image is generated and stored in page
    assert page.image_names
    # And: Native private topic exists
    ntopic = client.get_typed(
        f"/api/native-topics/pl/{r.topic_id}",
        200,
        NativeTopic,
        headers=headers,
    )
    assert ntopic.private

    # And: Native private page exists
    npage = client.get_typed(
        f"/api/native-topics/pl/{r.topic_id}/pages/{r.page_id}",
        200,
        NativeDefinitionGuess,
        headers=headers,
    )
    # And: Image is generated and stored in native page
    assert npage.image_names
    # And: All items are stored in proper paths
    topic_path = tmp_path / f"topics/{topic.id}.json"
    assert topic_path.exists()
    page_path = tmp_path / f"topics/{topic.id}/pages/{r.page_id}.json"
    assert page_path.exists()
    ntopic_path = tmp_path / f"translations/pl/topics/{topic.id}.json"
    assert ntopic_path.exists()
    npage_path = tmp_path / f"translations/pl/topics/{topic.id}/pages/{r.page_id}.json"
    assert npage_path.exists()

    # And: Repetition is added
    schedule = client.get_typed("/api/repetitions/schedule", 200, RepetitionSchedule, headers=headers)
    # Then: Status is returned
    assert schedule
    assert len(schedule.root) == 1
    assert list(schedule.root.items())[0][1] == 1
    # And: They are not available for unauthorized users
    client.get(f"/api/topics/{r.topic_id}", 403)
    client.get(f"/api/topics/{r.topic_id}/pages/{r.page_id}", 403)
    client.get(f"/api/native-topics/pl/{r.topic_id}", 403)
    client.get(f"/api/native-topics/pl/{r.topic_id}/pages/{r.page_id}", 403)
    # And: They are not available for other authorized users
    client.get(f"/api/topics/{r.topic_id}", 403, headers=second_user_headers)
    client.get(f"/api/topics/{r.topic_id}/pages/{r.page_id}", 403, headers=second_user_headers)
    client.get(f"/api/native-topics/pl/{r.topic_id}", 403, headers=second_user_headers)
    client.get(f"/api/native-topics/pl/{r.topic_id}/pages/{r.page_id}", 403, headers=second_user_headers)
