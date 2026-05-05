from haintech.ai.google_genai import GoogleAIModel

from .app_config import AppConfig


class TranslatorAIModel(GoogleAIModel):
    def __init__(self, app_config: AppConfig):
        super().__init__(
            model_name=app_config.translator_ai_model_name,
            parameters={"temperature": 0.1},
            api_key=app_config.google_api_key,
        )
