"""Service orchestrating deterministic parsing, semantic binding,
target resolution and authorization.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.authorization.service import AuthorizationContext

from .binder import AtlasCommandBinder, BoundAtlasCommand
from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus
from .errors import AtlasCommandError
from .lexer import AtlasCommandLexer
from .models import AtlasCommandParseResult
from .parser import AtlasCommandParser
from .resolver import AtlasCommandTargetResolver
from .specs import COMMAND_SPEC_REGISTRY, AtlasCommandSpecRegistry


class AtlasCommandParsingService:
    """Orchestrates ATLAS command pipeline from raw string to bound, authorized execution plan.

    Pure, deterministic and side-effect free:
    - 0 database mutations
    - 0 Redis calls
    - 0 ClickHouse queries
    - 0 Provider / OpenBB calls
    - 0 LLM calls
    """

    def __init__(
        self,
        session: AsyncSession,
        registry: Optional[AtlasCommandSpecRegistry] = None,
    ):
        self.session = session
        self.registry = registry or COMMAND_SPEC_REGISTRY
        self.lexer = AtlasCommandLexer()
        self.parser = AtlasCommandParser(self.registry)
        self.binder = AtlasCommandBinder(self.registry)
        self.resolver = AtlasCommandTargetResolver(session)

    async def parse_command(
        self,
        text: str,
        authz_context: Optional[AuthorizationContext] = None,
    ) -> AtlasCommandParseResult:
        """Parses, binds, validates and resolves command text into an execution-ready plan."""
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return AtlasCommandParseResult(
                status=AtlasCommandParseStatus.INVALID,
                error_code=AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND,
                error_message="Command text cannot be empty.",
                normalized_command="",
            )

        # Phase 1 & 2: Tokenize
        try:
            tokens = self.lexer.tokenize(cleaned_text)
        except AtlasCommandError as err:
            return AtlasCommandParseResult(
                status=err.status,
                error_code=err.error_code,
                error_message=err.message,
                normalized_command=cleaned_text,
            )

        # Phase 3: Syntactic parsing into AST
        try:
            ast = self.parser.parse(tokens, cleaned_text)
        except AtlasCommandError as err:
            return AtlasCommandParseResult(
                status=err.status,
                error_code=err.error_code,
                error_message=err.message,
                normalized_command=cleaned_text,
            )

        # Phase 4: Semantic binding
        try:
            bound: BoundAtlasCommand = self.binder.bind(ast)
        except AtlasCommandError as err:
            return AtlasCommandParseResult(
                status=err.status,
                source_kind=ast.source_kind,
                error_code=err.error_code,
                error_message=err.message,
                normalized_command=cleaned_text,
            )

        # Phase 5: Check command availability
        if not bound.available:
            return AtlasCommandParseResult(
                status=AtlasCommandParseStatus.UNAVAILABLE,
                source_kind=bound.source_kind,
                command_id=bound.command_id,
                module=bound.module_id,
                action=bound.action,
                raw_target=bound.raw_target,
                error_code=AtlasCommandErrorCode.COMMAND_UNAVAILABLE,
                error_message=bound.unavailable_reason
                or "Recognized, but this command is not available yet in ATLAS v1.",
                normalized_command=cleaned_text,
            )

        # Phase 6: Check authorization
        if authz_context and bound.required_permission:
            if not authz_context.has_permission(bound.required_permission):
                return AtlasCommandParseResult(
                    status=AtlasCommandParseStatus.INVALID,
                    source_kind=bound.source_kind,
                    command_id=bound.command_id,
                    module=bound.module_id,
                    action=bound.action,
                    raw_target=bound.raw_target,
                    error_code=AtlasCommandErrorCode.COMMAND_FORBIDDEN,
                    error_message=(
                        f"You do not have permission to access the {bound.module_id} module."
                    ),
                    normalized_command=cleaned_text,
                )

        # Phase 7: Target resolution (if required)
        if bound.target_required:
            if not bound.raw_target:
                return AtlasCommandParseResult(
                    status=AtlasCommandParseStatus.INCOMPLETE,
                    source_kind=bound.source_kind,
                    command_id=bound.command_id,
                    module=bound.module_id,
                    action=bound.action,
                    error_code=AtlasCommandErrorCode.MISSING_TARGET,
                    error_message="A target entity is required for this command.",
                    normalized_command=cleaned_text,
                )

            outcome = await self.resolver.resolve(
                raw_target=bound.raw_target,
                allowed_entity_types=bound.allowed_target_entity_types,
            )

            if outcome.status != AtlasCommandParseStatus.READY:
                return AtlasCommandParseResult(
                    status=outcome.status,
                    source_kind=bound.source_kind,
                    command_id=bound.command_id,
                    module=bound.module_id,
                    action=bound.action,
                    raw_target=bound.raw_target,
                    error_code=outcome.error_code,
                    error_message=outcome.error_message,
                    ambiguity_candidates=outcome.ambiguity_candidates,
                    normalized_command=cleaned_text,
                )

            # Target resolved successfully
            resolved = outcome.resolved_target
            arguments = {"entityId": str(resolved.entity_id)}
            module_label = (bound.module_id or "Module").capitalize()
            exec_summary = f"Run command: {resolved.display_name} → {module_label}"

            return AtlasCommandParseResult(
                status=AtlasCommandParseStatus.READY,
                source_kind=bound.source_kind,
                command_id=bound.command_id,
                module=bound.module_id,
                action=bound.action,
                raw_target=bound.raw_target,
                resolved_target=resolved,
                arguments=arguments,
                execution_summary=exec_summary,
                normalized_command=cleaned_text,
            )

        # Target-less command (module navigation or utility)
        if bound.module_id:
            exec_summary = f"Navigate to {bound.module_id.capitalize()}"
        elif bound.command_id == "settings.global.open":
            exec_summary = "Open Global Settings"
        elif bound.command_id == "search.focus":
            exec_summary = "Focus Global Search"
        elif bound.command_id == "entity.selection.clear":
            exec_summary = "Clear Selected Entity"
        else:
            exec_summary = f"Run command {bound.command_id}"

        return AtlasCommandParseResult(
            status=AtlasCommandParseStatus.READY,
            source_kind=bound.source_kind,
            command_id=bound.command_id,
            module=bound.module_id,
            action=bound.action,
            arguments={},
            execution_summary=exec_summary,
            normalized_command=cleaned_text,
        )
