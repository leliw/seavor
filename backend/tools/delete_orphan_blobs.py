import asyncio
import logging
from pathlib import Path

import _set_path as _set_path
from ampf.base import BaseAsyncCollectionStorage
from ampf.local import LocalAsyncBlobStorage, LocalAsyncFactory
from dotenv import load_dotenv
from features.languages import Language
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.levels import Level
from features.native_pages.native_page_model import NativePage
from features.native_topics.native_topic_model import NativeTopic
from features.pages.page_base_model import PageType
from features.pages.page_model import Page
from features.topics.topic_model import Topic
from shared.audio_files.audio_file_model import AudioFileMetadata
from shared.images.image_model import ImageMetadata
from storage_def import STORAGE_DEF

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


data_dir = "./data"

target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]


async def get_letter_shuffle_set_blobs(storage: BaseAsyncCollectionStorage[LetterShuffleSet]):
    images = set()
    audios = set()
    async for letter_shuffle_set in storage.get_all():
        if letter_shuffle_set.image_name:
            images.add(letter_shuffle_set.image_name)
            for item in letter_shuffle_set.items:
                if item.phrase_image_name:
                    images.add(item.phrase_image_name)
                if item.target_phrase_audio_file_name:
                    audios.add(item.target_phrase_audio_file_name)
                if item.target_description_audio_file_name:
                    audios.add(item.target_description_audio_file_name)

    return (images, audios)


async def get_letter_shuffle_translation_set_blobs(
    storage: BaseAsyncCollectionStorage[LetterShuffleSetTranslation],
):
    images = set()
    audios = set()
    async for letter_shuffle_set in storage.get_all():
        if letter_shuffle_set.image_name:
            images.add(letter_shuffle_set.image_name)
            for item in letter_shuffle_set.items:
                if item.phrase_image_name:
                    images.add(item.phrase_image_name)
                if item.target_phrase_audio_file_name:
                    audios.add(item.target_phrase_audio_file_name)
                if item.target_description_audio_file_name:
                    audios.add(item.target_description_audio_file_name)
                if item.native_phrase_audio_file_name:
                    audios.add(item.native_phrase_audio_file_name)
                if item.native_description_audio_file_name:
                    audios.add(item.native_description_audio_file_name)

    return (images, audios)


async def get_topic_blobs(storage: BaseAsyncCollectionStorage[Topic]):
    images = set()
    audios = set()
    async for i in storage.get_all():
        if i.image_name:
            images.add(i.image_name)
    return (images, audios)

async def get_page_blobs(storage: BaseAsyncCollectionStorage[Page]):
    images = set()
    audios = set()
    async for i in storage.get_all():
        if i.type == PageType.DEFINITION_GUESS:
            if i.image_names:
                images.update(i.image_names)
            if i.definition_audio_file_name:
                audios.add(i.definition_audio_file_name)
            if i.phrase_audio_file_name:
                audios.add(i.phrase_audio_file_name)
            if i.hint_audio_file_name:
                audios.add(i.hint_audio_file_name)
            if i.explanation_audio_file_name:
                audios.add(i.explanation_audio_file_name)
        elif i.type == PageType.INFO:
            if i.image_url:
                images.add(i.image_url)
        elif i.type == PageType.GAP_FILL_CHOICE:
            if i.sentence_audio_file_name:
                audios.add(i.sentence_audio_file_name)
            if i.explanation_audio_file_name:
                audios.add(i.explanation_audio_file_name)
            if i.hint_audio_file_name:
                audios.add(i.hint_audio_file_name)
            if i.distractors_explanation_audio_file_name:
                for v in i.distractors_explanation_audio_file_name.values():
                    audios.add(v)
    return (images, audios)


async def get_native_page_blobs(storage: BaseAsyncCollectionStorage[NativePage]):
    images = set()
    audios = set()
    async for i in storage.get_all():
        if i.type == PageType.DEFINITION_GUESS:
            continue
        elif i.type == PageType.INFO:
            continue
        elif i.type == PageType.GAP_FILL_CHOICE:
            if i.native_sentence_audio_file_name:
                audios.add(i.native_sentence_audio_file_name)
            if i.native_explanation_audio_file_name:
                audios.add(i.native_explanation_audio_file_name)
            if i.native_hint_audio_file_name:
                audios.add(i.native_hint_audio_file_name)
            if i.native_distractors_explanation_audio_file_name:
                for v in i.native_distractors_explanation_audio_file_name.values():
                    audios.add(v)
    return (images, audios)

async def main():
    factory = LocalAsyncFactory(data_dir)
    factory.register_collections(STORAGE_DEF)
    letter_shuffle_set_storages = [
        factory.get_collection("target-languages").get_collection(tl, LetterShuffleSet) for tl in target_languages
    ]

    letter_shuffle_set_translation_storages = [
        factory.get_collection("target-languages")
        .get_collection(tl, LetterShuffleSet)
        .get_collection(nl, LetterShuffleSetTranslation)
        for tl in target_languages
        for nl in native_languages
    ]

    topic_storages = [
        factory.get_collection("target-languages").get_collection(tl, "levels").get_collection(level, Topic)
        for tl in target_languages
        for level in Level
    ]

    page_storages = [
        topic_storage.get_collection(topic_id, Page)
        for topic_storage in topic_storages
        async for topic_id in topic_storage.keys()
    ]

    native_topic_storages = [
        factory.get_collection("target-languages").get_collection(tl, "levels").get_collection(level, "native-languages").get_collection(nl, NativeTopic)        
        for tl in target_languages
        for level in Level
        for nl in native_languages
    ]

    native_page_storages = [
        native_topic_storage.get_collection(topic_id, NativePage)
        for native_topic_storage in native_topic_storages
        async for topic_id in native_topic_storage.keys()
    ]

    ret = await asyncio.gather(
        *[get_letter_shuffle_set_blobs(s) for s in letter_shuffle_set_storages],
        *[get_letter_shuffle_translation_set_blobs(s) for s in letter_shuffle_set_translation_storages],
        *[get_topic_blobs(s) for s in topic_storages],
        *[get_page_blobs(s) for s in page_storages],
        *[get_native_page_blobs(s) for s in native_page_storages],
    )
    images = {img for sublist in ret for img in sublist[0]}
    print("Images:", len(images))
    audios = {audio for sublist in ret for audio in sublist[1]}
    print("Audios:", len(audios))

    image_storage: LocalAsyncBlobStorage[ImageMetadata] = factory.create_blob_storage("images", ImageMetadata, content_type="image/png") # type: ignore
    base_path = image_storage.base_path
    old_path = Path(str(image_storage.base_path).replace("data", "data-old"))
    old_path.mkdir(parents=True, exist_ok=True)
    async for image in image_storage.list_blobs():
        if image.name not in images:
            for ext in [".jpg", ".png", ".json"]:
                full_path = base_path.joinpath(f"{image.name}{ext}")
                if full_path.exists():
                    print("Moving image:", full_path)
                    full_path.rename(old_path.joinpath(f"{image.name}{ext}"))

    audio_storage: LocalAsyncBlobStorage[AudioFileMetadata] = factory.create_blob_storage("audio-files", AudioFileMetadata, content_type="audio/mpeg") # type: ignore
    base_path = audio_storage.base_path
    old_path = Path(str(audio_storage.base_path).replace("data", "data-old"))
    old_path.mkdir(parents=True, exist_ok=True)
    async for audio in audio_storage.list_blobs():
        if audio.name not in audios:
            for ext in [".mp3", ".json"]:
                full_path = base_path.joinpath(f"{audio.name}{ext}")
                if full_path.exists():
                    print("Moving audio:", full_path)
                    full_path.rename(old_path.joinpath(f"{audio.name}{ext}"))

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
