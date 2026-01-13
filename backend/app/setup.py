import asyncio

from ampf.testing import ApiTestClient
from app_state import AppState
from dependencies import get_image_gen_service, get_image_service
from features.letter_shuffles.letter_shuffle_model import LetterShuffleSet
from features.letter_shuffles.letter_shuffle_translation_model import LetterShuffleSetTranslation
from features.teacher.teacher_service import TeacherService
from main import app as main_app

target_languages=["en", "es", "de", "fr"]
native_languages=["en", "pl"]

if __name__ == "__main__":
    app = main_app
    with ApiTestClient(app) as client:
        for target_language_code in target_languages:
            teacher_service = TeacherService(target_language_code)

            # Create a new letter shuffle set
            theme = "Winter Holidays"
            number_of_words = 10
            letter_shuffle_set_create = teacher_service.create_letter_shuffle_set(theme, number_of_words)
            letter_shuffle_set = client.post_typed(
                f"/api/target-languages/{target_language_code}/letter-shuffles",
                200,
                LetterShuffleSet,
                json=letter_shuffle_set_create,
            )
            # Generate images for the letter shuffle set
            app_state: AppState = app.state.app_state
            image_gen_service = get_image_gen_service()
            image_service = get_image_service(app_state, image_gen_service)
            for i in letter_shuffle_set.items:
                if not i.phrase_image_name:
                    image_name = asyncio.run(image_service.generate_and_upload(i.target_phrase, target_language_code))
                    print(i.target_phrase, image_name)
                    i.phrase_image_name = image_name
                    client.put(
                        f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}",
                        200,
                        json=letter_shuffle_set,
                    )
            for native_language_code in native_languages:
                if target_language_code != native_language_code:
                    # Create a translation for the letter shuffle set
                    letter_shuffle_set_translation_create = teacher_service.create_letter_shuffle_set_translation(
                        letter_shuffle_set, native_language_code
                    )
                    letter_shuffle_set_translation = client.post_typed(
                        f"/api/target-languages/{target_language_code}/letter-shuffles/{letter_shuffle_set.id}/translations",
                        200,
                        LetterShuffleSetTranslation,
                        json=letter_shuffle_set_translation_create,
                    )
