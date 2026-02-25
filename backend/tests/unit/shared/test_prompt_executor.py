from pathlib import Path

from haintech.ai import AIChatResponse
import pytest

from shared.prompts.prompt_executor import PromptExecutor
from shared.prompts.prompt_service import PromptService
from haintech.ai.google_generativeai import GoogleAIModel

from features.pages.page_model import InfoPageCreate


@pytest.fixture
def prompt_service() -> PromptService:
    root_path = Path("./tests/data/prompts")
    return PromptService(root_path)

@pytest.fixture
def prompt_executor(prompt_service: PromptService) -> PromptExecutor:
    ai_model = GoogleAIModel("gemini-2.5-flash-lite")
    return PromptExecutor(ai_model, prompt_service)


def test_prepare_response_typed_list(prompt_executor: PromptExecutor):
    m_resp = AIChatResponse(content="""
{
  "type": "array",
  "items": [
    {
      "type": "info",
      "title": "Verb to be - Introduction",
      "content": "The verb 'to be' is very important in English. It means 'am', 'is', or 'are'. We use it to talk about people, things, and places."
    },
    {
      "type": "info",
      "title": "Using 'am'",
      "content": "'Am' is used with 'I'. For example: I am happy. I am a student."
    }
  ]
}
""")   
    ret = prompt_executor._prepare_response_typed_list(InfoPageCreate, m_resp)
    # Then: A list of InfoPageCreate objects is returned
    assert len(ret) > 0
    assert isinstance(ret, list)
    assert all(isinstance(page, InfoPageCreate) for page in ret)
