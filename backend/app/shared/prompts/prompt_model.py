from dataclasses import dataclass

from jinja2 import Template

@dataclass
class PromptSet:
    name: str
    system: Template
    user: Template
    version: str = "1.0.0"

    def render(self, **kwargs) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) ready for OpenAI/VertexAI messages"""
        system = self.system.render(**kwargs)
        user = self.user.render(**kwargs)
        return system.strip(), user.strip()
