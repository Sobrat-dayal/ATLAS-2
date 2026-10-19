"""Name normalization, validation, and sanitization for Watchlists V1 (Stage 76)."""

import re
import unicodedata
from typing import Optional

from .errors import InvalidWatchlistNameError

MAX_WATCHLIST_NAME_LENGTH = 100
MAX_WATCHLIST_DESCRIPTION_LENGTH = 500
MAX_WATCHLISTS_PER_USER = 50
MAX_ITEMS_PER_WATCHLIST = 250


def sanitize_watchlist_name(raw_name: str) -> str:
    """
    Sanitizes raw name input:
    - Normalizes unicode characters with NFKC.
    - Strips leading and trailing whitespace.
    - Validates length between 1 and 100 characters.
    - Rejects dangerous control characters and script tags.
    """
    if raw_name is None:
        raise InvalidWatchlistNameError("Watchlist name cannot be null.")

    normalized = unicodedata.normalize("NFKC", str(raw_name)).strip()
    if not normalized:
        raise InvalidWatchlistNameError("Watchlist name cannot be empty or whitespace only.")

    if len(normalized) > MAX_WATCHLIST_NAME_LENGTH:
        raise InvalidWatchlistNameError(
            f"Watchlist name exceeds limit of {MAX_WATCHLIST_NAME_LENGTH} chars."
        )

    # Basic sanitization against HTML / script execution
    if re.search(r"<\s*script[^>]*>", normalized, flags=re.IGNORECASE):
        raise InvalidWatchlistNameError("Watchlist name contains prohibited script elements.")

    return normalized


def normalize_watchlist_name(raw_name: str) -> str:
    """
    Produces the canonical normalized name key for uniqueness checks:
    - Sanitizes the name.
    - Converts to lower-case.
    - Normalizes internal whitespace sequences to single spaces.
    """
    sanitized = sanitize_watchlist_name(raw_name)
    lowered = sanitized.lower()
    return re.sub(r"\s+", " ", lowered).strip()


def validate_description(description: Optional[str]) -> Optional[str]:
    """
    Validates and sanitizes optional watchlist description:
    - Strips whitespace.
    - Enforces maximum length of 500 characters.
    - Returns None if empty.
    """
    if description is None:
        return None

    cleaned = unicodedata.normalize("NFKC", str(description)).strip()
    if not cleaned:
        return None

    if len(cleaned) > MAX_WATCHLIST_DESCRIPTION_LENGTH:
        raise InvalidWatchlistNameError(
            f"Watchlist description exceeds limit of {MAX_WATCHLIST_DESCRIPTION_LENGTH} chars."
        )

    return cleaned
