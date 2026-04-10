from features.languages import Language
from features.levels import Level
from pydantic import BaseModel, Field


class TeacherDefinitionGuessCreate(BaseModel):
    language: Language
    level: Level
    phrase: str
    native_language: Language = Language.PL


class ExpressionAndDefinition(BaseModel):
    expression: str
    definition: str


class EvaluationError(BaseModel):
    problem_type: str
    text_fragment: str
    suggestion: str | None = None


class Evaluation(BaseModel):
    score: int = Field(ge=0, le=100)
    errors: list[EvaluationError]
