import pytest
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativeInfoPageBase
from features.native_pages.native_page_translator import NativePageTranslator
from features.pages.page_model import InfoPage, InfoPageCreate, PageType
from haintech.ai.google_generativeai import GoogleAIModel
from haintech.testing import MockerAIModel
from shared.prompts.prompt_service import PromptService


@pytest.fixture
def native_page_translator() -> NativePageTranslator:
    ai_model = GoogleAIModel("gemini-2.5-flash-lite")
    return NativePageTranslator(ai_model, PromptService("./app/prompts"), None)  # type: ignore


@pytest.mark.asyncio
async def test_translate_info_page(native_page_translator: NativePageTranslator, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add(
        system_prompt="You are translating info pages of a language course from English to sudent native language: Polish.\nTranslate only if it is necessary.",
        message_containing='**\nVerb to be: Using "are"\n',
        response="[{\"native_title\": \"Czasownik 'by\u0107': U\u017cycie 'are'\", \"native_content\": \"U\u017cywaj 'are' z 'you', 'we', 'they' lub rzeczownikami w liczbie mnogiej. Na przyk\u0142ad: 'You are kind.' 'They are friends.'\"}]",
    )
    # Given: an info page
    page = InfoPage.create(
        InfoPageCreate(
            target_language=Language.EN,
            level=Level.A1,
            order=1,
            type=PageType.INFO,
            title='Verb to be: Using "are"',
            content='Use "are" with you, we, they, or plural nouns. For example: "You are kind." "They are friends."',
        )
    )
    # When: Translate page
    ret = await native_page_translator._translate_info_page(page.target_language, Language.PL, page)
    # Then: A translated page is returned
    assert isinstance(ret, NativeInfoPageBase)
    assert ret.native_title
    assert ret.native_content
