from uuid import UUID

from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_model import Page
from features.repetitions.repetition_model import RepetitionCard
from features.teacher.teacher_model import TeacherDefinitionGuessCreate
from features.workflows.base_workflow import BaseWorkflow, BaseWorkflowSnapshot


class DefinitionGuessWorkflowSnapshot(BaseWorkflowSnapshot):
    phrase: str

    @classmethod
    def create(cls, body: TeacherDefinitionGuessCreate, username: str):
        return cls(**body.model_dump(), username=username)


class DefinitionGuessWorkflow(BaseWorkflow):
    async def execute(
        self, body: TeacherDefinitionGuessCreate, username: str
    ) -> RepetitionCard:
        snapshot = DefinitionGuessWorkflowSnapshot.create(body, username)
        topic = await self._ensure_topic(snapshot)
        await self._ensure_native_topic(snapshot, topic.id)
        definition_guess_create = await self._generate_definition_guess(snapshot, topic.title)
        page = await self._create_page_with_translation(snapshot, topic.id, definition_guess_create)
        return await self._create_repetition_card(snapshot, topic.id, page.id)

    async def _generate_definition_guess(
        self, snapshot: DefinitionGuessWorkflowSnapshot, topic_title: str
    ) -> DefinitionGuessCreate:
        teacher_service = self.teacher_service_factory.create(snapshot.language, snapshot.level)
        return teacher_service.create_definition_guess(topic_title, snapshot.phrase)

    async def _create_page_with_translation(
        self, snapshot: DefinitionGuessWorkflowSnapshot, topic_id: UUID, content: DefinitionGuessCreate
    ) -> Page:
        page_service = self.page_service_factory.create(snapshot.language, snapshot.level, topic_id)
        page = await page_service.post_definition_guess(content)

        native_page = await self.page_translator.translate_page_to_native(
            snapshot.language, snapshot.native_language, page
        )
        native_page_service = self.native_page_service_factory.create(
            snapshot.language, snapshot.level, snapshot.native_language, topic_id
        )
        await native_page_service.create(native_page)
        return page
