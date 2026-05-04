from features.native_pages.native_page_model import NativeInfoPageBase as NativeInfoPageBaseOrg
from haintech.ai.prompts.prompt_model import BaseOutput


class NativeInfoPageBase(BaseOutput[NativeInfoPageBaseOrg]):
    native_title: str
    native_content: str

    def convert(self, **kwargs) -> NativeInfoPageBaseOrg:
        clean_kwargs = {k: v for k, v in kwargs.items() if k in NativeInfoPageBaseOrg.model_fields}
        return NativeInfoPageBaseOrg(
            **clean_kwargs,
            **self.model_dump(),
        )
