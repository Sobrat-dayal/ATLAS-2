"""Workflow definition and validation errors."""


class WorkflowError(Exception):
    """Base workflow error."""


class WorkflowNotFoundError(WorkflowError):
    """Workflow is not visible to the requesting principal."""


class WorkflowValidationError(WorkflowError):
    """Workflow graph is invalid or unsupported."""

    def __init__(self, messages: list[str] | str):
        self.messages = [messages] if isinstance(messages, str) else messages
        super().__init__("; ".join(self.messages))