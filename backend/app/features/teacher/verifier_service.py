from features.pages.definition_guess_model import DefinitionGuess
from features.teacher.teacher_model import Evaluation
from features.topics.topic_model import Topic
from haintech.ai import BaseAIModel
from haintech.ai.google_genai import GoogleAIModel
from haintech.ai.prompts import PromptExecutor, PromptService


class VerifierService:
    def __init__(self, prompt_service: PromptService, ai_model: BaseAIModel | None = None):
        self.prompt_service = prompt_service
        self.ai_model = ai_model or GoogleAIModel(parameters={"temperature": 0.1})
        self.prompt_executor = PromptExecutor(self.ai_model, self.prompt_service)

    async def verify_definition_guess(self, topic: Topic, definition_guess: DefinitionGuess):
        definition_guess_dict = definition_guess.model_dump(
            include={
                "phrase",
                "definition",
                "hint",
                "explanation",
            },
        )
        definition_guess_dict["language"] = str(definition_guess.language)
        definition_guess_dict["level"] = str(definition_guess.level)
        definition_guess_dict["sentences"] = [a.model_dump(include={"text_with_gap", "gap_filler_form"}) for a in definition_guess.sentences ]
        definition_guess_dict["alternatives"] = [a.model_dump(include={"value", "explanation"}) for a in definition_guess.alternatives ]
        definition_guess_dict["distractors"] = [a.model_dump(include={"value", "explanation"}) for a in definition_guess.distractors ]

        return await self.prompt_executor.execute_typed_async(
            "verifier", Evaluation, topic=topic, definition_guess=definition_guess_dict
        )
