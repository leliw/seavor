from fsrs import Scheduler, Card

from features.repetitions.repetition_model import RepetitionCard, RepetitionCardCreate


class RepetitionScheduler:
    def __init__(self):
        self.scheduler = Scheduler()

    def update_repetition_card_due(self, repetition_card: RepetitionCard | RepetitionCardCreate) -> RepetitionCard:
        """Calculate next repetition due date.
        
        Args:
            repetition_card (RepetitionCard | RepetitionCardCreate): The card or creation data to update.

        Returns:
            RepetitionCard: The updated repetition card with new due date and FSRS state.
        """
        if isinstance(repetition_card, RepetitionCardCreate):
            evaluation = repetition_card.evaluation
            card = Card()
        else:
            evaluation = repetition_card.evaluations[-1]
            card = repetition_card.get_card()
        if evaluation:
            card, _ = self.scheduler.review_card(card, evaluation.rating, evaluation.evaluated_at)
        if isinstance(repetition_card, RepetitionCardCreate):
            ret = RepetitionCard.create(repetition_card, card)
        else:
            ret = repetition_card
            ret.set_card(card)
        return ret
