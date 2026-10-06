import re
from typing import Optional
from urllib.parse import urlparse

from .errors import (
    InvalidProvenanceHashError,
    InvalidProvenanceSourceKeyError,
    InvalidProvenanceURLError,
)

SOURCE_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def validate_source_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    key = key.lower()
    if not SOURCE_KEY_PATTERN.match(key):
        raise InvalidProvenanceSourceKeyError(f"Invalid source key format: {key}")
    return key


def validate_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise InvalidProvenanceURLError(f"Invalid URL scheme, expected http/https: {url}")

    if parsed.username or parsed.password:
        raise InvalidProvenanceURLError("URL must not contain credentials")

    return url


def validate_content_hash(hash_str: Optional[str]) -> Optional[str]:
    if not hash_str:
        return None

    hash_str = hash_str.lower()
    if not HASH_PATTERN.match(hash_str):
        raise InvalidProvenanceHashError("Invalid content hash format, expected 64 hex characters.")
    return hash_str
