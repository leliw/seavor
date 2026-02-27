import logging
from typing import List, Optional, Tuple

import _set_path as _set_path
from ampf.testing import ApiTestClient
from app_state import AppState
from features.languages import Language
from features.levels import Level
from features.pages.page_model import PageHeader
from features.teacher.teacher_service import TeacherService
from features.topics.topic_model import Topic, TopicCreate, TopicType
from main import app
from shared.prompts.prompt_service import PromptService

_log = logging.getLogger(__name__)


class Creator:
    def __init__(self, app_state: AppState, client: ApiTestClient):
        self.app_state = app_state
        self.client = client

    def create_topic(self, target_language: Language, level: Level, topic_name: str) -> str:
        teacher_service = TeacherService(PromptService("./app/prompts"), target_language, level)
        topic_description = teacher_service.create_topic_description(topic_name)
        topic_create = TopicCreate(
            language=target_language,
            level=level,
            title=topic_name,
            description=topic_description,
            type=TopicType.GRAMMAR,
        )
        topic = self.client.post_typed("/api/topics", 200, Topic, json=topic_create)
        target_language = topic.language
        level = topic.level
        topic_url = f"/api/topics/{target_language}/{level}/{topic.id}"
        _log.warning("Created topic: %s", topic_url)
        return topic_url

    def _create_teacher_service_and_topic(self, topic_url: str) -> Tuple[TeacherService, Topic]:
        topic = self.client.get_typed(topic_url, 200, Topic)
        target_language = topic.language
        level = topic.level
        return (TeacherService(PromptService("./app/prompts"), target_language, level), topic)

    def translate_topic(self, topic_url: str, native_languages: Optional[List[Language]] = None):
        topic = self.client.get_typed(topic_url, 200, Topic)
        target_language = topic.language
        level = topic.level
        for native_language in native_languages or [Language.EN, Language.PL]:
            if native_language == topic.language:
                continue
            # Create native topic
            self.client.post(f"/api/native-topics/{target_language}/{level}/{native_language}/{topic.id}", 200)

    def create_info_pages(self, topic_url: str, native_languages: Optional[List[Language]] = None):
        teacher_service, topic = self._create_teacher_service_and_topic(topic_url)
        pages = teacher_service.create_info_pages(topic.title)
        for page in pages:
            self.client.post_typed(f"{topic_url}/pages", 200, PageHeader, json=page)
            _log.info("Created page: %s", page.title)


    def translate_topic_pages(self, topic_url: str, native_languages: Optional[List[Language]] = None):
        topic = client.get_typed(topic_url, 200, Topic)
        target_language = topic.language
        level = topic.level
        pages = client.get_typed_list(f"{topic_url}/pages", 200, PageHeader)
        for native_language in native_languages or [Language.EN, Language.PL]:
            if native_language == topic.language:
                continue
            # Create native topic pages
            for page in pages:
                client.post(
                    f"/api/native-topics/{target_language}/{level}/{native_language}/{topic.id}/pages/{page.id}", 200
                )


if __name__ == "__main__":
    with ApiTestClient(app) as client:
        app_state: AppState = client.app.state.app_state  # type: ignore
        creator = Creator(app_state, client)
        topic_url = creator.create_topic(Language.EN, Level.A1, "There is / There are")
        # topic_url = "/api/topics/en/A1/24c6f235-449f-424f-839b-094ab0b67ccf"
        creator.translate_topic(topic_url)
        creator.create_info_pages(topic_url)
        creator.translate_topic_pages(topic_url)

# 1. Create a topic
# 2. Generate pages
# 3. Add pages to topic
# 4. Update images and voices
# 5. Add translations
