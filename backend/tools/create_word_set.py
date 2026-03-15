import asyncio
import logging
from pathlib import Path

from ampf.local import LocalFactory

import _set_path as _set_path
from ampf.testing import ApiTestClient
from app_state import AppState
from dependencies import get_image_generator, get_image_service
from features.languages import Language
from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuess, DefinitionGuessCreate
from features.pages.page_base_model import PageHeader
from features.teacher.teacher_service import TeacherService
from features.topics.topic_model import Topic, TopicType
from haintech.ai.google_genai import GoogleAIModel
from main import app
from pydantic import BaseModel
from shared.prompts.prompt_service import PromptService

_log = logging.getLogger(__name__)


class CreatorSnapshot(BaseModel):
    language: Language
    native_languages: list[Language]
    theme: str
    type: TopicType
    word_count: int

    word_set: set[str] | None = None
    extra_words_round: int = 0

    levels: dict[Level, list[DefinitionGuessCreate]] | None = None

    topic_urls: dict[Level, str] | None = None
    page_urls: list[str] | None = None

    native_topic_urls: dict[Level, str] | None = None
    native_page_urls: list[str] | None = None


class Creator:
    def __init__(
        self,
        app_state: AppState,
        client: ApiTestClient,
    ):
        self.app_state = app_state
        self.client = client
        self.ai_model = GoogleAIModel(parameters={"temperature": 0.1})
        self.teacher_service = None

    def get_teacher_service(self, snapshot: CreatorSnapshot) -> TeacherService:
        if not self.teacher_service:
            self.teacher_service = TeacherService(
                PromptService("./app/prompts"), ai_model=self.ai_model, language=snapshot.language
            )
        return self.teacher_service

    def create_word_set(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        snapshot.word_set = set(
            self.get_teacher_service(snapshot).generate_word_set(snapshot.theme, snapshot.word_count)
        )
        return snapshot

    def create_definition_guess_pages(
        self, snapshot: CreatorSnapshot, word_set: set[str] | None = None
    ) -> CreatorSnapshot:
        if not snapshot.levels:
            snapshot.levels = {level: [] for level in Level.ALL.to_list()}
        word_set = word_set or snapshot.word_set
        assert word_set
        for word in word_set:
            print(word)
            # Generate page for each word
            dgc = self.get_teacher_service(snapshot).create_definition_guess(snapshot.theme, word, snapshot.extra_words_round)
            # Group pages by level
            snapshot.levels[dgc.level].append(dgc)
        return snapshot

    def create_extra_words_definition_guess_pages(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        extra_words = []
        assert snapshot.word_set
        assert snapshot.levels
        for level in snapshot.levels:
            for dgc in snapshot.levels[level]:
                if dgc.order == snapshot.extra_words_round:
                    # Only added in the previous loop
                    for a in [*dgc.alternatives, *dgc.distractors]:
                        extra_word = a.value
                        if extra_word not in snapshot.word_set and extra_word not in extra_words:
                            extra_words.append(extra_word)
        print(extra_words)
        filtered_words = self.get_teacher_service(snapshot).filter_word_set(snapshot.theme, extra_words)
        print(filtered_words)
        snapshot.extra_words_round += 1
        return self.create_definition_guess_pages(snapshot, set(filtered_words))

    def create_topics(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        assert snapshot.levels
        snapshot.topic_urls = {}
        for level, dgcs in snapshot.levels.items():
            if len(dgcs) == 0:
                continue
                # Create topic for level
            topic_url = self.create_topic(snapshot, level)
            snapshot.topic_urls[level] = topic_url
        return snapshot

    def create_topic(self, snapshot: CreatorSnapshot, level: Level) -> str:
        topic_create = self.get_teacher_service(snapshot).create_topic_create(level, snapshot.type, snapshot.theme)
        topic = self.client.post_typed("/api/topics", 200, Topic, json=topic_create)
        return f"/api/topics/{topic.language}/{topic.level}/{topic.id}"

    def create_pages(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        assert snapshot.topic_urls
        assert snapshot.levels
        snapshot.page_urls = []
        for level, topic_url in snapshot.topic_urls.items():
            for dgc in snapshot.levels[level]:
                # Save page in topic
                page_header = client.post_typed(f"{topic_url}/pages", 200, PageHeader, json=dgc)
                page_url = f"{topic_url}/pages/{page_header.id}"
                snapshot.page_urls.append(page_url)
        return snapshot

    def create_images(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        assert snapshot.page_urls
        for page_url in snapshot.page_urls:
            page = client.get_typed(page_url, 200, DefinitionGuess)
            if not page.image_names:
                s = "Create graphics for a language learning application. Blur the response text if it exists on image."
                u = f"Create **{page.phrase}** image by definition: {page.definition}"
                image_name = asyncio.run(image_service.generate_and_upload(f"{s}\n\n{u}", page.language))
                client.patch(page_url, 200, json={"image_names": [image_name]})
                _log.info("Created image: %s", image_name)
        return snapshot

    def translate_topics(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        assert snapshot.topic_urls
        snapshot.native_topic_urls = {}
        for level, topic_url in snapshot.topic_urls.items():
            topic_url = Path(topic_url)
            topic_id = topic_url.parts[5]
            for native_language in snapshot.native_languages:
                if native_language == snapshot.language:
                    continue
                # Create native topic
                url = f"/api/native-topics/{snapshot.language}/{level}/{native_language}/{topic_id}"
                self.client.post(url, 200)
                snapshot.native_topic_urls[level] = url
        return snapshot

    def translate_pages(self, snapshot: CreatorSnapshot) -> CreatorSnapshot:
        assert snapshot.topic_urls
        snapshot.native_page_urls = []
        for level, topic_url in snapshot.topic_urls.items():
            topic = client.get_typed(topic_url, 200, Topic)
            target_language = topic.language
            level = topic.level
            pages = client.get_typed_list(f"{topic_url}/pages", 200, PageHeader)
            for native_language in snapshot.native_languages or [Language.EN, Language.PL]:
                if native_language == topic.language:
                    continue
                # Create native topic pages
                for page in pages:
                    url = f"/api/native-topics/{target_language}/{level}/{native_language}/{topic.id}/pages/{page.id}"
                    client.post(url, 200)
                    snapshot.native_page_urls.append(url)
        return snapshot


if __name__ == "__main__":
    with ApiTestClient(app) as client:
        app_state: AppState = client.app.state.app_state  # type: ignore
        snapshot_storage = factory = LocalFactory(app_state.config.data_dir).create_storage(
            "snapshots", CreatorSnapshot, key = lambda x: f"{x.language.value}-{x.type}_{x.theme}"
        )
        image_gen_service = get_image_generator()
        image_service = get_image_service(app_state, image_gen_service)
        creator = Creator(app_state, client)
        # snapshot = snapshot_storage.get("en")
        snapshot = CreatorSnapshot(
            language=Language.EN,
            theme="Air travel and airports",
            type=TopicType.VOCABULARY,
            native_languages=[Language.EN, Language.PL],
            word_count=10,
        )
        snapshot = creator.create_word_set(snapshot)
        snapshot_storage.save(snapshot)
        print(snapshot.word_set)
        snapshot = creator.create_definition_guess_pages(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.create_extra_words_definition_guess_pages(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.create_topics(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.create_pages(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.create_images(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.translate_topics(snapshot)
        snapshot_storage.save(snapshot)
        snapshot = creator.translate_pages(snapshot)
        snapshot_storage.save(snapshot)
