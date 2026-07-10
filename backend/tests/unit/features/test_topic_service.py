from ampf.base import KeyNotExistsException
import pytest

from features.languages import Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_model import InfoPageCreate
from features.topics.topic_model import TopicCreate, TopicType
from features.topics.topic_service import TopicService


@pytest.mark.asyncio
async def test_delete_topic(
    topic_service: TopicService,
):
    # Given: Stored topic
    topic_create = TopicCreate(
        language=Language.EN,
        level=Level.A1,
        title="tt",
        description="td",
        type=TopicType.VOCABULARY,
        private=False,
    )
    topic = await topic_service.create(topic_create)
    # And: Stored pages
    page_service = topic_service.page_service_factory.create(topic.id)
    page_create = InfoPageCreate(
        language=Language.EN,
        level=Level.A1,
        order=1,
        title="pt",
        content="pc",
    )
    page = await page_service.post(page_create)
    assert await page_service.get(page.id)
    # And: Stored native topic
    native_topic_service = topic_service.native_topic_service
    native_topic = NativeTopic.from_topic(topic, Language.PL, "nt", "nd")
    await native_topic_service.create(native_topic)
    assert await native_topic_service.get(Language.PL, native_topic.id)
    # When: The topic is deleted
    await topic_service.delete(topic.id)
    # Then: The topic is deleted
    with pytest.raises(KeyNotExistsException):
        await topic_service.get(topic.id)
    # And: The pages are deleted too
    with pytest.raises(KeyNotExistsException):
        await page_service.get(page.id)
    # And: The native topics are deleted too
    with pytest.raises(KeyNotExistsException):
        await native_topic_service.get(Language.PL, native_topic.id)
        
