import asyncio

import _set_path as _set_path
from ampf.testing import ApiTestClient
from app_state import AppState
from dependencies import get_image_gen_service, get_image_service
from features.languages import Language
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet, LetterShuffleSetPatch
from features.letter_shuffles.letter_shuffle_translation_model import (
    LetterShuffleSetTranslation,
    LetterShuffleSetTranslationHeader,
)
from features.teacher.teacher_service import TeacherService
from main import app

theme = "Love and Valentine's Day"
number_of_words = 10
target_languages = [Language.EN, Language.ES, Language.DE, Language.FR]
native_languages = [Language.EN, Language.PL]
# number_of_words = 1
# target_languages = [Language.EN]
# native_languages = [Language.PL]


class Generator:
    def __init__(self, app_state: AppState, client: ApiTestClient):
        self.app_state = app_state
        self.client = client

    async def go(self):
        for target_language_code in target_languages:
            teacher_service = TeacherService(target_language_code)
            # Create a new letter shuffle set
            letter_shuffle_set_create = teacher_service.create_letter_shuffle_set(theme, number_of_words)
            client.post_typed(
                f"/api/target-languages/{target_language_code}/letter-shuffles",
                200,
                LetterShuffleSet,
                json=letter_shuffle_set_create,
            )

    async def generate_images(self, target_language_code: Language, letter_shuffle_set_id: str):
        # Generate images for the letter shuffle set
        image_gen_service = get_image_gen_service()
        image_service = get_image_service(self.app_state, image_gen_service)
        letter_shuffle_set = self.client.get_typed(
            f"/api/target-languages/{target_language_code.value}/letter-shuffles/{letter_shuffle_set_id}",
            200,
            LetterShuffleSet,
        )
        if not letter_shuffle_set.image_name:
            target_phrase = f"Create ilustration for theme: {theme}"
            image_name = await image_service.generate_and_upload(target_phrase, target_language_code)
            letter_shuffle_set = self.client.patch_typed(
                f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}",
                200,
                LetterShuffleSet,
                json=LetterShuffleSetPatch(image_name=image_name),
            )
        for i in letter_shuffle_set.items:
            if not i.phrase_image_name:
                image_name = await image_service.generate_and_upload(i.target_phrase, target_language_code)
                i.phrase_image_name = image_name
                client.put(
                    f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}",
                    200,
                    json=letter_shuffle_set,
                )

    def update_images(self, target_language_code: Language, letter_shuffle_set_id: str):
        # Update images for the letter shuffle set
        letter_shuffle_set = self.client.get_typed(
            f"/api/target-languages/{target_language_code.value}/letter-shuffles/{letter_shuffle_set_id}",
            200,
            LetterShuffleSet,
        )
        translations = self.client.get_typed_list(
            f"/api/target-languages/{target_language_code.value}/letter-shuffles/{letter_shuffle_set_id}/translations",
            200,
            LetterShuffleSetTranslationHeader,
        )
        for i in letter_shuffle_set.items:
            if i.phrase_image_name:
                for translation in translations:
                    client.patch(
                        f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}/translations/{translation.native_language_code}",
                        200,
                        json={"items": [{"target_phrase": i.target_phrase, "phrase_image_name": i.phrase_image_name}]},
                    )

    def translate_letter_shuffle_set(self, target_language_code: Language, letter_shuffle_set_id: str):
        letter_shuffle_set = self.client.get_typed(
            f"/api/target-languages/{target_language_code.value}/letter-shuffles/{letter_shuffle_set_id}",
            200,
            LetterShuffleSet,
        )
        teacher_service = TeacherService(target_language_code)
        for native_language_code in native_languages:
            if target_language_code != native_language_code:
                self.client.post_typed(
                    f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}/translations",
                    200,
                    LetterShuffleSetTranslation,
                    json=teacher_service.create_letter_shuffle_set_translation(
                        letter_shuffle_set, native_language_code
                    ),
                )


if __name__ == "__main__":
    # Reconfigure the lifespan to use the test server config
    with ApiTestClient(app) as client:
        generator = Generator(client.app.state.app_state, client)  # type: ignore
        # asyncio.run(generator.go())
        language = Language.FR
        set_id = "3b4f9a88-1ee4-4a3b-9e24-dd32aa1d473c"
        asyncio.run(generator.generate_images(language, set_id))
        generator.translate_letter_shuffle_set(language, set_id)
        # generator.update_images(Language.EN, "638fe8e7-7ea1-438f-82e8-aa78f6765c3e")
