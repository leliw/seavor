from features.pages.page_base_model import PageType
from features.pages.page_model import InfoPageCreate
from shared.prompts.prompt_model import BaseOutput


class Output(BaseOutput[InfoPageCreate]):
    content: str

    def convert(self, **kwargs) -> InfoPageCreate:
        return InfoPageCreate(
            order=0,
            type=PageType.INFO,
            **kwargs,
            **self.model_dump(),
        )
