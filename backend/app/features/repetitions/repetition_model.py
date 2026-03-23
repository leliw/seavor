from datetime import datetime, timezone
from uuid import UUID, uuid5

from features.languages import Language
from features.levels import Level
from fsrs import Card, Rating, State
from pydantic import BaseModel, Field, RootModel, computed_field

from features.pages.page_base_model import PageType


class LanguageStatus(BaseModel):
    language: Language


class LevelStatus(BaseModel):
    level: Level


class PageEvaluation(BaseModel):
    rating: Rating
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RepetitionCardCreate(BaseModel):
    language: Language
    level: Level
    topic_id: UUID
    page_id: UUID
    type: PageType = PageType.DEFINITION_GUESS
    evaluation: PageEvaluation


class RepetitionCardHeader(BaseModel):
    language: Language
    level: Level
    topic_id: UUID
    page_id: UUID
    type: PageType = PageType.DEFINITION_GUESS
    due: datetime

    @computed_field
    def id(self) -> UUID:
        return self.get_id(self.topic_id, self.page_id)

    @classmethod
    def get_id(cls, topic_id: UUID, page_id: UUID) -> UUID:
        return uuid5(page_id, str(topic_id))


class RepetitionCard(RepetitionCardHeader):
    evaluations: list[PageEvaluation] = Field(default_factory=list)

    #### FSRS fields ->
    card_id: int
    state: State
    step: int | None = None
    stability: float | None = None
    difficulty: float | None = None
    #### <-

    def get_card(self) -> Card:
        return Card(
            card_id=self.card_id,
            state=self.state,
            step=self.step,
            stability=self.stability,
            difficulty=self.difficulty,
            due=self.due,
            last_review=self.evaluations[-1].evaluated_at if self.evaluations else None,
        )

    def set_card(self, card: Card) -> None:
        self.card_id = card.card_id
        self.state = card.state
        self.step = card.step
        self.stability = card.stability
        self.difficulty = card.difficulty
        self.due = card.due

    @classmethod
    def create(cls, value_create: RepetitionCardCreate, card: Card) -> "RepetitionCard":
        return cls(
            language=value_create.language,
            level=value_create.level,
            topic_id=value_create.topic_id,
            page_id=value_create.page_id,
            evaluations=[value_create.evaluation],
            card_id=card.card_id,
            state=card.state,
            step=card.step,
            stability=card.stability,
            difficulty=card.difficulty,
            due=card.due,
        )

class RepetitionSchedule(RootModel):
    root: dict[str, int]
