import asyncio
import logging

import _set_path as _set_path
from ampf.testing import ApiTestClient
from app_state import AppState
from dependencies import (
    get_audio_file_service,
    get_topic_service,
    get_tts_service,
)
from features.languages import Language
from features.levels import Level
from features.topics.topic_model import Topic
from main import app
from routers.letter_shuffles import get_letter_shuffle_service
from routers.letter_shuffles_translations import get_letter_shuffle_translation_service

__all__ = ["_set_path"]
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


async def go(app_state: AppState, client: ApiTestClient):
    tts_service = get_tts_service()
    audio_service = get_audio_file_service(app_state, tts_service)
    for lang in list(Language):
        ls_service = get_letter_shuffle_service(app_state, audio_service, lang)
        topic_service = get_topic_service(app_state)
        async for ls in ls_service.get_all():
            lst_service = get_letter_shuffle_translation_service(app_state, audio_service, lang, ls.id)
            async for lsth in lst_service.get_all():
                print(lsth)
                lst = await lst_service.get(lsth.native_language_code)
                calls = [
                    topic_service.save(Topic.from_letter_shuffle_translation(level, lst))
                    for level in lst.levels or list(Level)
                ]
                await asyncio.gather(*calls)


if __name__ == "__main__":
    # Reconfigure the lifespan to use the test server config
    with ApiTestClient(app) as client:
        app_state = client.app.state.app_state  # type: ignore
        asyncio.run(go(app_state, client))
