import asyncio
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
    LanguageStatus,
    LevelStatus,
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
        return RepetitionService(
            self.user_storage.get_collection(username, "languages"),
            self.user_storage.get_collection(username, RepetitionCard),
        )


class RepetitionService:
    def __init__(
        self,
        language_storage: BaseAsyncCollectionStorage[LanguageStatus],
        new_storage: BaseAsyncCollectionStorage[RepetitionCard],
    ):
        self.language_storage = language_storage
        self.new_storage = new_storage
        self.scheduler = RepetitionScheduler()

    async def get_all(self) -> AsyncGenerator[RepetitionCardHeader]:
        async for language in self.language_storage.keys():
            try:
                async for repetition in self.get_all_by_language(Language(language)):
                    yield repetition
            except Exception as e:
                _log.warning(e)

    async def get_all_by_language(self, language: Language) -> AsyncGenerator[RepetitionCardHeader]:
        level_storage = self.language_storage.get_collection(language, "levels")
        async for level in level_storage.keys():
            try:
                async for repetition in self.get_all_by_level(language, Level(level)):
                    yield repetition
            except Exception as e:
                _log.warning(e)

    async def get_all_by_level(self, language: Language, level: Level) -> AsyncGenerator[RepetitionCardHeader]:
        level_storage = self.language_storage.get_collection(language, "levels")
        repetition_storage = level_storage.get_collection(level, RepetitionCard)
        async for repetition in repetition_storage.get_all():
            yield repetition

    async def create(self, value_create: RepetitionCardCreate) -> RepetitionCard:
        level_storage = self.language_storage.get_collection(value_create.language, "levels")
        repetition_storage = level_storage.get_collection(value_create.level, RepetitionCard)
        value = self.scheduler.update_repetition_card_due(value_create)
        for res in await asyncio.gather(
            self.language_storage.save(LanguageStatus(language=value_create.language)),
            level_storage.save(LevelStatus(level=value_create.level)),
            repetition_storage.create(value),
            self.new_storage.create(value),
            return_exceptions=True,
        ):
            if isinstance(res, Exception):
                _log.warning(f"Error creating repetition card: {res}")
        return value

    async def evaluate(
        self, language: Language, level: Level, topic_id: UUID, page_id: UUID, evaluation: PageEvaluation
    ) -> RepetitionCard:
        level_storage = self.language_storage.get_collection(language, "levels")
        repetition_storage = level_storage.get_collection(level, RepetitionCard)
        try:
            value = await repetition_storage.get(RepetitionCard.get_id(topic_id, page_id))
            value.evaluations.append(evaluation)
            self.scheduler.update_repetition_card_due(value)
            for res in await asyncio.gather(
                repetition_storage.save(value),
                self.new_storage.save(value),
                return_exceptions=True,
            ):
                if isinstance(res, Exception):
                    _log.warning(f"Error saving repetition card: {res}")
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
        schedule = {}
        groups = self.create_groups()
        async for rch in self.get_all():
            for group in groups:
                if rch.due <= group:
                    s_group = str(group)
                    schedule[s_group] = schedule.get(s_group, 0) + 1
                    break
        return RepetitionSchedule(root=schedule)

    def create_groups(self) -> list[datetime]:
        groups = []
        curr = datetime.now(timezone.utc)
        # First 2 days per 5 minutes (12 times per hour)
        for i in range(2 * 24 * 12):
            groups.append(curr)
            curr = curr + timedelta(minutes=5)
        # Next month per 1 day
        for i in range(31):
            curr = curr + timedelta(days=1)
            groups.append(curr)
        return groups
