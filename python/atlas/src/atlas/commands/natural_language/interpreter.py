"""Interpreter service orchestrating natural-language command classification
and Stage 47 binding.
"""

import hashlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.authorization.service import AuthorizationContext
from atlas.commands.enums import AtlasCommandParseStatus
from atlas.commands.service import AtlasCommandParsingService

from .compiler import NaturalLanguageIntentCompiler
from .enums import (
    NaturalLanguageCommandIntent,
    NaturalLanguageCommandInterpretationStatus,
    UnsupportedActionReason,
)
from .errors import (
    InterpreterTimeoutError,
    InterpreterUnavailableError,
    InvalidModelOutputError,
)
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
    RawModelCommandOutput,
)
from .prompt import NaturalLanguageCommandPromptBuilder
from .settings import NaturalLanguageCommandSettings

UNSUPPORTED_MESSAGES = {
    UnsupportedActionReason.TRADING_ACTION: (
        "Trading and broker actions are not available through natural-language commands."
    ),
    UnsupportedActionReason.BROKER_ACTION: (
        "Broker operations are not available through natural-language commands."
    ),
    UnsupportedActionReason.PORTFOLIO_ACTION: (
        "Portfolio rebalancing and management actions are deferred to a future stage."
    ),
    UnsupportedActionReason.RISK_ACTION: (
        "Portfolio risk calculations are deferred to a future stage."
    ),
    UnsupportedActionReason.AGENT_ACTION: (
        "Autonomous agent creation and execution are not supported here."
    ),
    UnsupportedActionReason.WORKFLOW_ACTION: (
        "Workflow creation and execution are not supported here."
    ),
    UnsupportedActionReason.TERMINAL_ACTION: (
        "Terminal and shell commands cannot be executed through this interface."
    ),
    UnsupportedActionReason.SYSTEM_ACTION: (
        "System and operating system commands are strictly prohibited."
    ),
    UnsupportedActionReason.EXTERNAL_ACTION: (
        "External communications and arbitrary URL navigation are not supported."
    ),
    UnsupportedActionReason.MULTI_COMMAND: (
        "Multiple commands cannot be chained in a single instruction."
    ),
    UnsupportedActionReason.OTHER_UNSUPPORTED: (
        "This action is not currently supported in ATLAS v1."
    ),
}


class NaturalLanguageCommandInterpreter:
    """Interprets human instructions into validated, executable Stage 47 commands.

    Strict security invariant:
    The model classifies intent only. It does not execute commands, navigate, resolve
    entities, grant permissions, or call providers. Every executable intent is compiled
    into canonical Stage 47 syntax and reparsed through Stage 47.
    """

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        settings: Optional[NaturalLanguageCommandSettings] = None,
        model_client: Optional[CommandInterpretationModelClient] = None,
        parsing_service: Optional[AtlasCommandParsingService] = None,
        parser_service: Optional[AtlasCommandParsingService] = None,
    ):
        self.session = session
        self.settings = settings or NaturalLanguageCommandSettings()
        self.prompt_builder = NaturalLanguageCommandPromptBuilder()
        self.compiler = NaturalLanguageIntentCompiler()

        chosen_service = parsing_service or parser_service
        if chosen_service:
            self.parsing_service = chosen_service
        elif session:
            self.parsing_service = AtlasCommandParsingService(session)
        else:
            from unittest.mock import AsyncMock

            self.parsing_service = AtlasCommandParsingService(AsyncMock())

        if model_client:
            self.model_client = model_client
        elif self.settings.mock_mode:
            self.model_client = MockCommandInterpretationModelClient(self.settings)
        else:
            self.model_client = OpenAICompatibleModelClient(self.settings)

    async def interpret_command(
        self,
        text: str,
        authz_context: Optional[AuthorizationContext] = None,
    ) -> NaturalLanguageCommandInterpretation:
        """Single-turn natural-language interpretation pipeline."""
        cleaned_text = (text or "").strip()
        fingerprint = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()

        # Phase 1: Input Validation
        if not cleaned_text:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.NOT_COMMAND,
                input_fingerprint=fingerprint,
                error_message="Command text cannot be empty.",
            )

        if len(cleaned_text) > self.settings.max_input_characters:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT,
                input_fingerprint=fingerprint,
                error_code="INPUT_TOO_LONG",
                error_message=(
                    f"Input text exceeds maximum length of "
                    f"{self.settings.max_input_characters} characters."
                ),
            )

        # Phase 2: Check Interpreter Enabled
        if not self.settings.enabled:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INTERPRETER_UNAVAILABLE,
                input_fingerprint=fingerprint,
                error_code="INTERPRETER_DISABLED",
                error_message="Natural language command interpretation is disabled in settings.",
            )

        # Phase 3: Invoke Model Client (strictly 1 normal call)
        try:
            raw_output: RawModelCommandOutput = await self.model_client.interpret(
                cleaned_text,
                self.prompt_builder,
            )
        except InterpreterTimeoutError as err:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INTERPRETER_UNAVAILABLE,
                input_fingerprint=fingerprint,
                error_code=err.error_code,
                error_message="Model request timed out. Please try again.",
            )
        except InterpreterUnavailableError as err:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INTERPRETER_UNAVAILABLE,
                input_fingerprint=fingerprint,
                error_code=err.error_code,
                error_message="Natural-language interpretation is temporarily unavailable.",
            )
        except InvalidModelOutputError as err:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT,
                input_fingerprint=fingerprint,
                error_code=err.error_code,
                error_message="ATLAS could not safely interpret this command.",
            )

        # Phase 4: Handle Non-Executable Intents
        if raw_output.intent == NaturalLanguageCommandIntent.NOT_COMMAND:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.NOT_COMMAND,
                input_fingerprint=fingerprint,
                intent=raw_output.intent,
                error_message=(
                    "This looks like a question or general inquiry rather than an ATLAS command."
                ),
            )

        if raw_output.intent == NaturalLanguageCommandIntent.UNSUPPORTED_ACTION:
            reason = raw_output.unsupported_reason or UnsupportedActionReason.OTHER_UNSUPPORTED
            default_unsupported = UNSUPPORTED_MESSAGES[UnsupportedActionReason.OTHER_UNSUPPORTED]
            msg = UNSUPPORTED_MESSAGES.get(reason, default_unsupported)
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.UNSUPPORTED,
                input_fingerprint=fingerprint,
                intent=raw_output.intent,
                unsupported_reason=reason,
                error_message=msg,
            )

        if raw_output.intent == NaturalLanguageCommandIntent.AMBIGUOUS:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.AMBIGUOUS,
                input_fingerprint=fingerprint,
                intent=raw_output.intent,
                clarification_question=raw_output.clarification_question
                or "Please specify which ATLAS module or action you would like to run.",
            )

        # Phase 5: Compile Intent into Canonical Stage 47 Syntax
        try:
            canonical_command = self.compiler.compile(raw_output)
        except InvalidModelOutputError as err:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT,
                input_fingerprint=fingerprint,
                intent=raw_output.intent,
                module=raw_output.module,
                target_text=raw_output.target_text,
                error_code=err.error_code,
                error_message=err.message,
            )

        if not canonical_command:
            return NaturalLanguageCommandInterpretation(
                status=NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT,
                input_fingerprint=fingerprint,
                intent=raw_output.intent,
                error_code="COMPILATION_FAILED",
                error_message="Failed to compile intent into a valid ATLAS command.",
            )

        # Phase 6: Reparse and Bind via Stage 47
        stage47_result = await self.parsing_service.parse_command(
            canonical_command,
            authz_context=authz_context,
        )

        # Phase 7: Map Stage 47 Result to Interpretation Status
        if stage47_result.status == AtlasCommandParseStatus.READY:
            status = NaturalLanguageCommandInterpretationStatus.READY
        elif stage47_result.status == AtlasCommandParseStatus.AMBIGUOUS:
            status = NaturalLanguageCommandInterpretationStatus.AMBIGUOUS
        elif stage47_result.status == AtlasCommandParseStatus.UNAVAILABLE:
            status = NaturalLanguageCommandInterpretationStatus.UNSUPPORTED
        elif stage47_result.status == AtlasCommandParseStatus.INVALID:
            if stage47_result.error_code in (
                "TARGET_NOT_FOUND",
                "TARGET_TYPE_MISMATCH",
                "TARGET_AMBIGUOUS",
            ):
                status = NaturalLanguageCommandInterpretationStatus.AMBIGUOUS
            else:
                status = NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT
        else:
            status = NaturalLanguageCommandInterpretationStatus.INVALID_MODEL_OUTPUT

        return NaturalLanguageCommandInterpretation(
            interpreter_version=INTERPRETER_VERSION,
            prompt_version=PROMPT_VERSION,
            model_output_schema_version=MODEL_OUTPUT_SCHEMA_VERSION,
            status=status,
            input_fingerprint=fingerprint,
            intent=raw_output.intent,
            module=raw_output.module,
            target_text=raw_output.target_text,
            canonical_command=canonical_command,
            structured_parse_result=stage47_result,
            error_code=stage47_result.error_code,
            error_message=stage47_result.error_message,
        )

    async def interpret(
        self,
        user_text: str,
        authz_context: Optional[AuthorizationContext] = None,
        principal: Optional[object] = None,
    ) -> NaturalLanguageCommandInterpretation:
        """Alias for interpret_command supporting (user_text, principal, authz_context)."""
        return await self.interpret_command(
            text=user_text,
            authz_context=authz_context,
        )
