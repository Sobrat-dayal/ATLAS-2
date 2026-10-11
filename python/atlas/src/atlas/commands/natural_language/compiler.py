"""Intent compiler for ATLAS Natural-Language Command Interpretation (Stage 48)."""

from typing import Optional

from atlas.commands.specs import COMMAND_SPEC_REGISTRY, AtlasCommandSpecRegistry

from .enums import NaturalLanguageCommandIntent
from .errors import InvalidModelOutputError
from .models import RawModelCommandOutput


class NaturalLanguageIntentCompiler:
    """Compiles validated intermediate model intents into canonical Stage 47 command strings."""

    def __init__(self, registry: Optional[AtlasCommandSpecRegistry] = None):
        self.registry = registry or COMMAND_SPEC_REGISTRY

    def compile(self, output: RawModelCommandOutput) -> Optional[str]:
        """Translates a structured model output into canonical Stage 47 command syntax.

        Returns None if intent is non-executable (e.g. NOT_COMMAND, AMBIGUOUS, UNSUPPORTED_ACTION).
        """
        if output.intent == NaturalLanguageCommandIntent.NAVIGATE_MODULE:
            if not output.module:
                raise InvalidModelOutputError("NAVIGATE_MODULE intent missing destination module.")
            mod_spec = self.registry.resolve_module_by_name_or_alias(output.module)
            if not mod_spec:
                raise InvalidModelOutputError(
                    f"Module '{output.module}' is not a recognized module."
                )
            return f"/{mod_spec.canonical_slash_name}"

        elif output.intent == NaturalLanguageCommandIntent.OPEN_ENTITY_IN_MODULE:
            if not output.module or not output.target_text:
                raise InvalidModelOutputError(
                    "OPEN_ENTITY_IN_MODULE requires both module and target_text."
                )
            mod_spec = self.registry.resolve_module_by_name_or_alias(output.module)
            if not mod_spec:
                raise InvalidModelOutputError(
                    f"Module '{output.module}' is not a recognized module."
                )
            if not mod_spec.supports_entity_context:
                raise InvalidModelOutputError(
                    f"Module '{output.module}' does not support entity-context navigation."
                )

            # Safely escape backslashes and double quotes under Stage 47 lexer rules
            escaped_target = output.target_text.replace("\\", "\\\\").replace('"', '\\"')
            return f'/{mod_spec.canonical_slash_name} "{escaped_target}"'

        elif output.intent == NaturalLanguageCommandIntent.OPEN_GLOBAL_SETTINGS:
            return "/settings"

        elif output.intent == NaturalLanguageCommandIntent.FOCUS_ENTITY_SEARCH:
            return "/search"

        elif output.intent == NaturalLanguageCommandIntent.CLEAR_SELECTED_ENTITY:
            return "/clear entity"

        # Non-executable intents
        return None
