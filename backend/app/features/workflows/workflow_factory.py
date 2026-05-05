from dataclasses import dataclass

from features.repetitions.repetition_service import RepetitionService
from features.workflows.definition_guess_workflow import DefinitionGuessWorkflow


@dataclass
class WorkflowFactory:
    repetition_service: RepetitionService

    def create_definition_guess_workflow(self) -> DefinitionGuessWorkflow:
        return DefinitionGuessWorkflow(**{k: v for k, v in self.__dict__.items() if not k.startswith("_")})
