from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .prompt_model import PromptSet


class PromptService:
    def __init__(self, root_path: str | Path) -> None:
        self.root_path = Path(root_path)
        self.env = Environment(
            loader=FileSystemLoader(self.root_path),
            autoescape=False,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self.registry: Dict[str, PromptSet] = {}

    def load_prompt(self, prompt_path: Path | str) -> PromptSet:
        if isinstance(prompt_path, str):
            prompt_path = self.root_path / prompt_path

        if prompt_path.is_dir() and not prompt_path.name.startswith("_"):
            system_path = prompt_path / "system.jinja"
            user_path = prompt_path / "user.jinja"

            if system_path.exists() and user_path.exists():
                return PromptSet(
                    name=prompt_path.name,
                    system=self.env.get_template(f"{prompt_path.name}/system.jinja"),
                    user=self.env.get_template(f"{prompt_path.name}/user.jinja"),
                    version="1.0.0",
                )
        raise ValueError(f"Prompt set {prompt_path} not found")


    def load_all_prompts(self) -> Dict[str, PromptSet]:
        self.registry: Dict[str, PromptSet] = {}

        for item in self.root_path.iterdir():
            self.registry[item.name] = self.load_prompt(item)
        return self.registry



    def render(self, prompt_name: str, **kwargs) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) ready for OpenAI/VertexAI messages

        Args:
            prompt_name: name of the prompt set to render
            **kwargs: variables to render in the prompt templates
        Returns:
            tuple[str, str]: (system_prompt, user_prompt)
        """
        if prompt_name not in self.registry:
            self.registry[prompt_name] = self.load_prompt(prompt_name)
        return self.registry[prompt_name].render(**kwargs)
