from features.workflows.definition_guess_workflow import DefinitionGuessWorkflow, DefinitionGuessWorkflowContext


class WorkflowFactory:
    def create_definition_guess_workflow(self) -> DefinitionGuessWorkflow:
        return DefinitionGuessWorkflow()

    def create_for_context(self, context: DefinitionGuessWorkflowContext) -> DefinitionGuessWorkflow:
        return self.create_definition_guess_workflow()
