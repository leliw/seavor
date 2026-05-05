import asyncio
import logging

import _set_path as _set_path
from app_config import AppConfig
from dotenv import load_dotenv
from features.languages import Language
from features.levels import Level
from features.native_pages.native_page_model import NativePage
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_model import Page
from features.repetitions.repetition_model import RepetitionCard
from features.topics.topic_model import Topic
from storage_def import STORAGE_DEF, set_storage_formats

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]


async def main():
    config = AppConfig()  # pyright: ignore[reportCallIssue]
    # Change the .env file !!!
    # config = AppConfig(gcp_bucket_name="test-seavor-9b08fd", gcp_root_storage="projects/test-seavor")  # pyright: ignore[reportCallIssue] # Test
    # config = AppConfig(gcp_bucket_name="prod-seavor-939101", gcp_root_storage="projects/prod-seavor")  # pyright: ignore[reportCallIssue] # Prod
    set_storage_formats(config.feature_flags)

    if config.gcp_root_storage:
        from ampf.gcp import GcpAsyncFactory

        factory = GcpAsyncFactory(root_storage=config.gcp_root_storage, bucket_name=config.gcp_bucket_name)
        _log.info(f"GCP storage root: {config.gcp_root_storage}")
        _log.info(f"GCP storage bucket: {config.gcp_bucket_name}")
    elif config.data_dir:
        from ampf.local import LocalAsyncFactory

        factory = LocalAsyncFactory(config.data_dir)
        _log.info(f"Local storage: {config.data_dir}")
    else:
        raise ValueError("No factory setup!")
    factory.register_collections(STORAGE_DEF)

    # Topics
    new_storage = factory.get_collection(Topic)
    for language in target_languages:
        for level in Level:
            old_storage = (
                factory.get_collection("target-languages")
                .get_collection(language, "levels")
                .get_collection(level, Topic)
            )
            async for topic_id in old_storage.keys():
                _log.debug("Topic: %s/%s/%s", language, level, topic_id)
                value = await old_storage.get(topic_id)
                await new_storage.save(value)
                # Pages
                old_pstorage = old_storage.get_collection(topic_id, Page)
                new_pstorage = new_storage.get_collection(topic_id, Page)
                async for page_id in old_pstorage.keys():
                    _log.debug(" Page: %s/%s/%s/%s", language, level, topic_id, page_id)
                    value = await old_pstorage.get(page_id)
                    await new_pstorage.save(value)
    # Native Topics
    for native_language in native_languages:
        new_storage = factory.get_collection("translations").get_collection(native_language, NativeTopic)
        for language in target_languages:
            for level in Level:
                old_storage = (
                    factory.get_collection("target-languages")
                    .get_collection(language, "levels")
                    .get_collection(level, "native-languages")
                    .get_collection(native_language, NativeTopic)
                )
                async for topic_id in old_storage.keys():
                    _log.debug("Native Topic: %s/%s/%s/%s", language, level, topic_id, native_language)
                    value = await old_storage.get(topic_id)
                    await new_storage.save(value)
                    # Native Pages
                    old_pstorage = old_storage.get_collection(topic_id, NativePage)
                    new_pstorage = new_storage.get_collection(topic_id, NativePage)
                    async for page_id in old_pstorage.keys():
                        _log.debug(" Native Page: %s/%s/%s/%s", language, level, topic_id, page_id)
                        value = await old_pstorage.get(page_id)
                        await new_pstorage.save(value)

    # Repetitions
    user_storage = factory.get_collection("users")
    async for username in user_storage.keys():
        _log.debug("User: %s", username)
        new_storage = user_storage.get_collection(username, RepetitionCard)
        for language in target_languages:
            for level in Level:
                old_storage = (
                    user_storage.get_collection(username, "languages")
                    .get_collection(language, "levels")
                    .get_collection(level, RepetitionCard)
                )
                async for card_id in old_storage.keys():
                    _log.debug("Repetition: %s/%s/%s", language, level, card_id)
                    value = await old_storage.get(card_id)
                    await new_storage.save(value)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
