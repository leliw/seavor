import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncCollectionStorage, KeyNotExistsException
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


class RepetitionService:
    def __init__(self, language_storage: BaseAsyncCollectionStorage):
        self.language_storage = language_storage
        self.scheduler = RepetitionScheduler()

    async def get_all(self) -> AsyncGenerator[RepetitionCardHeader]:
        async for language in self.language_storage.decorated.keys():
            try:
                async for repetition in self.get_all_by_language(Language(language)):
                    yield repetition
            except Exception as e:
                _log.warning(e)

    async def get_all_by_language(self, language: Language) -> AsyncGenerator[RepetitionCardHeader]:
        level_storage = self.language_storage.get_collection(language, "levels")
        async for level in level_storage.decorated.keys():
            try:
                async for repetition in self.get_all_by_level(language, Level(level)):
                    yield repetition
            except Exception as e:
                _log.warning(e)

    async def get_all_by_level(self, language: Language, level: Level) -> AsyncGenerator[RepetitionCardHeader]:
        level_storage = self.language_storage.get_collection(language, "levels")
        repetition_storage = level_storage.get_collection(level, RepetitionCard)
        async for repetition in repetition_storage.decorated.get_all():
            yield repetition

    async def evaluate(
        self, language: Language, level: Level, topic_id: UUID, page_id: UUID, evaluation: PageEvaluation
    ) -> RepetitionCard:
        level_storage = self.language_storage.get_collection(language, "levels")
        repetition_storage = level_storage.get_collection(level, RepetitionCard)
        try:
            value = await repetition_storage.decorated.get(RepetitionCard.get_id(topic_id, page_id))
            value.evaluations.append(evaluation)
            self.scheduler.update_repetition_card_due(value)
            await repetition_storage.decorated.save(value)
        except KeyNotExistsException:
            value_create = RepetitionCardCreate(
                language=language,
                level=level,
                topic_id=topic_id,
                page_id=page_id,
                evaluation=evaluation,
            )
            value = self.scheduler.update_repetition_card_due(value_create)
            await asyncio.gather(
                self.language_storage.decorated.save(LanguageStatus(language=language)),
                level_storage.decorated.save(LevelStatus(level=level)),
                repetition_storage.decorated.create(value),
            )
        return value

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
        for i in range(2*24*12):
            groups.append(curr)
            curr = curr + timedelta(minutes=5)
        # Next month per 1 day
        for i in range(31):
            curr = curr + timedelta(days=1)
            groups.append(curr)
        return groups
