from typing import List
from uuid import UUID

from ampf.fastapi import JsonStreamingResponse
from dependencies import (
    ImageServiceDep,
    NativePageServiceFactoryDep,
    PageServiceDep,
    PageServiceFactoryDep,
    PromptExecutorImageDep,
    RepetitionServiceDep,
    TopicServiceDep,
    get_topic_for_user,
)
from fastapi import APIRouter, Depends
from features.languages import Language
from features.levels import Level
from features.pages.page_base_model import BasePage
from features.pages.page_model import (
    Page,
    PageCreate,
    PagePatch,
)
from features.repetitions.repetition_model import PageEvaluation, RepetitionCard
from features.workflows.page_image_workflow import PageImageWorkflow

router = APIRouter(tags=["Topic pages"], dependencies=[Depends(get_topic_for_user)])
ITEM_PATH = "/{page_id}"


@router.post("")
async def post(service: PageServiceDep, value_create: PageCreate) -> Page:
    return await service.post(value_create)


@router.get("")
async def get_all(
    service: PageServiceDep,
) -> List[BasePage]:
    return JsonStreamingResponse(service.get_all())  # type: ignore


@router.get(ITEM_PATH)
async def get(service: PageServiceDep, page_id: UUID) -> Page:
    return await service.get(page_id)


@router.patch(ITEM_PATH)
async def patch(service: PageServiceDep, page_id: UUID, value_patch: PagePatch) -> Page:
    return await service.patch(page_id, value_patch)


@router.delete(ITEM_PATH)
async def delete(service: PageServiceDep, page_id: UUID) -> None:
    await service.delete(page_id)


@router.post(f"{ITEM_PATH}/evaluate")
async def evaluate(
    service: RepetitionServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
    page_id: UUID,
    page_evaluation: PageEvaluation,
) -> RepetitionCard:
    return await service.evaluate(target_language, level, topic_id, page_id, page_evaluation)


@router.post(f"{ITEM_PATH}/generate-image")
async def generate_image(
    topic_service: TopicServiceDep,
    page_service_factory: PageServiceFactoryDep,
    native_page_service_factory: NativePageServiceFactoryDep,
    image_service: ImageServiceDep,
    prompt_executor_image: PromptExecutorImageDep,
    service: PageServiceDep,
    target_language: Language,
    level: Level,
    topic_id: UUID,
    page_id: UUID,
) -> Page:
    workflow = PageImageWorkflow(
        topic_service=topic_service,
        page_service_factory=page_service_factory,
        native_page_service_factory=native_page_service_factory,
        image_service=image_service,
        prompt_executor_image=prompt_executor_image,
    )
    await workflow.execute(target_language, level, topic_id, page_id)
    return await service.get(page_id)
