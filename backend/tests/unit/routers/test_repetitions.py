from uuid import UUID

from ampf.base import BaseAsyncFactory
from fsrs import Rating
import pytest
from ampf.testing import ApiTestClient
from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate, Sentence
from features.repetitions.repetition_model import PageEvaluation, RepetitionCard


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
    evaluation = PageEvaluation(rating=Rating.Good)
    # When: Send evaluation
    card = client.post_typed(
        f"/api/topics/en/A1/{topic_id}/pages/{page.id}/evaluate",
        200,
        RepetitionCard,
        json=evaluation,
        headers=headers,
    )
    # Then: Card is returned
    assert card.due is not None
    assert card.evaluations[0].rating == evaluation.rating
    assert card.evaluations[0].evaluated_at is not None
    # And: It is saved
    storage = factory.create_storage("users/test/languages/en/levels/A1/repetitions", RepetitionCard, "id")
    stored = await storage.get(card.id)
    assert stored.due is not None


def test_send_evaluation_again(
    client: ApiTestClient,
    headers: dict[str, str],
    topic_id: UUID,
    definition_guess_create: DefinitionGuessCreate,
):
    # Given: A topic with definition guess page
    page = client.post_typed(f"/api/topics/en/A1/{topic_id}/pages", 200, DefinitionGuess, json=definition_guess_create)
    # And: An page evaluated once
    client.post_typed(
        f"/api/topics/en/A1/{topic_id}/pages/{page.id}/evaluate",
        200,
        RepetitionCard,
        json=PageEvaluation(rating=Rating.Good),
        headers=headers,
    )
    # When: Send evaluation again
    card = client.post_typed(
        f"/api/topics/en/A1/{topic_id}/pages/{page.id}/evaluate",
        200,
        RepetitionCard,
        json=PageEvaluation(rating=Rating.Again),
        headers=headers,
    )
    # Then: Card is returned
    assert card.due is not None
    assert card.evaluations[1].rating == Rating.Again
    assert card.evaluations[1].evaluated_at is not None
