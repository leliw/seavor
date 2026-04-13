from dataclasses import dataclass
from uuid import NAMESPACE_DNS, UUID, uuid5

from ampf.base import KeyNotExistsException

from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_service import NativePageServiceFactory
from features.pages.page_base_model import PageType
from features.pages.page_service import PageServiceFactory
from features.topics.topic_service import TopicService
from shared.images.image_model import ImageBlob, ImageMetadata
from shared.images.image_service import ImageService
from shared.prompts.prompt_executor_image import PromptExecutorImage


@dataclass
class PageImageWorkflow:
    topic_service: TopicService
    page_service_factory: PageServiceFactory
    native_page_service_factory: NativePageServiceFactory
    image_service: ImageService
    prompt_executor_image: PromptExecutorImage

    async def execute(self, language: Language, level: Level, topic_id: UUID, page_id: UUID) -> None:
        page_service = self.page_service_factory.create(language=language, level=level, topic_id=topic_id)
        topic = await self.topic_service.get(language=language, level=level, id=topic_id)
        page = await page_service.get(page_id)
        if page.type == PageType.DEFINITION_GUESS:
            text = page.phrase
            description = page.definition
        else:
            raise ValueError(f"Unsupported page type: {page.type}")

        blob_create = await self.prompt_executor_image.execute_image_prompt_async(
            "picture_generator", topic=topic, content=page
        )
        if not blob_create:
            return
        name = uuid5(NAMESPACE_DNS, f"{language.value}-{text}").hex
        blob = ImageBlob(
            name=name,
            content=blob_create.content,
            metadata=ImageMetadata(
                **blob_create.metadata.model_dump(),
                language=language.value,
                text=text,
                description=description,
            ),
        )
        await self.image_service.upload(blob)
        page = await page_service.add_image_name(page_id, blob.name)
        if page:
            for native_language in Language:
                native_page_service = self.native_page_service_factory.create(target_language=language, level=level, native_language=native_language, topic_id=topic_id)
                try:
                    await native_page_service.patch(page_id, page.model_dump(include={"image_names"}))
                except KeyNotExistsException:
                    pass


        
