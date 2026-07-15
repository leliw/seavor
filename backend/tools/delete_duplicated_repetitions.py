import asyncio
import logging

from ampf.base import BaseAsyncCollectionStorage

import _set_path as _set_path
from core.app_config import AppConfig
from dotenv import load_dotenv
from core.users.user_model import UserInDB
from features.languages import Language
from features.repetitions.repetition_model import LanguageStatus, RepetitionCard, RepetitionCardHeader
from features.repetitions.repetition_service import RepetitionService
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
    user_storage = factory.get_collection(UserInDB)
    async for username in user_storage.keys():
        await process_user(
            username,
            user_storage.get_collection(username, "languages"),
            user_storage.get_collection(username, RepetitionCard),
        )


async def process_user(
    username: str,
    language_storage: BaseAsyncCollectionStorage[LanguageStatus],
    new_storage: BaseAsyncCollectionStorage[RepetitionCard],
) -> None:
    _log.info("Processing user: %s", username)
    service = RepetitionService(language_storage, new_storage)
    reps: dict[str, list[RepetitionCardHeader]] = {}
    async for rep in service.get_all():
        tp_id = f"{rep.topic_id}_{rep.page_id}"
        if tp_id in reps:
            reps[tp_id].append(rep)
        else:
            reps[tp_id] = [rep]
    for k, v in reps.items():
        if len(v) > 1:
            vs = sorted(v, key=lambda r: r.due)
            dues = [r.due for r in vs]
            levels = [r.level for r in vs]
            _log.info("%s: %d - %s %s", k, len(v), dues, levels, )


if __name__ == "__main__":
    # load_dotenv("../infra/env/prod/.env.app", override=True)
    # load_dotenv(".env.prod")
    load_dotenv(".env")
    asyncio.run(main())
