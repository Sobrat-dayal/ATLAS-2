"""Pure, side-effect free lexical analyzer for ATLAS Command Language v1."""

import re
from typing import List

from .enums import AtlasCommandErrorCode
from .errors import AtlasCommandLexerError
from .tokens import Token, TokenType

# Input limits (Section 51-54)
MAX_COMMAND_LENGTH = 512
MAX_TOKENS = 32
MAX_TOKEN_LENGTH = 256
MAX_PARAMETERS = 16

# Dangerous control character pattern: \x00-\x08, \x0b, \x0c, \x0e-\x1f, \x7f
CONTROL_CHAR_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Forbidden shell syntax (Sections 36-41)
FORBIDDEN_SHELL_PATTERNS = [
    ("&&", "&&"),
    ("||", "||"),
    (">>", ">>"),
    ("<<", "<<"),
    ("$()", "$()"),
    ("${}", "${}"),
    ("|", "|"),
    ("&", "&"),
    (";", ";"),
    (">", ">"),
    ("<", "<"),
    ("`", "`"),
    ("$(", "$("),
    ("${", "${"),
]

# Parameter name pattern: [a-z][a-z0-9-]*
PARAM_NAME_REGEX = re.compile(r"^[a-z][a-z0-9-]*$")


class AtlasCommandLexer:
    """Deterministic, side-effect free scanner for ATLAS Command Language v1.

    Guarantees strict input bounds, rejection of shell control operators,
    support for quoted strings with safe escapes, and parameter flags.
    """

    def __init__(
        self,
        max_command_length: int = MAX_COMMAND_LENGTH,
        max_tokens: int = MAX_TOKENS,
        max_token_length: int = MAX_TOKEN_LENGTH,
    ):
        self.max_command_length = max_command_length
        self.max_tokens = max_tokens
        self.max_token_length = max_token_length

    def tokenize(self, text: str) -> List[Token]:
        """Tokenizes raw command input into a sequence of Tokens.

        Raises:
            AtlasCommandLexerError on bounded security limit violations,
            forbidden syntax, unterminated quotes, or control characters.
        """
        if text is None:
            text = ""

        # 1. Check maximum command length
        if len(text) > self.max_command_length:
            raise AtlasCommandLexerError(
                error_code=AtlasCommandErrorCode.COMMAND_TOO_LONG,
                message=(
                    f"Command text exceeds maximum length of {self.max_command_length} "
                    f"characters (length={len(text)})."
                ),
                position=self.max_command_length,
            )

        # 2. Check for non-display/dangerous control characters
        match_ctrl = CONTROL_CHAR_REGEX.search(text)
        if match_ctrl:
            raise AtlasCommandLexerError(
                error_code=AtlasCommandErrorCode.CONTROL_CHARACTERS,
                message="Non-display control characters are not permitted.",
                position=match_ctrl.start(),
            )

        # 3. Check for forbidden shell syntax operators
        for pattern, symbol in FORBIDDEN_SHELL_PATTERNS:
            idx = text.find(pattern)
            if idx != -1:
                raise AtlasCommandLexerError(
                    error_code=AtlasCommandErrorCode.FORBIDDEN_SYNTAX,
                    message=(
                        f"Forbidden shell syntax '{symbol}' is not supported in ATLAS commands."
                    ),
                    raw_token=symbol,
                    position=idx,
                )

        tokens: List[Token] = []
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]

            # Skip standard whitespace
            if ch.isspace():
                i += 1
                continue

            # Enforce max tokens
            if len(tokens) >= self.max_tokens:
                raise AtlasCommandLexerError(
                    error_code=AtlasCommandErrorCode.TOO_MANY_TOKENS,
                    message=f"Command exceeds maximum token limit of {self.max_tokens} tokens.",
                    position=i,
                )

            # Slash operator
            if ch == "/":
                tokens.append(Token(type=TokenType.SLASH, value="/", position=i, raw_length=1))
                i += 1
                continue

            # Equals sign (only outside of quotes / words)
            if ch == "=":
                tokens.append(Token(type=TokenType.EQUALS, value="=", position=i, raw_length=1))
                i += 1
                continue

            # Parameter flag: starts with --
            if ch == "-" and i + 1 < n and text[i + 1] == "-":
                param_pos = i
                i += 2  # skip --
                name_start = i
                # Read parameter name until whitespace or =
                while i < n and not text[i].isspace() and text[i] != "=":
                    i += 1
                raw_name = text[name_start:i]

                if not raw_name or not PARAM_NAME_REGEX.match(raw_name):
                    raise AtlasCommandLexerError(
                        error_code=AtlasCommandErrorCode.UNEXPECTED_TOKEN,
                        message=(
                            f"Invalid parameter name '--{raw_name}'. "
                            "Names must match [a-z][a-z0-9-]*."
                        ),
                        raw_token=f"--{raw_name}",
                        position=param_pos,
                    )

                if len(raw_name) + 2 > self.max_token_length:
                    msg = f"Parameter name exceeds max length of {self.max_token_length}."
                    raise AtlasCommandLexerError(
                        error_code=AtlasCommandErrorCode.TOKEN_TOO_LONG,
                        message=msg,
                        position=param_pos,
                    )

                tokens.append(
                    Token(
                        type=TokenType.PARAM_NAME,
                        value=raw_name,
                        position=param_pos,
                        raw_length=i - param_pos,
                    )
                )

                # Check if immediately followed by = without whitespace
                if i < n and text[i] == "=":
                    tokens.append(Token(type=TokenType.EQUALS, value="=", position=i, raw_length=1))
                    i += 1
                continue

            # Quoted string ("..." or '...')
            if ch in ('"', "'"):
                quote_char = ch
                quote_pos = i
                i += 1  # skip opening quote
                val_chars = []
                closed = False

                while i < n:
                    curr = text[i]
                    if curr == "\\":
                        # Limited safe escapes: \", \', \\
                        if i + 1 < n:
                            next_ch = text[i + 1]
                            if next_ch in ('"', "'", "\\"):
                                val_chars.append(next_ch)
                                i += 2
                                continue
                            else:
                                # Normal backslash followed by other char
                                val_chars.append("\\")
                                i += 1
                                continue
                        else:
                            val_chars.append("\\")
                            i += 1
                            continue
                    elif curr == quote_char:
                        closed = True
                        i += 1  # skip closing quote
                        break
                    else:
                        val_chars.append(curr)
                        i += 1

                if not closed:
                    raise AtlasCommandLexerError(
                        error_code=AtlasCommandErrorCode.UNTERMINATED_QUOTE,
                        message=f"Unterminated quoted string starting at position {quote_pos}.",
                        position=quote_pos,
                    )

                val_str = "".join(val_chars)
                raw_len = i - quote_pos
                if len(val_str) > self.max_token_length:
                    msg = f"Quoted string token exceeds max length of {self.max_token_length}."
                    raise AtlasCommandLexerError(
                        error_code=AtlasCommandErrorCode.TOKEN_TOO_LONG,
                        message=msg,
                        position=quote_pos,
                    )

                tokens.append(
                    Token(
                        type=TokenType.STRING,
                        value=val_str,
                        position=quote_pos,
                        raw_length=raw_len,
                    )
                )
                continue

            # General word / identifier
            word_pos = i
            word_chars = []
            while i < n:
                curr = text[i]
                if curr.isspace() or curr in ('"', "'", "="):
                    break
                # If encountering a slash, break if preceded by non-slash
                if curr == "/" and word_chars:
                    break
                word_chars.append(curr)
                i += 1

            word_str = "".join(word_chars)
            if len(word_str) > self.max_token_length:
                msg = f"Token '{word_str[:20]}...' exceeds max length of {self.max_token_length}."
                raise AtlasCommandLexerError(
                    error_code=AtlasCommandErrorCode.TOKEN_TOO_LONG,
                    message=msg,
                    raw_token=word_str,
                    position=word_pos,
                )

            tokens.append(
                Token(
                    type=TokenType.WORD,
                    value=word_str,
                    position=word_pos,
                    raw_length=len(word_str),
                )
            )

        # EOF token
        tokens.append(Token(type=TokenType.EOF, value="", position=len(text), raw_length=0))
        return tokens
