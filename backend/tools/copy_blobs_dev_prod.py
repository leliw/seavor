import asyncio
import logging

import _set_path as _set_path
from ampf.base import BaseAsyncFactory, BaseBlobMetadata
from app_state import AppState
from core.app_config import AppConfig
from dotenv import load_dotenv
from pydantic import ValidationError
from shared.audio_files.audio_file_model import AudioFileMetadata
from shared.images.image_model import ImageMetadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
logging.getLogger("httpx2").setLevel(logging.WARNING)
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


async def copy_blob_storage[T: BaseBlobMetadata](
    src_factory: BaseAsyncFactory,
    dest_factory: BaseAsyncFactory,
    collection_name: str,
    clazz: type[T],
    content_type: str,
) -> None:
    _log.info("Copying %s", collection_name)

    src_storage = src_factory.create_blob_storage(collection_name, clazz, content_type)
    dest_storage = dest_factory.create_blob_storage(collection_name, clazz, content_type)

    src_keys = {b.name async for b in src_storage.list_blobs()}
    dest_keys = {b.name async for b in dest_storage.list_blobs()}

    for key in src_keys:
        if key not in dest_keys:
            _log.info("Copying %s", key)
            try:
                blob = await src_storage.download_async(key)
            except ValidationError as e:
                _log.error("Error downloading %s: %s", key, e)
                continue
            except Exception as e:
                _log.error("Error downloading %s: %s", key, e)
                continue
            await dest_storage.upload_async(blob)


async def main():
    load_dotenv(".env", override=True)
    src_config = AppConfig()  # pyright: ignore[reportCallIssue]
    load_dotenv("../infra/env/prod/.env.app", override=True)
    load_dotenv(".env.prod")
    dest_config = AppConfig()  # pyright: ignore[reportCallIssue]

    src_factory = AppState.create_factory(src_config)
    dest_factory = AppState.create_factory(dest_config)

    _log.info("GCP storage bucket %s -> %s", src_config.gcp_bucket_name, dest_config.gcp_bucket_name)

    await asyncio.gather(
        copy_blob_storage(src_factory, dest_factory, "audio-files", AudioFileMetadata, content_type="audio/mpeg"),
        copy_blob_storage(src_factory, dest_factory, "images", ImageMetadata, content_type="image/png"),
    )


if __name__ == "__main__":
    asyncio.run(main())
