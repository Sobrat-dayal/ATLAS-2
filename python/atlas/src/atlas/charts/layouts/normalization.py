"""Layout Name Normalization and Validation utilities (Stage 74).

Enforces:
- Non-empty trimmed names
- Maximum 100 character length
- Unicode-safe NFKC normalization
- Lowercase normalized representation for case-insensitive uniqueness per user
- Safe display sanitization (strips script injection / control characters)
"""

import re
import unicodedata

MAX_NAME_LENGTH = 100
MIN_NAME_LENGTH = 1


class InvalidLayoutNameError(ValueError):
    """Raised when a layout name fails normalization or validation rules."""

    pass


def normalize_layout_name(name: str) -> str:
    """
    Normalizes a user-supplied layout name for storage and unique indexing.

    1. Checks type
    2. Strips surrounding whitespace
    3. Normalizes via Unicode NFKC
    4. Rejects control characters
    5. Validates bounded length (1 to 100 characters)
    6. Returns lowercase canonical form for case-insensitive uniqueness check
    """
    if not isinstance(name, str):
        raise InvalidLayoutNameError("Layout name must be a string.")

    cleaned = unicodedata.normalize("NFKC", name.strip())

    # Reject control characters (ASCII 0-31 and 127)
    if any(ord(char) < 32 or ord(char) == 127 for char in cleaned):
        raise InvalidLayoutNameError("Layout name contains invalid control characters.")

    # Strip script blocks completely and any HTML tags
    cleaned = re.sub(r"(?is)<script.*?>.*?</script>", "", cleaned)
    cleaned = re.sub(r"<[^>]*>", "", cleaned).strip()

    if len(cleaned) < MIN_NAME_LENGTH:
        raise InvalidLayoutNameError("Layout name cannot be empty.")

    if len(cleaned) > MAX_NAME_LENGTH:
        raise InvalidLayoutNameError(
            f"Layout name exceeds maximum length of {MAX_NAME_LENGTH} characters."
        )

    return cleaned.lower()


def sanitize_display_name(name: str) -> str:
    """
    Sanitizes a layout name for safe user display without converting to lowercase.
    """
    if not isinstance(name, str):
        raise InvalidLayoutNameError("Layout name must be a string.")

    cleaned = unicodedata.normalize("NFKC", name.strip())
    cleaned = re.sub(r"(?is)<script.*?>.*?</script>", "", cleaned)
    cleaned = re.sub(r"<[^>]*>", "", cleaned).strip()

    if len(cleaned) < MIN_NAME_LENGTH:
        raise InvalidLayoutNameError("Layout name cannot be empty.")

    if len(cleaned) > MAX_NAME_LENGTH:
        raise InvalidLayoutNameError(
            f"Layout name exceeds maximum length of {MAX_NAME_LENGTH} characters."
        )

    return cleaned
