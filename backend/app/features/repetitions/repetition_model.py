from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid5

from features.languages import Language
from features.levels import Level
from fsrs import Rating
from pydantic import BaseModel, Field


class PageEvaluation(BaseModel):
    rating: Rating
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RepetitionCardCreate(BaseModel):
    language: Language
    level: Level
    topic_id: UUID
    page_id: UUID
    evaluation: PageEvaluation


class RepetitionCard(BaseModel):
    language: Language
    level: Level
    topic_id: UUID
    page_id: UUID
    evaluations: list[PageEvaluation] = Field(default_factory=list)
    next_repetition: datetime

    @property
    def id(self) -> UUID:
        return self.get_id(self.topic_id, self.page_id)

    @classmethod
    def get_id(cls, topic_id: UUID, page_id: UUID) -> UUID:
        return uuid5(page_id, str(topic_id))

    @classmethod
    def create(cls, value_create: RepetitionCardCreate) -> "RepetitionCard":
        return cls(
            language=value_create.language,
            level=value_create.level,
            topic_id=value_create.topic_id,
            page_id=value_create.page_id,
            evaluations=[value_create.evaluation],
            next_repetition=datetime.now(timezone.utc) + timedelta(days=1),
        )
