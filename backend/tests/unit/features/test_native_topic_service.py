from datetime import datetime
from uuid import uuid4

import pytest
from ampf.base import BaseAsyncFactory, KeyNotExistsException
from ampf.dependency import DependencyRegistry
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeDefinitionGuess, NativeDefinitionGuessBase
from features.native_topics.native_topic_model import NativeTopic
from features.native_topics.native_topic_service import NativeTopicService
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, Sentence
from features.pages.page_base_model import PageType
from features.topics.topic_model import TopicType

target_language = Language.EN
level = Level.A1
native_language = Language.PL

v2 = NativeTopic(
    id=uuid4(),
    language=target_language,
    level=level,
    type=TopicType.LETTER_SHUFFLE,
    title="tt",
    description="td",
    native_language=native_language,
    native_title="nt",
    native_description="nd",
    created_at=datetime.now(),
    updated_at=datetime.now(),
)


@pytest.fixture
def service(factory: BaseAsyncFactory):
    return DependencyRegistry.get(NativeTopicService)


@pytest.mark.asyncio
async def test_delete_pages(
    service: NativeTopicService,
):
    # Given: Stored native topic
    topic = v2
    await service.save(topic)
    # And: Stored native page
    page_service = service.native_page_service_factory.create(topic.native_language, topic.id)
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
        image_names=[],
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
    page = await page_service.create(native_page)
    assert await page_service.get(page.id)
    # When: The topic is deleted
    await service.delete(topic.native_language, topic.id)
    # Then: The page is deleted too
    with pytest.raises(KeyNotExistsException):
        await page_service.get(page.id)
