import logging

from dotenv import load_dotenv

import _set_path as _set_path
from ampf.base import BaseBlobMetadata
from ampf.gcp import GcpFactory
from ampf.local import LocalFactory
from app_config import AppConfig
from features.languages import Language
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.topics.topic_model import Topic
from pydantic import BaseModel, ValidationError
from shared.audio_files.audio_file_model import AudioFileMetadata
from shared.images.image_model import ImageMetadata


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


data_dir = "./data"


def copy_storage[T: BaseModel](
    src_factory: LocalFactory, dest_factory: GcpFactory, collection_name: str, clazz: type[T]
) -> None:
    _log.info("Copying %s", collection_name)

    src_storage = src_factory.create_storage(collection_name, clazz)
    dest_storage = dest_factory.create_storage(collection_name, clazz)

    src_keys = set(src_storage.keys())
    dest_keys = set(dest_storage.keys())

    for key in src_keys:
        if key not in dest_keys:
            _log.info("Copying %s", key)
            value = src_storage.get(key)
            dest_storage.save(value)


def copy_blob_storage[T: BaseBlobMetadata](
    src_factory: LocalFactory, dest_factory: GcpFactory, collection_name: str, clazz: type[T], content_type: str
) -> None:
    _log.info("Copying %s", collection_name)

    src_storage = src_factory.create_blob_storage(collection_name, clazz, content_type)
    dest_storage = dest_factory.create_blob_storage(collection_name, clazz, content_type)

    src_keys = set(src_storage.keys())
    dest_keys = set(dest_storage.keys())

    for key in src_keys:
        if key not in dest_keys:
            _log.info("Copying %s", key)
            try:
                blob = src_storage.download(key)
            except ValidationError as e:
                _log.error("Error downloading %s: %s", key, e)
                continue
            except Exception as e:
                _log.error("Error downloading %s: %s", key, e)
                continue
            dest_storage.upload(blob)


target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]


if __name__ == "__main__":
    load_dotenv()
    config = AppConfig()
    src_factory = LocalFactory(data_dir)
    dest_factory = GcpFactory(root_storage=config.gcp_root_storage, bucket_name=config.gcp_bucket_name)
    _log.info(f"GCP storage root: {config.gcp_root_storage}")
    _log.info(f"GCP storage bucket: {config.gcp_bucket_name}")
    # for target_language_code in target_languages:
    #     lss_storage = src_factory.create_storage(
    #         f"target-languages/{target_language_code}/letter-shuffles", LetterShuffleSet
    #     )
    #     for id in lss_storage.keys():
    #         ls = lss_storage.get(id)
    #         src_storage = src_factory.create_storage(
    #             f"target-languages/{target_language_code}/letter-shuffles/{id}",
    #             LetterShuffleSetTranslation,
    #         )
    #         dest_storage = dest_factory.create_storage(
    #             f"target-languages/{target_language_code}/letter-shuffles/{id}/native-languages",
    #             LetterShuffleSetTranslation,
    #             "native_language_code"
    #         )
    #         src_keys = set(src_storage.keys())
    #         dest_keys = set(dest_storage.keys())

    #         for key in src_keys:
    #             if key not in dest_keys:
    #                 _log.info("Copying %s", key)
    #                 value = src_storage.get(key)
    #                 dest_storage.save(value)

    # for target_language_code in target_languages:
    #     copy_storage(
    #         src_factory, dest_factory, f"target-languages/{target_language_code}/letter-shuffles", LetterShuffleSet
    #     )
    #     for native_language_code in native_languages:
    #         copy_storage(
    #             src_factory,
    #             dest_factory,
    #             f"target-languages/{target_language_code}/letter-shuffles/{native_language_code}/translations",
    #             LetterShuffleSetTranslation,
    #         )
    #         for level in list(Level):
    #             copy_storage(
    #                 src_factory,
    #                 dest_factory,
    #                 f"target-languages/{target_language_code}/levels/{level}/native-languages/{native_language_code}/topics",
    #                 Topic,
    #             )
    copy_blob_storage(src_factory, dest_factory, "audio-files", AudioFileMetadata, content_type="audio/mpeg")
    copy_blob_storage(src_factory, dest_factory, "images", ImageMetadata, content_type="image/png")
