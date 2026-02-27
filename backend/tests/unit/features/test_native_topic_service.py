from datetime import datetime
from uuid import uuid4

from ampf.base import BaseAsyncFactory, BaseAsyncStorage
from pydantic import ValidationError
import pytest
import pytest_asyncio

from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic_v1, NativeTopic_v2
from features.native_topics.native_topic_service import NativeTopicService
from features.topics.topic_model import TopicType

target_language = Language.EN
level = Level.A1
native_language = Language.PL
v1 = NativeTopic_v1(
    id=uuid4(),
    target_language_code=target_language,
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
    return NativeTopicService(factory)


@pytest_asyncio.fixture
async def storage_v2(service: NativeTopicService):
    return service._get_storage(target_language, level, native_language)


@pytest.mark.asyncio
async def test_save_old_read_new(service: NativeTopicService, storage_v1: BaseAsyncStorage[NativeTopic_v1]):
    # Given: A session stored in previous format
    old = v1
    await storage_v1.save(old)
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
