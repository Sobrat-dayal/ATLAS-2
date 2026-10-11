"""Pydantic models for ATLAS Natural-Language Command Interpretation (Stage 48)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.commands.models import AtlasCommandParseResult

from .enums import (
    NaturalLanguageCommandIntent,
    NaturalLanguageCommandInterpretationStatus,
    UnsupportedActionReason,
)

INTERPRETER_VERSION: int = 1
PROMPT_VERSION: int = 1
MODEL_OUTPUT_SCHEMA_VERSION: int = 1


class RawModelCommandOutput(BaseModel):
    """Strict schema for the JSON output returned by the command interpretation model.

    Extra fields are strictly forbidden to reject hallucinated attributes (e.g., entity IDs,
    command IDs, routes, code, etc.).
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(
        default=MODEL_OUTPUT_SCHEMA_VERSION,
        description="Schema version of the model output.",
    )
    intent: NaturalLanguageCommandIntent = Field(
        ...,
        description="The recognized command intent.",
    )
    module: Optional[str] = Field(
        default=None,
        description="Canonical module ID when intent requires a destination module.",
    )
    target_text: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Target entity text extracted verbatim from user input without transformation.",
    )
    unsupported_reason: Optional[UnsupportedActionReason] = Field(
        default=None,
        description="Reason category when intent is UNSUPPORTED_ACTION.",
    )
    clarification_question: Optional[str] = Field(
        default=None,
        max_length=160,
        description="Optional clarification text when intent is AMBIGUOUS.",
    )

    @model_validator(mode="after")
    def validate_intent_contracts(self) -> "RawModelCommandOutput":
        """Enforces conditional validation rules based on intent."""
        if self.intent == NaturalLanguageCommandIntent.OPEN_ENTITY_IN_MODULE:
            if not self.module or not self.module.strip():
                raise ValueError("OPEN_ENTITY_IN_MODULE requires a non-empty 'module'.")
            if not self.target_text or not self.target_text.strip():
                raise ValueError("OPEN_ENTITY_IN_MODULE requires a non-empty 'target_text'.")

        elif self.intent == NaturalLanguageCommandIntent.NAVIGATE_MODULE:
            if not self.module or not self.module.strip():
                raise ValueError("NAVIGATE_MODULE requires a non-empty 'module'.")
            if self.target_text is not None:
                raise ValueError("NAVIGATE_MODULE must have null 'target_text'.")

        elif self.intent in (
            NaturalLanguageCommandIntent.OPEN_GLOBAL_SETTINGS,
            NaturalLanguageCommandIntent.FOCUS_ENTITY_SEARCH,
            NaturalLanguageCommandIntent.CLEAR_SELECTED_ENTITY,
        ):
            if self.module is not None:
                raise ValueError(f"{self.intent} must have null 'module'.")
            if self.target_text is not None:
                raise ValueError(f"{self.intent} must have null 'target_text'.")

        elif self.intent == NaturalLanguageCommandIntent.UNSUPPORTED_ACTION:
            if not self.unsupported_reason:
                raise ValueError("UNSUPPORTED_ACTION requires an 'unsupported_reason'.")

        return self


class NaturalLanguageCommandInterpretRequest(BaseModel):
    """Request payload sent by client to interpret natural language command text."""

    text: str = Field(
        ...,
        max_length=1000,
        description="Natural language instruction text to interpret.",
    )


class NaturalLanguageCommandInterpretation(BaseModel):
    """Validated response payload returned to client following interpretation and binding."""

    interpreter_version: int = Field(default=INTERPRETER_VERSION)
    prompt_version: int = Field(default=PROMPT_VERSION)
    model_output_schema_version: int = Field(default=MODEL_OUTPUT_SCHEMA_VERSION)

    status: NaturalLanguageCommandInterpretationStatus = Field(
        ...,
        description="Status of the interpretation.",
    )
    input_fingerprint: str = Field(
        ...,
        description="SHA-256 fingerprint of the normalized input text for stale response defense.",
    )
    intent: Optional[NaturalLanguageCommandIntent] = None
    module: Optional[str] = None
    target_text: Optional[str] = None
    canonical_command: Optional[str] = None

    structured_parse_result: Optional[AtlasCommandParseResult] = None
    clarification_question: Optional[str] = None
    unsupported_reason: Optional[UnsupportedActionReason] = None

    error_code: Optional[str] = None
    error_message: Optional[str] = None
