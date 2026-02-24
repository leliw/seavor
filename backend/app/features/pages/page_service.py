import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import UUID

from ampf.base import BaseAsyncFactory
from pydantic import TypeAdapter
from features.pages.page_model import (
    GapFillChoiceExercise,
    GapFillChoiceExerciseCreate,
    GapFillChoiceExercisePatch,
    GapFillChoiceExercisePut,
    Page,
    PageHeader,
)
from features.languages import Language
from features.levels import Level
from shared.audio_files.audio_file_service import AudioFileService

PageAdapter = TypeAdapter(Page)


class PageService:
    def __init__(
        self,
        factory: BaseAsyncFactory,
        audio_file_service: AudioFileService,
        target_language: Language,
        level: Level,
        topic_id: UUID,
    ):
        self.storage = factory.create_storage(
            f"target-languages/{target_language}/levels/{level}/topics/{topic_id}/pages",
            PageAdapter,  # type: ignore
            "id",
        )
        self.storage.from_storage = lambda value: PageAdapter.validate_python(value)  # type: ignore

        self.audio_file_service = audio_file_service
        self.target_language_code = target_language

    async def get_all(self) -> AsyncGenerator[PageHeader]:
        async for value in self.storage.get_all():
            yield PageHeader(**value.model_dump())

    async def post(self, value: GapFillChoiceExerciseCreate) -> Page:
        new_exercise = GapFillChoiceExercise.create(value)

        texts_to_synthesize = []
        if new_exercise.target_sentence:
            texts_to_synthesize.append(new_exercise.target_sentence)
        if new_exercise.target_explanation:
            texts_to_synthesize.append(new_exercise.target_explanation)
        if new_exercise.target_hint:
            texts_to_synthesize.append(new_exercise.target_hint)
        if new_exercise.target_distractors_explanation:
            for distractor in new_exercise.target_distractors_explanation.items():
                texts_to_synthesize.append(distractor[1])

        audio_file_names = await asyncio.gather(
            *[
                self.audio_file_service.generate_and_upload(text=text, language=self.target_language_code)
                for text in texts_to_synthesize
            ]
        )

        audio_file_index = 0
        if new_exercise.target_sentence:
            new_exercise.target_sentence_audio_file_name = audio_file_names[audio_file_index]
            audio_file_index += 1
        if new_exercise.target_explanation:
            new_exercise.target_explanation_audio_file_name = audio_file_names[audio_file_index]
            audio_file_index += 1
        if new_exercise.target_hint:
            new_exercise.target_hint_audio_file_name = audio_file_names[audio_file_index]
            audio_file_index += 1
        if new_exercise.target_distractors_explanation:
            new_exercise.target_distractors_explanation_audio_file_name = {}
            for distractor in new_exercise.target_distractors_explanation.items():
                new_exercise.target_distractors_explanation_audio_file_name[distractor[0]] = audio_file_names[
                    audio_file_index
                ]
                audio_file_index += 1

        await self.storage.create(new_exercise)
        return new_exercise

    async def get(self, key: UUID) -> Page:
        return await self.storage.get(key)

    async def put(self, key: UUID, value: GapFillChoiceExercisePut) -> None:
        if key != value.id:
            raise ValueError("The key in the path must match the id in the request body.")

        existing_exercise = await self.storage.get(key)
        updated_exercise = existing_exercise.model_copy(update=value.model_dump(exclude_unset=True))
        updated_exercise.updated_at = datetime.now(timezone.utc)

        # For simplicity, audio files are not regenerated on PUT.
        # If audio regeneration is needed, a more complex logic similar to POST would be required.

        await self.storage.put(key, updated_exercise)

    async def patch(self, uid: UUID, value_patch: GapFillChoiceExercisePatch) -> Page:
        value = await self.storage.get(uid)
        value.patch(value_patch)
        await self.storage.put(uid, value)
        return value

    async def delete(self, key: UUID) -> None:
        exercise_to_delete = await self.storage.get(key)

        audio_files_to_delete = []
        if exercise_to_delete.target_sentence_audio_file_name:
            audio_files_to_delete.append(exercise_to_delete.target_sentence_audio_file_name)
        if exercise_to_delete.target_explanation_audio_file_name:
            audio_files_to_delete.append(exercise_to_delete.target_explanation_audio_file_name)
        if exercise_to_delete.target_hint_audio_file_name:
            audio_files_to_delete.append(exercise_to_delete.target_hint_audio_file_name)
        if exercise_to_delete.target_distractors_explanation_audio_file_name:
            for distractor in exercise_to_delete.target_distractors_explanation_audio_file_name.items():
                if distractor[1]:
                    audio_files_to_delete.append(distractor[1])

        for file_name in audio_files_to_delete:
            self.audio_file_service.delete(name=file_name)
        # await asyncio.gather(
        #     *[self.audio_file_service.delete(name=file_name) for file_name in audio_files_to_delete]
        # )
        await self.storage.delete(key)
