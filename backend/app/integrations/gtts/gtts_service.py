from io import BytesIO

from gtts import gTTS


class GttsService:
    def text_to_speech(self, text: str, lang: str) -> BytesIO:
        ret = BytesIO()
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(ret)
        ret.seek(0)
        return ret
