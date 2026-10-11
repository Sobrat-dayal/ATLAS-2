"""Enums for ATLAS Natural-Language Command Interpretation (Stage 48)."""

from enum import Enum


class NaturalLanguageCommandIntent(str, Enum):
    """Allowed intent categories recognized by the command interpretation model."""

    NAVIGATE_MODULE = "NAVIGATE_MODULE"
    OPEN_ENTITY_IN_MODULE = "OPEN_ENTITY_IN_MODULE"
    OPEN_GLOBAL_SETTINGS = "OPEN_GLOBAL_SETTINGS"
    FOCUS_ENTITY_SEARCH = "FOCUS_ENTITY_SEARCH"
    CLEAR_SELECTED_ENTITY = "CLEAR_SELECTED_ENTITY"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_COMMAND = "NOT_COMMAND"
    UNSUPPORTED_ACTION = "UNSUPPORTED_ACTION"


class UnsupportedActionReason(str, Enum):
    """Specific categories of unsupported natural-language requests."""

    TRADING_ACTION = "TRADING_ACTION"
    BROKER_ACTION = "BROKER_ACTION"
    PORTFOLIO_ACTION = "PORTFOLIO_ACTION"
    RISK_ACTION = "RISK_ACTION"
    AGENT_ACTION = "AGENT_ACTION"
    WORKFLOW_ACTION = "WORKFLOW_ACTION"
    TERMINAL_ACTION = "TERMINAL_ACTION"
    SYSTEM_ACTION = "SYSTEM_ACTION"
    EXTERNAL_ACTION = "EXTERNAL_ACTION"
    MULTI_COMMAND = "MULTI_COMMAND"
    OTHER_UNSUPPORTED = "OTHER_UNSUPPORTED"


class NaturalLanguageCommandInterpretationStatus(str, Enum):
    """Final high-level status of the natural-language command interpretation."""

    READY = "READY"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_COMMAND = "NOT_COMMAND"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID_MODEL_OUTPUT = "INVALID_MODEL_OUTPUT"
    INTERPRETER_UNAVAILABLE = "INTERPRETER_UNAVAILABLE"
