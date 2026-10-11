"""ATLAS Natural-Language Command Interpretation Package (Stage 48)."""

from .compiler import NaturalLanguageIntentCompiler
from .enums import (
    NaturalLanguageCommandIntent,
    NaturalLanguageCommandInterpretationStatus,
    UnsupportedActionReason,
)
from .errors import (
    InputTooLongError,
    InterpreterTimeoutError,
    InterpreterUnavailableError,
    InvalidModelOutputError,
    NaturalLanguageInterpreterError,
)
from .interpreter import NaturalLanguageCommandInterpreter
from .model_client import (
    CommandInterpretationModelClient,
    MockCommandInterpretationModelClient,
    OpenAICompatibleModelClient,
)
from .models import (
    INTERPRETER_VERSION,
    MODEL_OUTPUT_SCHEMA_VERSION,
    PROMPT_VERSION,
    NaturalLanguageCommandInterpretation,
    NaturalLanguageCommandInterpretRequest,
    RawModelCommandOutput,
)
from .prompt import NaturalLanguageCommandPromptBuilder
from .settings import NaturalLanguageCommandSettings

__all__ = [
    "INTERPRETER_VERSION",
    "PROMPT_VERSION",
    "MODEL_OUTPUT_SCHEMA_VERSION",
    "NaturalLanguageCommandIntent",
    "UnsupportedActionReason",
    "NaturalLanguageCommandInterpretationStatus",
    "NaturalLanguageCommandSettings",
    "NaturalLanguageCommandPromptBuilder",
    "CommandInterpretationModelClient",
    "OpenAICompatibleModelClient",
    "MockCommandInterpretationModelClient",
    "RawModelCommandOutput",
    "NaturalLanguageCommandInterpretRequest",
    "NaturalLanguageCommandInterpretation",
    "NaturalLanguageIntentCompiler",
    "NaturalLanguageCommandInterpreter",
    "NaturalLanguageInterpreterError",
    "InterpreterUnavailableError",
    "InvalidModelOutputError",
    "InterpreterTimeoutError",
    "InputTooLongError",
]
