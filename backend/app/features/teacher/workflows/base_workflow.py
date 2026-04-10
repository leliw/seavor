from features.languages import Language
from features.levels import Level
from pydantic import BaseModel


class BaseWorkflowSnapshot(BaseModel):
    language: Language
    level: Level
    native_language: Language
    username: str
