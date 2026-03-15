from features.levels import Level
from features.pages.definition_guess_model import DefinitionGuessCreate
from features.pages.page_base_model import PageType
from pydantic import BaseModel
from shared.prompts.prompt_model import BaseOutput


class Sentence(BaseModel):
    text_with_gap: str
    gap_filler_form: str


class AnswerOption(BaseModel):
    value: str
    explanation: str


class Output(BaseOutput[DefinitionGuessCreate]):
    level: Level
    definition: str

    sentences: list[Sentence]
    alternatives: list[AnswerOption]
    distractors: list[AnswerOption]

    hint: str

    def convert(self, **kwargs) -> DefinitionGuessCreate:
        clean_kwargs = {k: v for k, v in kwargs.items() if k in DefinitionGuessCreate.model_fields}
        return DefinitionGuessCreate(
            type=PageType.DEFINITION_GUESS,
            order=0,
            **clean_kwargs,
            **self.model_dump(),
        )
