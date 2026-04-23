
from ampf.base import BlobLocation
from ampf.local import LocalFactory
from haintech.testing import MockerAIModel
import pytest
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_base_model import PageType
from features.pages.page_service import PageServiceFactory
from features.topics.topic_model import TopicCreate, TopicType
from features.topics.topic_service import TopicService

from features.workflows.page_image_workflow import PageImageWorkflow
from shared.images.image_service import ImageService
from shared.prompts.prompt_executor_image import PromptExecutorImage


@pytest.fixture()
def page_image_workflow(
    topic_service: TopicService,
    page_service_factory: PageServiceFactory,
    native_page_service_factory: NativePageServiceFactory,
    image_service: ImageService,    
    prompt_executor_image: PromptExecutorImage):
    return PageImageWorkflow(
        topic_service=topic_service,
        page_service_factory=page_service_factory,
        native_page_service_factory=native_page_service_factory,
        image_service=image_service,
        prompt_executor_image=prompt_executor_image,
    )


@pytest.mark.asyncio
@pytest.mark.skip("Mock is required!")
async def test_generate_image(page_image_workflow: PageImageWorkflow, mocker_ai_model: MockerAIModel):
    mocker_ai_model.add_calls([
  {
    "system_prompt": "You are an expert Educational Illustrator and AI Image Prompt Engineer integrated into a modern language learning application. \nYour primary role is to design highly descriptive, vivid image generation prompts (e.g., for DALL-E 3 or Midjourney) that visually represent vocabulary words or phrases. These images serve as visual clues to help students guess and remember the target vocabulary.\n\n### BEHAVIORAL CONSTRAINTS & RULES:\n1. **NO TEXT IN IMAGES**: The generated image MUST NOT contain the target word, phrase, or any explicit text that gives away the answer. You must explicitly instruct the image generator to avoid writing text.\n2. **HANDLE ABSTRACT CONCEPTS**: If the target word or phrase is a highly abstract concept (e.g., \"existence\", \"although\", \"to assume\") that is extremely difficult or confusing to illustrate clearly, you must return an empty/null prompt.\n3. **EDUCATIONAL FOCUS**: The visual should be clear, engaging, and directly related to the provided definition and topic. It should match the cognitive level of the student.\n4. **LANGUAGE**: Always write the final image generation prompt in English, as image generation models perform best with English instructions, regardless of the language being learned.\n5. **OUTPUT FORMAT**: You must respond ONLY with a valid JSON object. Do not include conversational filler, explanations, or markdown formatting (like ```json).\n\n### JSON OUTPUT SCHEMA:\n{\n  \"image_prompt\": \"Detailed description of the scene, style, and elements. (Must include instruction: 'No text or words in the image.')\" // Use null or \"\" if the concept is too abstract.\n}",
    "message_str": "Please generate an image prompt for the following language learning exercise based on the provided context.\n\n### CONTEXT & TARGET AUDIENCE:\n- **Target Language**: Not specified\n- **Student Proficiency Level**: Not specified\n\n### EXERCISE CONTEXT:\n- **Topic**: (default)\n\n### TARGET VOCABULARY (DO NOT REVEAL IN IMAGE):\n- **Word/Phrase to Guess (Answer)**: keep you on your toes\n- **Definition/Clue**: To ensure someone stays alert, active, and ready for any surprises, preventing them from becoming too relaxed or overconfident. \n\n### INSTRUCTIONS:\n1. Analyze the target word/phrase (\"keep you on your toes\") and its definition.\n2. Determine if the concept is highly abstract. If it cannot be clearly and unambiguously illustrated, return `{\"image_prompt\": null}`.\n3. If it can be illustrated, create a detailed, vivid image generation prompt that captures the essence of the definition and fits the topic.\n4. Ensure the prompt explicitly forbids any text, letters, or words from appearing in the image.\n5. Return ONLY the JSON object.",
    "response": {
      "content": "{\"image_prompt\": \"A person, gender-neutral, is navigating a dynamic and slightly unpredictable environment, like an obstacle course or a path with unexpected, playful elements. They are in an active, alert stance, perhaps on the balls of their feet, with a focused and ready expression. The scene should convey a sense of constant vigilance and readiness for minor surprises or changes, preventing them from becoming too relaxed. The background could be a vibrant, engaging setting, like a game show stage or a fantastical training ground. No text or words in the image.\"}"
    }
  }
])
    # Given: A topic
    topic = await page_image_workflow.topic_service.create(
        TopicCreate(
            language=Language.EN,
            level=Level.B1,
            title="(default)",
            description="Various words and phrases",
            type=TopicType.VOCABULARY,
        )
    )
    # And: A definition guess page
    page_service = page_image_workflow.page_service_factory.create(
        language=Language.EN, level=Level.B1, topic_id=topic.id
    )
    page = await page_service.post(
        DefinitionGuessCreate(
            language=Language.EN,
            level=Level.B1,
            phrase="keep you on your toes",
            definition="To ensure someone stays alert, active, and ready for any surprises, preventing them from becoming too relaxed or overconfident. ",
            sentences=[],
            alternatives=[],
            distractors=[],
            hint="test_hint",
            explanation="test_explanation",
            image_names=[],
        )
    )
    # When: The generate_image method is called
    await page_image_workflow.execute(topic.language, topic.level, topic.id, page.id)
    # Then: Image is stored in page
    page = await page_service.get(page.id)
    assert page.type == PageType.DEFINITION_GUESS
    assert page.image_names
    assert len(page.image_names) == 1
    assert page.image_names[0]
    blob = await page_image_workflow.image_service.download(page.image_names[0])
    # factory = LocalFactory("./tests/data/")
    # factory.upload_blob(BlobLocation(name=__name__), blob)
    assert blob.name
    assert blob.content
    assert blob.metadata.language == topic.language.value
    assert blob.metadata.text == page.phrase
    assert blob.metadata.description == page.definition
    assert blob.metadata.prompt




