from features.languages import Language
from features.levels import Level
from pydantic import BaseModel


class TeacherDefinitionGuessCreate(BaseModel):
    language: Language
    level: Level
    phrase: str
    native_language: Language = Language.PL


class ExpressionAndDefinition(BaseModel):
    expression: str
    definition: str
