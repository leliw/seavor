import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, KeyNotExistsException
from core.users.user_model import UserInDB
from features.languages import Language
from features.levels import Level
from features.repetitions.repetition_scheduler import RepetitionScheduler

from .repetition_model import (
    PageEvaluation,
    RepetitionCard,
    RepetitionCardCreate,
    RepetitionCardHeader,
    RepetitionSchedule,
)

_log = logging.getLogger(__name__)


@dataclass
class RepetitionServiceFactory:
    user_storage: BaseAsyncCollectionStorage[UserInDB]

    def create(self, username: str) -> "RepetitionService":
        return RepetitionService(self.user_storage.get_collection(username, RepetitionCard))


class RepetitionService:
    def __init__(self, new_storage: BaseAsyncCollectionStorage[RepetitionCard]):
        self.new_storage = new_storage
        self.scheduler = RepetitionScheduler()

    async def get_all(self) -> AsyncGenerator[RepetitionCardHeader]:
        async for repetition in self.new_storage.get_all():
            yield repetition

    async def get(self, id: UUID) -> RepetitionCard:
        return await self.new_storage.get(id)

    async def create(self, value_create: RepetitionCardCreate) -> RepetitionCard:
        value = self.scheduler.update_repetition_card_due(value_create)
        await self.new_storage.create(value)
        return value

    async def evaluate(
        self, language: Language, level: Level, topic_id: UUID, page_id: UUID, evaluation: PageEvaluation
    ) -> RepetitionCard:
        try:
            value = await self.get(RepetitionCard.get_id(topic_id, page_id))
            value.evaluations.append(evaluation)
            self.scheduler.update_repetition_card_due(value)
            await self.new_storage.save(value)
            return value
        except KeyNotExistsException:
            return await self.create(
                RepetitionCardCreate(
                    language=language,
                    level=level,
                    topic_id=topic_id,
                    page_id=page_id,
                    evaluation=evaluation,
                )
            )

    async def get_schedule(self) -> RepetitionSchedule:
        schedule: dict[str, int] = {}
        groups = self.create_groups()
        async for rch in self.get_all():
            for group in groups:
                if rch.due <= group:
                    s_group = str(group)
                    schedule[s_group] = schedule.get(s_group, 0) + 1
                    break
        return RepetitionSchedule(root=dict(sorted(schedule.items())))

    def create_groups(self) -> list[datetime]:
        groups = []
        curr = datetime.now(timezone.utc)
        # First 2 days per 5 minutes (12 times per hour)
        for i in range(2 * 24 * 12):
            groups.append(curr)
            curr = curr + timedelta(minutes=5)
        # Next month per 1 day
        for i in range(31):
            groups.append(curr)
            curr = curr + timedelta(days=1)
        return groups
