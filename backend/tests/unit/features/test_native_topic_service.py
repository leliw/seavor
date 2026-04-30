from datetime import datetime
from uuid import uuid4

from ampf.base import BaseAsyncFactory, BaseAsyncStorage, KeyNotExistsException, StorageFormatFlags
from ampf.dependency import DependencyRegistry
from pydantic import ValidationError
import pytest
import pytest_asyncio

from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeDefinitionGuess, NativeDefinitionGuessBase
from features.native_topics.native_topic_model import NativeTopic_v1, NativeTopic_v2
from features.native_topics.native_topic_service import NativeTopicService
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, Sentence
from features.pages.page_base_model import PageType
from features.topics.topic_model import TopicType

target_language = Language.EN
level = Level.A1
native_language = Language.PL
v1 = NativeTopic_v1(
    id=uuid4(),
    target_language_code=target_language,
    levels=[level],
    target_title="tt",
    target_description="td",
    native_language_code=native_language,
    native_title="nt",
    native_description="nd",
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
v2 = NativeTopic_v2(
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
def storage_v1(factory: BaseAsyncFactory):
    return factory.create_storage(
        f"target-languages/{target_language}/levels/{level}/native-languages/{native_language}/topics", NativeTopic_v1
    )


@pytest.fixture
def service(factory: BaseAsyncFactory):
    return DependencyRegistry.get(NativeTopicService)


@pytest_asyncio.fixture
async def storage_v2(service: NativeTopicService):
    return service._get_storage(target_language, level, native_language)


@pytest.mark.asyncio
async def test_save_old_read_new(service: NativeTopicService, storage_v1: BaseAsyncStorage[NativeTopic_v1]):
    # Given: A session stored in previous format
    old = v1
    await storage_v1.save(old)
    # And: An old fromat is stored
    NativeTopic_v2.FORMAT_FLAGS = StorageFormatFlags(save_new_format=False, migrate_legacy_on_read=False)
    # When: The session is read
    new = await service.get(target_language, level, native_language, old.id)
    # Then: A new format is returned
    assert isinstance(new, NativeTopic_v2)
    # And: The previous version is returned
    assert new.v == 1
    # And: The old format is sill stored
    saved = await storage_v1.get(old.id)
    assert isinstance(saved, NativeTopic_v1)
    assert "v" not in saved.model_dump().keys()


@pytest.mark.asyncio
async def test_save_new_read_old(
    storage_v1: BaseAsyncStorage[NativeTopic_v1],
    storage_v2: BaseAsyncStorage[NativeTopic_v2],
):
    # Given: A session stored in new format
    new = v2
    # And: Upgrade feature flag is not set
    NativeTopic_v2.FORMAT_FLAGS.save_new_format = False
    # When: The new format is saved
    await storage_v2.save(new)
    # Then: The old format is stored
    saved = await storage_v1.get(new.id)
    assert isinstance(saved, NativeTopic_v1)
    assert "v" not in saved.model_dump().keys()


@pytest.mark.asyncio
async def test_save_new_read_new(
    service: NativeTopicService,
    storage_v1: BaseAsyncStorage[NativeTopic_v1],
    storage_v2: BaseAsyncStorage[NativeTopic_v2],
):
    # Given: A session stored in new format
    new = v2
    # And: Upgrade feature flag is set
    NativeTopic_v2.FORMAT_FLAGS.save_new_format = True
    # When: The new format is saved
    await storage_v2.save(new)
    # Then: The new format is stored
    with pytest.raises(ValidationError):
        await storage_v1.get(new.id)

    saved = await storage_v2.get(new.id)
    assert isinstance(saved, NativeTopic_v2)
    assert saved.v == 2


@pytest.mark.asyncio
async def test_delete_pages(
    service: NativeTopicService,
):
    # Given: Stored native topic
    topic = v2
    await service.save(topic)
    # And: Stored native page
    page_service = service.native_page_service_factory.create(
        topic.language, topic.level, topic.native_language, topic.id
    )
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
        native_phrase="xxx", native_definition="xxx", native_sentences=[], native_alternatives=[], native_distractors=[]
    )
    native_page = NativeDefinitionGuess.from_page(DefinitionGuess.create(value_create), native_value_create)
    page = await page_service.create(native_page)
    assert await page_service.get(page.id)
    # When: The topic is deleted
    await service.delete(topic.language, topic.level, topic.native_language, topic.id)
    # Then: The page is deleted too
    with pytest.raises(KeyNotExistsException):
        await page_service.get(page.id)

