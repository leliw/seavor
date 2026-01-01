from io import BytesIO


class GttsService:
    def text_to_speech(self, text: str, lang: str) -> BytesIO:
        from gtts import gTTS

        ret = BytesIO()
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(ret)
        ret.seek(0)
        return ret

    async def text_to_speech_async(self, text: str, lang: str) -> BytesIO:
        from aiogtts import aiogTTS

        aiogtts = aiogTTS()
        io = BytesIO()
        await aiogtts.write_to_fp(text, io, lang=lang)
        io.seek(0)
        return io
