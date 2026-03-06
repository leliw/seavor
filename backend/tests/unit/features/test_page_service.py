from uuid import uuid4

from ampf.base import BaseAsyncFactory
import pytest

from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import AnswerOption, DefinitionGuess, DefinitionGuessCreate, Sentence
from features.pages.page_base_model import PageType
from features.pages.page_service import PageService
from shared.audio_files.audio_file_service import AudioFileService
from tests.unit.conftest import TtsServiceMock


@pytest.fixture
def page_service(
    factory: BaseAsyncFactory,
) -> PageService:
    audio_file_service = AudioFileService(factory, TtsServiceMock())
    return PageService(factory, audio_file_service, Language.EN, Level.A1, uuid4())


@pytest.mark.asyncio
async def test_post_definition_guess(page_service: PageService):
    # Given: PageService
    assert page_service is not None
    # And: DefinitionGuessCreate without audios and images
    value_create = DefinitionGuessCreate(
        language=Language.EN,
        level=Level.A1,
        order=1,
        type=PageType.DEFINITION_GUESS,
        phrase="Runway",
        definition="This is a specially prepared long, flat surface at an airport where aircraft accelerate to take off or decelerate after landing.",
        sentences=[
            Sentence(
                text_with_gap="The pilot brought the jumbo jet down smoothly onto the main ______.",
                gap_filler_form="runway",
            ),
            Sentence(
                text_with_gap="We watched from the terminal as the small private plane lined up at the end of the ______ for departure.",
                gap_filler_form="runway",
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
        ],
        hint="Consider the specific part of an airport where an aeroplane gathers speed to lift off or slows down after touching the ground.",
        explanation="The 'runway' is the very heart of an airport's operational area for aircraft movement. It's the dedicated stretch of ground, often several kilometres long, where planes perform their most critical high-speed manoeuvres for departure and arrival. It's a cornerstone of aviation, much like the main thoroughfare of a bustling market town, but for aeroplanes!",
    )
    # When: Post
    value: DefinitionGuess = await page_service.post(value_create)  # type: ignore
    # Then: DefinitionGuess is created
    assert value is not None
    assert value.id is not None
    assert value.type == PageType.DEFINITION_GUESS
    # Then: Audio files are exist
    assert value.phrase_audio_file_name is not None
    assert value.definition_audio_file_name is not None
    assert value.hint_audio_file_name is not None
    assert value.explanation_audio_file_name is not None
    for sentence in value.sentences:
        assert sentence.audio_file_name is not None
    for alternative in value.alternatives:
        assert alternative.audio_file_name is not None
    for distractor in value.distractors:
        assert distractor.audio_file_name is not None

