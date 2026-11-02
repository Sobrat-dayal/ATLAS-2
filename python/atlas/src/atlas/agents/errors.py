"""Errors raised by the Stage 146 agent foundation."""


class AgentError(Exception):
    """Base error for agent registry operations."""


class AgentNotFoundError(AgentError):
    """The requested agent or run is not visible to the caller."""


class AgentValidationError(AgentError):
    """The requested agent configuration is invalid."""