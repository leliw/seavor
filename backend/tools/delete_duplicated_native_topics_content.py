import asyncio
import logging
from uuid import UUID

import _set_path as _set_path
from core.app_config import AppConfig
from dotenv import load_dotenv
from features.languages import Language
from features.native_topics.native_topic_model import NativeTopic
from storage_def import STORAGE_DEF, set_storage_formats

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]

# Deletes duplicated native topics recognized by content_id
# (letter-shuffle)

async def main():
    config = AppConfig()  # pyright: ignore[reportCallIssue]
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

    # Native Topics
    for native_language in native_languages:
        contents: dict[UUID, set[UUID]] = {}
        nstorage = factory.get_collection("translations").get_collection(native_language, NativeTopic)
        async for topic_id in nstorage.keys():
            topic = await nstorage.get(topic_id)
            _log.debug("Topic: %s/%s/%s, type: %s level: %s, title: %s, content_id: %s", topic.id, topic.language, topic.native_language, topic.type, topic.level, topic.native_title, topic.content_id)
            if topic.content_id:
                if topic.content_id in contents:
                    contents[topic.content_id].add(topic.id)
                else:
                    contents[topic.content_id] = {topic.id}
        for content_id, topics in contents.items():
            _log.info("%s : %s", content_id, topics)
            for topic_id in list(topics)[1:]:
                _log.warning("Deleting %s", topic_id)
                await nstorage.delete(topic_id)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
