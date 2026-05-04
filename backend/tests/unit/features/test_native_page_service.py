from uuid import uuid4

import pytest
from ampf.base import KeyNotExistsException
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeDefinitionGuess, NativeDefinitionGuessBase
from features.native_pages.native_page_service import NativePageService, NativePageServiceFactory
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, Sentence
from features.pages.page_base_model import PageType
from shared.audio_files.audio_file_service import AudioFileService
from shared.images.image_service import ImageService


@pytest.fixture
def native_page_service(
    native_page_service_factory: NativePageServiceFactory,
) -> NativePageService:
    return native_page_service_factory.create(Language.EN, Level.A1, Language.PL, uuid4())


@pytest.mark.asyncio
async def test_delete_native_page(
    native_page_service: NativePageService, audio_file_service: AudioFileService, image_service: ImageService
):
    # Given: NativePageService
    assert native_page_service is not None
    # And: Existing native page with audio files and image
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
            )
        ],
        alternatives=[],
        distractors=[],
        hint="Consider the specific part of an airport where an aeroplane gathers speed to lift off or slows down after touching the ground.",
        explanation="",
        image_names=[await image_service.generate_and_upload("xxx", Language.EN)],
        definition_audio_file_name=await audio_file_service.generate_and_upload("xxx", Language.EN),
    )
    native_value_create = NativeDefinitionGuessBase(
        native_language=Language.PL,
        native_phrase="xxx",
        native_definition="xxx",
        native_sentences=[],
        native_alternatives=[],
        native_distractors=[],
    )
    native_page = NativeDefinitionGuess.from_page(DefinitionGuess.create(value_create), native_value_create)
    native_page = await native_page_service.create(native_page)
    # When: Delete
    await native_page_service.delete(native_page.id)
    # Then: Page is deleted
    with pytest.raises(KeyNotExistsException):
        assert await native_page_service.get(native_page.id)
    # And: Audio files are deleted
    assert native_page.type == PageType.DEFINITION_GUESS
    assert native_page.definition_audio_file_name
    with pytest.raises(KeyNotExistsException):
        await audio_file_service.download(native_page.definition_audio_file_name)
    for image_name in native_page.image_names or []:
        with pytest.raises(KeyNotExistsException):
            await image_service.download(image_name)
