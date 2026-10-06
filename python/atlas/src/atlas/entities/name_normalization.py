import re
import unicodedata


def normalize_entity_name(name: str) -> str:
    """
    Normalizes a human-facing entity name or alias for deterministic matching.

    Rules:
    1. Unicode NFKC normalization
    2. Casefold
    3. Collapse repeated internal whitespace
    4. Trim outer whitespace
    5. Preserves punctuation

    Raises:
        ValueError: If the normalized name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")

    # 1. NFKC normalization
    normalized = unicodedata.normalize("NFKC", name)

    # 2. Casefold
    normalized = normalized.casefold()

    # 3 & 4. Collapse whitespace and trim
    normalized = re.sub(r"\s+", " ", normalized).strip()

    if not normalized:
        raise ValueError("Name cannot be empty after normalization")

    return normalized
