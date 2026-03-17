from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, KeyNotExistsException
from features.languages import Language
from features.levels import Level
from features.repetitions.repetition_scheduler import RepetitionScheduler

from .repetition_model import PageEvaluation, RepetitionCard, RepetitionCardCreate


class RepetitionService:
    def __init__(self, language_storage: BaseAsyncCollectionStorage):
        self.language_storage = language_storage
        self.scheduler = RepetitionScheduler()

    async def evaluate(
        self, language: Language, level: Level, topic_id: UUID, page_id: UUID, evaluation: PageEvaluation
    ) -> RepetitionCard:
        storage = self.language_storage.get_collection(language, "levels").get_collection(level, RepetitionCard)
        try:
            value = await storage.decorated.get(RepetitionCard.get_id(topic_id, page_id))
            value.evaluations.append(evaluation)
            self.scheduler.update_repetition_card_due(value)
            await storage.decorated.save(value)
        except KeyNotExistsException:
            value_create = RepetitionCardCreate(
                language=language,
                level=level,
                topic_id=topic_id,
                page_id=page_id,
                evaluation=evaluation,
            )
            value = self.scheduler.update_repetition_card_due(value_create)
            await storage.decorated.create(value)
        return value
