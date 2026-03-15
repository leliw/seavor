import pytest
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeDefinitionGuessBase, NativeInfoPageBase
from features.native_pages.native_page_translator import NativePageTranslator
from features.pages.definition_guess_model import AnswerOption, DefinitionGuess, DefinitionGuessCreate, Sentence
from features.pages.page_model import InfoPage, InfoPageCreate, PageType
from haintech.ai.google_generativeai import GoogleAIModel
from haintech.testing import MockerAIModel
from shared.prompts.prompt_service import PromptService


@pytest.fixture
def native_page_translator() -> NativePageTranslator:
    ai_model = GoogleAIModel("gemini-2.5-flash-lite")
    return NativePageTranslator(ai_model, PromptService("./app/prompts"), None)  # type: ignore


@pytest.mark.asyncio
async def test_translate_info_page(native_page_translator: NativePageTranslator, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        system_prompt="You are translating info pages of a language course from English to sudent native language: Polish.\nTranslate only if it is necessary.",
        message_containing='**\nVerb to be: Using "are"\n',
        response="[{\"native_title\": \"Czasownik 'by\u0107': U\u017cycie 'are'\", \"native_content\": \"U\u017cywaj 'are' z 'you', 'we', 'they' lub rzeczownikami w liczbie mnogiej. Na przyk\u0142ad: 'You are kind.' 'They are friends.'\"}]",
    )
    # Given: an info page
    page = InfoPage.create(
        InfoPageCreate(
            language=Language.EN,
            level=Level.A1,
            order=1,
            type=PageType.INFO,
            title='Verb to be: Using "are"',
            content='Use "are" with you, we, they, or plural nouns. For example: "You are kind." "They are friends."',
        )
    )
    # When: Translate page
    ret = await native_page_translator._translate_info_page(page.language, Language.PL, page)
    # Then: A translated page is returned
    assert isinstance(ret, NativeInfoPageBase)
    assert ret.native_title
    assert ret.native_content


@pytest.mark.asyncio
async def test_translate_definition_guess(native_page_translator: NativePageTranslator, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add_calls(
        [
            {
                "system_prompt": "You are a English teacher.\nUse phrases and expressions that are natural to the English language and related to English tradition.\nYour student speaks Polish.",
                "message_str": "Translate definition guess exercise to student's native language: Polish:\n\nPhrase: Runaway\nDefinition: This is a specially prepared long, flat surface at an airport where aircraft accelerate to take off or decelerate after landing.\nSentences:\n - The pilot brought the jumbo jet down smoothly onto the main runway.\n - We watched from the terminal as the small private plane lined up at the end of the runaway for departure.\n - Due to the icy conditions, ground crews were busy clearing snow from the runaway all morning.\nAlternatives:\n - value: Airstrip; explanation: An 'airstrip' is generally a simpler, often unpaved or less developed landing area, typically for smaller aircraft or in more remote locations. A 'runway' is a highly engineered, paved surface at a formal airport.\n - value: Landing strip; explanation: While very similar to an airstrip and sometimes used interchangeably, 'landing strip' often implies a more basic facility. 'Runway' specifically denotes the primary, marked, and often illuminated surface at a commercial or military airport designed for regular, heavy operations.\nDistractors:\n - value: Taxiway; explanation: A 'taxiway' is a path connecting runways to terminals, hangars, and other airport facilities. Aircraft use it to move around the airport, but not for the actual act of takeoff or landing.\n - value: Apron / Tarmac; explanation: The 'apron' (often colloquially called the 'tarmac') is the area where aircraft are parked, loaded, unloaded, refuelled, and boarded. It's a static area, not for the dynamic actions of takeoff or landing.\n - value: Flight path; explanation: A 'flight path' refers to the route an aircraft follows in the air, not a physical surface on the ground.\n\nHint: Consider the specific part of an airport where an aeroplane gathers speed to lift off or slows down after touching the ground.\nExplanation: The 'runway' is the very heart of an airport's operational area for aircraft movement. It's the dedicated stretch of ground, often several kilometres long, where planes perform their most critical high-speed manoeuvres for departure and arrival. It's a cornerstone of aviation, much like the main thoroughfare of a bustling market town, but for aeroplanes!\n\n\nEach page should adhere strictly to the json schema provided below.\n\nThe output should be a JSON object:\n{'$defs': {'NativeAnswerOption': {'properties': {'value': {'title': 'Value', 'type': 'string'}, 'explanation': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Explanation'}}, 'required': ['value'], 'title': 'NativeAnswerOption', 'type': 'object'}, 'NativeSentence': {'properties': {'text': {'title': 'Text', 'type': 'string'}}, 'required': ['text'], 'title': 'NativeSentence', 'type': 'object'}}, 'properties': {'native_phrase': {'title': 'Native Phrase', 'type': 'string'}, 'native_definition': {'title': 'Native Definition', 'type': 'string'}, 'native_sentences': {'items': {'$ref': '#/$defs/NativeSentence'}, 'title': 'Native Sentences', 'type': 'array'}, 'native_alternatives': {'items': {'$ref': '#/$defs/NativeAnswerOption'}, 'title': 'Native Alternatives', 'type': 'array'}, 'native_distractors': {'items': {'$ref': '#/$defs/NativeAnswerOption'}, 'title': 'Native Distractors', 'type': 'array'}, 'native_hint': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Native Hint'}, 'native_explanation': {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Native Explanation'}}, 'required': ['native_phrase', 'native_definition', 'native_sentences', 'native_alternatives', 'native_distractors'], 'title': 'NativeDefinitionGuessBase', 'type': 'object'}",
                "response": {
                    "content": '[\n  {\n    "native_phrase": "Pas startowy",\n    "native_definition": "Jest to specjalnie przygotowana, d\u0142uga, p\u0142aska powierzchnia na lotnisku, gdzie samoloty przyspieszaj\u0105, aby wystartowa\u0107, lub zwalniaj\u0105 po wyl\u0105dowaniu.",\n    "native_sentences": [\n      {\n        "text": "Pilot p\u0142ynnie posadzi\u0142 jumbo jeta na g\u0142\u00f3wnym pasie startowym."\n      },\n      {\n        "text": "Obserwowali\u015bmy z terminala, jak ma\u0142y prywatny samolot ustawi\u0142 si\u0119 na ko\u0144cu pasa startowego, gotowy do odlotu."\n      },\n      {\n        "text": "Z powodu oblodzenia, ekipy naziemne przez ca\u0142y ranek by\u0142y zaj\u0119te od\u015bnie\u017caniem pasa startowego."\n      }\n    ],\n    "native_alternatives": [\n      {\n        "value": "L\u0105dowisko",\n        "explanation": "\'L\u0105dowisko\' to zazwyczaj prostszy, cz\u0119sto nieutwardzony lub mniej rozwini\u0119ty obszar do l\u0105dowania, typowo dla mniejszych samolot\u00f3w lub w bardziej odleg\u0142ych miejscach. \'Pas startowy\' to wysoce in\u017cynieryjna, utwardzona powierzchnia na formalnym lotnisku."\n      },\n      {\n        "value": "Pas do l\u0105dowania",\n        "explanation": "Chocia\u017c bardzo podobny do l\u0105dowiska i czasami u\u017cywany zamiennie, \'pas do l\u0105dowania\' cz\u0119sto sugeruje bardziej podstawow\u0105 infrastruktur\u0119. \'Pas startowy\' konkretnie oznacza g\u0142\u00f3wn\u0105, oznakowan\u0105 i cz\u0119sto o\u015bwietlon\u0105 powierzchni\u0119 na lotnisku komercyjnym lub wojskowym, przeznaczon\u0105 do regularnych, intensywnych operacji."\n      }\n    ],\n    "native_distractors": [\n      {\n        "value": "Droga ko\u0142owania",\n        "explanation": "\'Droga ko\u0142owania\' to \u015bcie\u017cka \u0142\u0105cz\u0105ca pasy startowe z terminalami, hangarami i innymi obiektami lotniska. Samoloty u\u017cywaj\u0105 jej do poruszania si\u0119 po lotnisku, ale nie do samego startu czy l\u0105dowania."\n      },\n      {\n        "value": "P\u0142yta postojowa / Tarmac",\n        "explanation": "\'P\u0142yta postojowa\' (cz\u0119sto potocznie nazywana \'tarmac\') to obszar, gdzie samoloty s\u0105 parkowane, \u0142adowane, roz\u0142adowywane, tankowane i wsiadaj\u0105 na nie pasa\u017cerowie. Jest to obszar statyczny, nie przeznaczony do dynamicznych dzia\u0142a\u0144 startu czy l\u0105dowania."\n      },\n      {\n        "value": "Tor lotu",\n        "explanation": "\'Tor lotu\' odnosi si\u0119 do trasy, kt\u00f3r\u0105 samolot pod\u0105\u017ca w powietrzu, a nie do fizycznej powierzchni na ziemi."\n      }\n    ],\n    "native_hint": "Zastan\u00f3w si\u0119 nad konkretn\u0105 cz\u0119\u015bci\u0105 lotniska, gdzie samolot nabiera pr\u0119dko\u015bci, aby wzbi\u0107 si\u0119 w powietrze, lub zwalnia po dotkni\u0119ciu ziemi.",\n    "native_explanation": "\'Pas startowy\' to samo serce obszaru operacyjnego lotniska dla ruchu samolot\u00f3w. To dedykowany odcinek ziemi, cz\u0119sto d\u0142ugi na kilka kilometr\u00f3w, gdzie samoloty wykonuj\u0105 swoje najbardziej krytyczne manewry z du\u017c\u0105 pr\u0119dko\u015bci\u0105 podczas odlotu i przylotu. Jest to kamie\u0144 w\u0119gielny lotnictwa, niczym g\u0142\u00f3wna arteria t\u0119tni\u0105cego \u017cyciem miasteczka targowego, ale dla samolot\u00f3w!"\n  }\n]'
                },
            }
        ]
    )

    # Given: A definition guess
    page = DefinitionGuess.create(
        DefinitionGuessCreate(
            language=Language.EN,
            level=Level.A1,
            order=1,
            type=PageType.DEFINITION_GUESS,
            phrase="Runaway",
            definition="This is a specially prepared long, flat surface at an airport where aircraft accelerate to take off or decelerate after landing.",
            sentences=[
                Sentence(
                    text_with_gap="The pilot brought the jumbo jet down smoothly onto the main ______.",
                    gap_filler_form="runway",
                ),
                Sentence(
                    text_with_gap="We watched from the terminal as the small private plane lined up at the end of the ______ for departure.",
                    gap_filler_form="runaway",
                ),
                Sentence(
                    text_with_gap="Due to the icy conditions, ground crews were busy clearing snow from the ______ all morning.",
                    gap_filler_form="runaway",
                ),
            ],
            alternatives=[
                AnswerOption(
                    value="Airstrip",
                    explanation="An 'airstrip' is generally a simpler, often unpaved or less developed landing area, typically for smaller aircraft or in more remote locations. A 'runway' is a highly engineered, paved surface at a formal airport.",
                ),
                AnswerOption(
                    value="Landing strip",
                    explanation="While very similar to an airstrip and sometimes used interchangeably, 'landing strip' often implies a more basic facility. 'Runway' specifically denotes the primary, marked, and often illuminated surface at a commercial or military airport designed for regular, heavy operations.",
                ),
            ],
            distractors=[
                AnswerOption(
                    value="Taxiway",
                    explanation="A 'taxiway' is a path connecting runways to terminals, hangars, and other airport facilities. Aircraft use it to move around the airport, but not for the actual act of takeoff or landing.",
                ),
                AnswerOption(
                    value="Apron / Tarmac",
                    explanation="The 'apron' (often colloquially called the 'tarmac') is the area where aircraft are parked, loaded, unloaded, refuelled, and boarded. It's a static area, not for the dynamic actions of takeoff or landing.",
                ),
                AnswerOption(
                    value="Flight path",
                    explanation="A 'flight path' refers to the route an aircraft follows in the air, not a physical surface on the ground.",
                ),
            ],
            hint="Consider the specific part of an airport where an aeroplane gathers speed to lift off or slows down after touching the ground.",
            explanation="The 'runway' is the very heart of an airport's operational area for aircraft movement. It's the dedicated stretch of ground, often several kilometres long, where planes perform their most critical high-speed manoeuvres for departure and arrival. It's a cornerstone of aviation, much like the main thoroughfare of a bustling market town, but for aeroplanes!",
        )
    )
    # When: Translate page
    ret = await native_page_translator._translate_definition_guess(page.language, Language.PL, page)
    # Then: A translated page is returned
    assert isinstance(ret, NativeDefinitionGuessBase)
    assert ret.native_phrase
    assert ret.native_definition
