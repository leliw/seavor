from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.native_topics.native_topic_model import NativeTopic, NativeTopicHeader
from features.topics.topic_model import Topic, TopicCreate

@pytest.fixture
def topic_id(client: ApiTestClient, topic_create: TopicCreate) -> UUID:
    r = client.post_typed("/api/topics", 200, Topic, json=topic_create)
    return r.id


@pytest.fixture
def endpoint() -> str:
    return "/api/native-topics/en/A1/pl"


def test_get_all(client: ApiTestClient, endpoint: str):
    r = client.get_typed_list(endpoint, 200, NativeTopicHeader)
    assert isinstance(r, list)
    assert 0 == len(r)

def test_get_(client: ApiTestClient, endpoint: str, topic_id: UUID):
    r = client.get_typed(f"{endpoint}/{topic_id}", 200, NativeTopic)
    assert isinstance(r, NativeTopic)
