from uuid import UUID

from ampf.base import BaseAsyncFactory
import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, Sentence
from features.repetitions.repetition_model import PageEvaluation, RepetitionStatus


@pytest.fixture
def definition_guess_create() -> DefinitionGuessCreate:
    return DefinitionGuessCreate(
        language=Language.EN,
        level=Level.A1,
        order=1,
        phrase="Hello",
        definition="The common greeting.",
        sentences=[
            Sentence(
                text_with_gap="[___] World!",
                gap_filler_form="Hello",
            )
        ],
        alternatives=[],
        distractors=[],
        hint="Starts with W",
    )


@pytest.mark.asyncio
async def test_send_evaluation(
    client: ApiTestClient,
    headers: dict[str, str],
    factory: BaseAsyncFactory,
    topic_id: UUID,
    definition_guess_create: DefinitionGuessCreate,
):
    # Given: A topic with definition guess page
    page = client.post_typed(f"/api/topics/en/A1/{topic_id}/pages", 200, DefinitionGuess, json=definition_guess_create)
    # And: An page evaluation
    evaluation = PageEvaluation(rate=0)
    # When: Send evaluation
    status = client.post_typed(
        f"/api/topics/en/A1/{topic_id}/pages/{page.id}/evaluate",
        200,
        RepetitionStatus,
        json=evaluation,
        headers=headers,
    )
    # Then: Status is returned
    assert status.next_repetition is not None
    assert status.evaluations[0].rate == evaluation.rate
    assert status.evaluations[0].evaluated_at is not None
    # And: It is saved
    storage = factory.create_storage("users/test/languages/en/levels/A1/repetitions", RepetitionStatus, "id")
    stored = await storage.get(status.id)
    assert stored.next_repetition is not None

