
from features.native_pages.native_page_model import NativeAnswerOption, NativeDefinitionGuessBase as NativeDefinitionGuessBaseOrg, NativeSentence
from haintech.ai.prompts.prompt_model import BaseOutput


class NativeDefinitionGuessBase(BaseOutput[NativeDefinitionGuessBaseOrg]):
    native_phrase: str
    native_definition: str  # markdown / HTML / JSON

    native_sentences: list[NativeSentence]
    native_alternatives: list[NativeAnswerOption]
    native_distractors: list[NativeAnswerOption]

    native_hint: str | None = None
    native_explanation: str | None = None

    def convert(self, **kwargs) -> NativeDefinitionGuessBaseOrg:
        clean_kwargs = {k: v for k, v in kwargs.items() if k in NativeDefinitionGuessBaseOrg.model_fields}
        return NativeDefinitionGuessBaseOrg(
            **clean_kwargs,
            **self.model_dump(),
        )
