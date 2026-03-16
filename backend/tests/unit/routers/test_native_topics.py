from uuid import UUID

import pytest
from ampf.testing import ApiTestClient
from features.native_topics.native_topic_model import NativeTopic, NativeTopicHeader

from haintech.testing import MockerAIModel


@pytest.fixture
def endpoint() -> str:
    return "/api/native-topics/en/A1/pl"

@pytest.fixture
def topic_endpoint(endpoint: str, topic_id: UUID) -> str:
    return f"{endpoint}/{topic_id}"

def test_get_all(client: ApiTestClient, endpoint: str):
    r = client.get_typed_list(endpoint, 200, NativeTopicHeader)
    assert isinstance(r, list)
    assert 0 == len(r)

def test_topic_translate_and_get(client: ApiTestClient, topic_endpoint: str, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        message_containing="Semi-modals",
        response= "{\"title\": \"Czasowniki półmodalne\",  \"description\": \"Czasowniki półmodalne a czyste czasowniki modalne\"}"
    )
    # POST
    r = client.post_typed(topic_endpoint, 200, NativeTopic)
    assert isinstance(r, NativeTopic)
    assert r.native_title == "Czasowniki półmodalne"


    # GET
    r = client.get_typed(topic_endpoint, 200, NativeTopic)
    assert isinstance(r, NativeTopic)
    assert r.native_title == "Czasowniki półmodalne"
