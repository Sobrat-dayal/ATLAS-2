"""Pure, side-effect free syntactic parser for ATLAS Command Language v1."""

from typing import Dict, List, Optional

from .ast import AtlasCommandAst
from .enums import AtlasCommandErrorCode, AtlasCommandParseStatus, AtlasCommandSourceKind
from .errors import AtlasCommandParserError
from .specs import COMMAND_SPEC_REGISTRY, AtlasCommandSpecRegistry
from .tokens import Token, TokenType

RECOGNIZED_ACTIONS = {"open"}


class AtlasCommandParser:
    """Deterministic, side-effect free syntactic parser.

    Transforms token streams into an AtlasCommandAst. Rejects shell syntax,
    detects structured slash commands and recognized deterministic shorthand.
    """

    def __init__(self, registry: Optional[AtlasCommandSpecRegistry] = None):
        self.registry = registry or COMMAND_SPEC_REGISTRY

    def parse(self, tokens: List[Token], raw_text: str) -> AtlasCommandAst:
        """Parses tokens into an AtlasCommandAst.

        Raises:
            AtlasCommandParserError if the token sequence violates syntax rules
            or does not represent a valid structured command.
        """
        # Filter out trailing EOF
        content_tokens = [t for t in tokens if t.type != TokenType.EOF]

        if not content_tokens:
            raise AtlasCommandParserError(
                error_code=AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND,
                message="Command input is empty.",
            )

        first = content_tokens[0]

        # Case A: Slash command
        if first.type == TokenType.SLASH:
            return self._parse_slash_command(content_tokens, raw_text)

        # Case B: Shorthand command
        return self._parse_shorthand_command(content_tokens, raw_text)

    def _parse_slash_command(self, tokens: List[Token], raw_text: str) -> AtlasCommandAst:
        """Parses slash command grammar: /<module> [action] [target] [--param value]."""
        if len(tokens) == 1:
            # Just "/"
            raise AtlasCommandParserError(
                error_code=AtlasCommandErrorCode.UNKNOWN_COMMAND,
                message="Incomplete slash command: missing command name after '/'.",
                status=AtlasCommandParseStatus.INCOMPLETE,
                position=0,
            )

        cmd_name_token = tokens[1]
        if cmd_name_token.type != TokenType.WORD:
            raise AtlasCommandParserError(
                error_code=AtlasCommandErrorCode.UNEXPECTED_TOKEN,
                message=f"Expected command name after '/', got '{cmd_name_token.value}'.",
                raw_token=cmd_name_token.value,
                position=cmd_name_token.position,
            )

        raw_cmd_name = cmd_name_token.value.lower()
        i = 2
        n = len(tokens)

        # Special utility check: /clear entity
        if raw_cmd_name == "clear":
            if i < n and tokens[i].type == TokenType.WORD and tokens[i].value.lower() == "entity":
                i += 1
                return AtlasCommandAst(
                    source_kind=AtlasCommandSourceKind.SLASH,
                    raw_text=raw_text,
                    command_name="clear_entity",
                    action="clear",
                    target=None,
                    parameters={},
                )
            else:
                # Disallow arbitrary /clear all or /clear
                raise AtlasCommandParserError(
                    error_code=AtlasCommandErrorCode.UNKNOWN_COMMAND,
                    message="Unrecognized clear command. Only '/clear entity' is supported.",
                    position=cmd_name_token.position,
                )

        # Separate arguments and parameter flags
        arg_tokens: List[Token] = []
        parameters: Dict[str, str] = {}

        while i < n:
            token = tokens[i]

            if token.type == TokenType.PARAM_NAME:
                param_name = token.value.lower()
                if param_name in parameters:
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.DUPLICATE_PARAMETER,
                        message=f"Duplicate parameter '--{param_name}' specified.",
                        raw_token=param_name,
                        position=token.position,
                    )

                i += 1
                # Check for = or space-separated value
                if i < n and tokens[i].type == TokenType.EQUALS:
                    i += 1  # consume =

                if i < n and tokens[i].type in (TokenType.WORD, TokenType.STRING):
                    param_val = tokens[i].value
                    parameters[param_name] = param_val
                    i += 1
                else:
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.INVALID_PARAMETER_VALUE,
                        message=f"Parameter '--{param_name}' is missing a value.",
                        raw_token=param_name,
                        position=token.position,
                    )
            else:
                arg_tokens.append(token)
                i += 1

        action: Optional[str] = None
        target: Optional[str] = None

        if len(arg_tokens) == 1:
            first_arg = arg_tokens[0]
            val = first_arg.value
            if val.lower() in RECOGNIZED_ACTIONS:
                action = val.lower()
            else:
                # Default action is implied for entity-context commands
                target = val
        elif len(arg_tokens) == 2:
            first_arg = arg_tokens[0]
            second_arg = arg_tokens[1]
            if first_arg.value.lower() in RECOGNIZED_ACTIONS:
                action = first_arg.value.lower()
                target = second_arg.value
            else:
                # Unrecognized action followed by target
                raise AtlasCommandParserError(
                    error_code=AtlasCommandErrorCode.UNKNOWN_ACTION,
                    message=f"Unknown action '{first_arg.value}' for command '/{raw_cmd_name}'.",
                    raw_token=first_arg.value,
                    position=first_arg.position,
                )
        elif len(arg_tokens) > 2:
            msg = (
                f"Too many arguments for command '/{raw_cmd_name}'. "
                "Use quotes for multi-word targets."
            )
            raise AtlasCommandParserError(
                error_code=AtlasCommandErrorCode.UNEXPECTED_TOKEN,
                message=msg,
                raw_token=arg_tokens[2].value,
                position=arg_tokens[2].position,
            )

        return AtlasCommandAst(
            source_kind=AtlasCommandSourceKind.SLASH,
            raw_text=raw_text,
            command_name=raw_cmd_name,
            action=action,
            target=target,
            parameters=parameters,
        )

    def _parse_shorthand_command(self, tokens: List[Token], raw_text: str) -> AtlasCommandAst:
        """Parses Bloomberg-style deterministic shorthand commands."""
        # 1. Exact match (e.g. PORT RISK)
        words = [t.value for t in tokens if t.type in (TokenType.WORD, TokenType.STRING)]
        joined_upper = " ".join(words).upper()

        exact_spec = self.registry.find_shorthand_exact(joined_upper)
        if exact_spec:
            return AtlasCommandAst(
                source_kind=AtlasCommandSourceKind.SHORTHAND,
                raw_text=raw_text,
                command_name=exact_spec.module_id,
                action=exact_spec.action,
                target=None,
                parameters={},
            )

        # 2. Suffix match (e.g. <TARGET> CHART, <TARGET> NEWS, <TARGET> FA)
        last_token = tokens[-1]
        if last_token.type == TokenType.WORD:
            suffix_spec = self.registry.find_shorthand_by_suffix(last_token.value)
            if suffix_spec:
                target_tokens = tokens[:-1]
                if not target_tokens:
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.MISSING_TARGET,
                        message=f"Target required for shorthand action '{suffix_spec.keyword}'.",
                        status=AtlasCommandParseStatus.INCOMPLETE,
                        position=last_token.position,
                    )
                if len(target_tokens) == 1:
                    target_val = target_tokens[0].value
                else:
                    # Section 70: Multi-word targets must be quoted
                    msg = (
                        "Unquoted multi-word text is not a structured ATLAS command. "
                        "Multi-word targets must be quoted."
                    )
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND,
                        message=msg,
                        position=target_tokens[1].position,
                    )

                return AtlasCommandAst(
                    source_kind=AtlasCommandSourceKind.SHORTHAND,
                    raw_text=raw_text,
                    command_name=suffix_spec.module_id,
                    action=suffix_spec.action,
                    target=target_val,
                    parameters={},
                )

        # 3. Prefix match (e.g. MAP <TARGET>, OPTIONS <TARGET>, BUY <TARGET>, SELL <TARGET>)
        first_token = tokens[0]
        if first_token.type == TokenType.WORD:
            prefix_spec = self.registry.find_shorthand_by_prefix(first_token.value)
            if prefix_spec:
                target_tokens = tokens[1:]
                if not target_tokens:
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.MISSING_TARGET,
                        message=f"Target required for shorthand command '{prefix_spec.keyword}'.",
                        status=AtlasCommandParseStatus.INCOMPLETE,
                        position=first_token.position,
                    )
                if len(target_tokens) == 1:
                    target_val = target_tokens[0].value
                else:
                    # Section 70: Multi-word targets must be quoted
                    msg = (
                        "Unquoted multi-word text is not a structured ATLAS command. "
                        "Multi-word targets must be quoted."
                    )
                    raise AtlasCommandParserError(
                        error_code=AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND,
                        message=msg,
                        position=target_tokens[1].position,
                    )

                return AtlasCommandAst(
                    source_kind=AtlasCommandSourceKind.SHORTHAND,
                    raw_text=raw_text,
                    command_name=prefix_spec.module_id,
                    action=prefix_spec.action,
                    target=target_val,
                    parameters={},
                )

        # If neither slash nor recognized shorthand, reject as non-structured
        raise AtlasCommandParserError(
            error_code=AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND,
            message="Not a recognized ATLAS structured command.",
        )
