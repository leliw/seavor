import json
import logging
from typing import List, Optional

import _set_path as _set_path
from ampf.testing import ApiTestClient
from app_state import AppState
from features.pages.page_model import GapFillChoiceExercise, GapFillChoiceExerciseCreate, PageHeader
from features.languages import Language
from features.topics.topic_model import Topic_v1, TopicCreate
from main import app

_log = logging.getLogger(__name__)

response = """
[
  {
    "level": "A1",
    "order": 1,
    "target_language": "en",
    "target_sentence": "You ____ finish your homework before you watch TV.",
    "gap_marker": "____",
    "options": ["have to", "might", "used to", "be able to"],
    "correct_index": 0,
    "target_explanation": "\\"Have to\\" expresses obligation or necessity. In this sentence, it shows that finishing homework is necessary before watching TV.",
    "target_distractors_explanation": {
      "1": "\\"Might\\" expresses possibility, not obligation.",
      "2": "\\"Used to\\" refers to past habits or states, not present obligation.",
      "3": "\\"Be able to\\" expresses ability, not necessity."
    },
    "target_hint": "Use a semi-modal that shows obligation."
  },
  {
    "level": "A2",
    "order": 2,
    "target_language": "en",
    "target_sentence": "When I was a child, I ____ play outside every day.",
    "gap_marker": "____",
    "options": ["used to", "have to", "am able to", "ought to"],
    "correct_index": 0,
    "target_explanation": "\\"Used to\\" describes past habits or repeated actions that are no longer true.",
    "target_distractors_explanation": {
      "1": "\\"Have to\\" expresses obligation, not past habit.",
      "2": "\\"Am able to\\" expresses present ability, not past repeated actions.",
      "3": "\\"Ought to\\" expresses advice or moral obligation."
    },
    "target_hint": "Choose the semi-modal for past habits."
  },
  {
    "level": "B1",
    "order": 3,
    "target_language": "en",
    "target_sentence": "You ____ see a doctor if the pain continues.",
    "gap_marker": "____",
    "options": ["ought to", "used to", "be used to", "have got"],
    "correct_index": 0,
    "target_explanation": "\\"Ought to\\" is used to give advice or make recommendations.",
    "target_distractors_explanation": {
      "1": "\\"Used to\\" refers to past habits.",
      "2": "\\"Be used to\\" means being accustomed to something.",
      "3": "\\"Have got\\" expresses possession, not advice."
    },
    "target_hint": "Choose the semi-modal that gives advice."
  },
  {
    "level": "B2",
    "order": 4,
    "target_language": "en",
    "target_sentence": "She didn’t ____ understand the instructions clearly, so she asked for help.",
    "gap_marker": "____",
    "options": ["manage to", "used to", "have to", "ought to"],
    "correct_index": 0,
    "target_explanation": "\\"Manage to\\" expresses success or failure in doing something, often with difficulty. In negative form, it shows failure to succeed.",
    "target_distractors_explanation": {
      "1": "\\"Used to\\" refers to past habits, not a specific failed attempt.",
      "2": "\\"Have to\\" expresses obligation.",
      "3": "\\"Ought to\\" expresses advice."
    },
    "target_hint": "Choose the semi-modal that expresses (lack of) success in doing something."
  },
  {
    "level": "C1",
    "order": 5,
    "target_language": "en",
    "target_sentence": "He ____ have informed us earlier; the delay caused serious problems.",
    "gap_marker": "____",
    "options": ["ought to", "used to", "is able to", "has to"],
    "correct_index": 0,
    "target_explanation": "\\"Ought to have + past participle\\" is used to express criticism or regret about a past action that did not happen.",
    "target_distractors_explanation": {
      "1": "\\"Used to\\" refers to past habits and cannot be followed by \\"have + past participle\\" in this structure.",
      "2": "\\"Is able to\\" expresses present ability and does not fit the past perfect structure.",
      "3": "\\"Has to\\" expresses present obligation, not past criticism."
    },
    "target_hint": "Use a semi-modal structure that expresses past criticism or regret."
  }
]

"""


class Generator:
    def __init__(self, app_state: AppState, client: ApiTestClient):
        self.app_state = app_state
        self.client = client

    def go(self, topic_create: TopicCreate) -> str:
        # Create topic
        topic = client.post_typed("/api/topics", 200, Topic_v1, json=topic_create)
        target_language = topic.target_language
        level = topic.level
        topic_url = f"/api/topics/{target_language}/{level}/{topic.id}"
        _log.warning("Created topic: %s", topic_url)
        # Create topic pages
        #     teacher_service = TeacherService(target_language_code)
        #     # Create a new letter shuffle set
        #     letter_shuffle_set_create = teacher_service.create_letter_shuffle_set(theme, number_of_words)
        rs = json.loads(response)
        for r in rs:
            c = GapFillChoiceExerciseCreate.model_validate(r)
            client.post_typed(f"{topic_url}/pages", 200, GapFillChoiceExercise, json=c)
        return topic_url

    def translate_topic(self, topic_url: str, native_languages: Optional[List[Language]] = None):
        topic = client.get_typed(topic_url, 200, Topic_v1)
        target_language = topic.target_language
        level = topic.level
        for native_language in native_languages or [Language.EN, Language.PL]:
            if native_language == topic.target_language:
                continue
            # Create native topic
            client.post(f"/api/native-topics/{target_language}/{level}/{native_language}/{topic.id}", 200)

    def translate_topic_pages(self, topic_url: str, native_languages: Optional[List[Language]] = None):
        topic = client.get_typed(topic_url, 200, Topic_v1)
        target_language = topic.target_language
        level = topic.level
        pages = client.get_typed_list(f"{topic_url}/pages", 200, PageHeader)
        for native_language in native_languages or [Language.EN, Language.PL]:
            if native_language == topic.target_language:
                continue
            # Create native topic pages
            for page in pages:
                client.post(f"/api/native-topics/{target_language}/{level}/{native_language}/{topic.id}/pages/{page.id}", 200)


if __name__ == "__main__":
    with ApiTestClient(app) as client:
        generator = Generator(client.app.state.app_state, client)  # type: ignore
        # topic_url = generator.go(
        #     TopicCreate(
        #         target_language=Language.EN,
        #         level=Level.A1,
        #         target_title="Semi-modals",
        #         target_description="Semi-modals vs. pure modal verbs",
        #         type=TopicType.GRAMMAR,
        #     )
        # )
        # generator.translate_topic(topic_url)
        topic_url = "/api/topics/en/A1/b02e279d-426d-475b-996c-fd376f9ad76e"
        generator.translate_topic_pages(topic_url)

# 1. Create a topic
# 2. Generate pages
# 3. Add pages to topic
# 4. Update images and voices
# 5. Add translations
