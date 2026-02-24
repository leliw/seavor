from typing import Dict
from uuid import UUID

from features.languages import LANGUAGE_NAMES, Language
from features.levels import Level
from features.native_topics.native_topic_model import NativeTopic
from features.topics.topic_service import TopicService
from haintech.ai import AITaskExecutor, BaseAIModel


class NativeTopicTranslator:
    def __init__(self, ai_model: BaseAIModel, service: TopicService):
        self.service = service
        self.ai_model = ai_model

    async def translate_topic_to_native(
        self, target_language: Language, level: Level, native_language: Language, topic_id: UUID
    ) -> NativeTopic:
        topic = await self.service.get(target_language, level, topic_id)
        native = await self._translate(target_language, native_language, topic.target_title, topic.target_description)
        return NativeTopic.from_topic(topic, native_language, native.get("title", ""), native.get("description", ""))

    async def _translate(
        self, src_language: Language, dest_language: Language, title: str, description: str
    ) -> Dict[str, str]:
        system_instructions = "You are translating topics of a language course. Translate only if it is necessary."

        message = "Translate the topic title and its description from {src_language} to {dest_language}. "
        message += "Return the response as a single JSON dictionary."
        message += "\nTitle: **{title}**"
        message += "\nDescription: **{description}**"
        message += "\n\n"
        message += "Example response:"
        message += "\n{{'title': 'translated title', 'description': 'translated description'}}"
        message += "\n"

        task = AITaskExecutor(self.ai_model, system_instructions, message, "json")
        ret = await task.execute_async(
            src_language=LANGUAGE_NAMES[src_language],
            dest_language=LANGUAGE_NAMES[dest_language],
            title=title,
            description=description,
        )
        if isinstance(ret, dict) and len(ret) == 1:
            ret = list(ret.values())[0]
        return ret  # type: ignore
