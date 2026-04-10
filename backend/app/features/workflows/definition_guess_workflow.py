from typing import Self
from uuid import UUID

from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_model import Page
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.topics.topic_model import Topic
from features.workflows.base_workflow import BaseWorkflow, BaseWorkflowPageSnapshot


class DefinitionGuessSnapshotInitial(BaseWorkflowPageSnapshot):
    phrase: str

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str) -> Self:
        return cls(**body.model_dump(), username=username)


class DefinitionGuessSnapshotTopicCreated(DefinitionGuessSnapshotInitial):
    topic_title: str

    @classmethod
    def create(cls, snapshot: DefinitionGuessSnapshotInitial, topic: Topic) -> Self:
        previous_snapshot_dict = snapshot.model_dump(exclude_defaults=True)
        return cls(**previous_snapshot_dict, topic_id=topic.id, topic_title=topic.title)


class DefinitionGuessSnapshotPageCreated(DefinitionGuessSnapshotTopicCreated):
    @classmethod
    def create(cls, snapshot: DefinitionGuessSnapshotTopicCreated, page_id: UUID) -> Self:
        previous_snapshot_dict = snapshot.model_dump(exclude_defaults=True)
        return cls(**previous_snapshot_dict, page_id=page_id)


class DefinitionGuessWorkflow(BaseWorkflow):
    async def execute(self, body: TeacherDefinitionGuessCreate, username: str) -> RepetitionCard:
        snapshot = DefinitionGuessSnapshotInitial.create(body, username)
        topic = await self._ensure_topic(snapshot)
        await self._ensure_native_topic(snapshot, topic.id)
        snapshot = DefinitionGuessSnapshotTopicCreated.create(snapshot, topic)
        definition_guess_create = await self._generate_definition_guess(snapshot)
        page = await self._create_page_with_translation(snapshot, definition_guess_create)
        snapshot = DefinitionGuessSnapshotPageCreated.create(snapshot, page.id)
        return await self._create_repetition_card(snapshot)

    async def _generate_definition_guess(self, snapshot: DefinitionGuessSnapshotTopicCreated) -> DefinitionGuessCreate:
        teacher_service = self.teacher_service_factory.create(snapshot.language, snapshot.level)
        return await teacher_service.create_definition_guess(snapshot.topic_title, snapshot.phrase)

    async def _create_page_with_translation(
        self, snapshot: DefinitionGuessSnapshotTopicCreated, content: DefinitionGuessCreate
    ) -> Page:
        page_service = self.page_service_factory.create(snapshot.language, snapshot.level, snapshot.required_topic_id)
        page = await page_service.post_definition_guess(content)

        native_page = await self.page_translator.translate_page_to_native(
            snapshot.language, snapshot.native_language, page
        )
        native_page_service = self.native_page_service_factory.create(
            snapshot.language, snapshot.level, snapshot.native_language, snapshot.required_topic_id
        )
        await native_page_service.create(native_page)
        return page
