import asyncio
import logging

import _set_path as _set_path
from ampf.base import BaseAsyncCollectionStorage, BaseBlobMetadata, KeyNotExistsException
from ampf.gcp import GcpAsyncFactory
from ampf.local import LocalAsyncFactory
from app_config import AppConfig
from dotenv import load_dotenv
from features.languages import Language
from pydantic import BaseModel, ValidationError
from storage_def import STORAGE_DEF, set_storage_formats

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


data_dir = "./data"


async def copy_value(src: BaseAsyncCollectionStorage, dest: BaseAsyncCollectionStorage, key) -> None:
    _log.info("%s->%s", src.collection_name, key)
    try:
        value = await src.get(key)
        await dest.save(value)
    except KeyNotExistsException as e:
        _log.warning(e)


async def copy_collection[T: BaseModel](
    src: BaseAsyncCollectionStorage[T], dest: BaseAsyncCollectionStorage[T]
) -> None:
    _log.info("Copying %s", src.collection_name)

    src_keys = {k.split("/")[0] async for k in src.keys()}
    dest_keys = {k.split("/")[0] async for k in dest.keys()}
    keys_to_copy = src_keys - dest_keys
    await asyncio.gather(
        *[copy_value(src, dest, key) for key in keys_to_copy],
        *[
            copy_collection(src.get_collection(key, coll), dest.get_collection(key, coll))
            for key in src_keys
            for coll in src.subcollections
        ],
    )


async def copy_storage[T: BaseModel](
    src_factory: LocalAsyncFactory, dest_factory: GcpAsyncFactory, collection_name: str, clazz: type[T]
) -> None:
    _log.info("Copying %s", collection_name)

    src_storage = src_factory.create_storage(collection_name, clazz)
    dest_storage = dest_factory.create_storage(collection_name, clazz)

    src_keys = {k async for k in src_storage.keys()}
    dest_keys = {k async for k in dest_storage.keys()}

    for key in src_keys:
        if key not in dest_keys:
            _log.info("Copying %s/%s", collection_name, key)
            value = await src_storage.get(key)
            await dest_storage.save(value)


async def copy_blob_storage[T: BaseBlobMetadata](
    src_factory: LocalAsyncFactory,
    dest_factory: GcpAsyncFactory,
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


target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]


async def main():
    config = AppConfig(gcp_bucket_name="test-seavor-9b08fd", gcp_root_storage="projects/test-seavor")
    set_storage_formats(config.feature_flags)
    src_factory = LocalAsyncFactory(data_dir)
    src_factory.register_collections(STORAGE_DEF)
    dest_factory = GcpAsyncFactory(root_storage=config.gcp_root_storage, bucket_name=config.gcp_bucket_name)
    dest_factory.register_collections(STORAGE_DEF)

    _log.info(f"GCP storage root: {config.gcp_root_storage}")
    _log.info(f"GCP storage bucket: {config.gcp_bucket_name}")

    # src_collection = src_factory.get_collection(UserInDB)
    # dest_collection = dest_factory.get_collection(UserInDB)
    # await copy_collection(src_collection, dest_collection)

    src_collection = src_factory.get_collection("target-languages")
    dest_collection = dest_factory.get_collection("target-languages")
    await copy_collection(src_collection, dest_collection)

    # await asyncio.gather(
    #     copy_blob_storage(src_factory, dest_factory, "audio-files", AudioFileMetadata, content_type="audio/mpeg"),
    #     copy_blob_storage(src_factory, dest_factory, "images", ImageMetadata, content_type="image/png"),
    # )


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
