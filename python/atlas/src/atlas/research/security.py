"""Security, Sanitization, and URL Validation for Financial Research (Stage 104)."""

import ipaddress
import re
import urllib.parse
from typing import Optional

from atlas.research.errors import ResearchNoteContentInvalidError, ResearchSourceUrlUnsafeError

# Maximum lengths for analyst content
MAX_NOTE_BODY_LENGTH = 500_000
MAX_NOTE_TITLE_LENGTH = 500
MAX_INVESTIGATION_TITLE_LENGTH = 500
MAX_INVESTIGATION_DESC_LENGTH = 50_000
MAX_QUESTION_TEXT_LENGTH = 2_000
MAX_HYPOTHESIS_STATEMENT_LENGTH = 5_000
MAX_CLAIM_STATEMENT_LENGTH = 5_000
MAX_EXCERPT_LENGTH = 5_000

# Forbidden internal IP ranges and hostname keywords
BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "169.254.169.254",  # AWS/GCP instance metadata endpoint
    "metadata.google.internal",
}

# Dangerous HTML / script injection patterns
DANGEROUS_HTML_PATTERNS = [
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*object[^>]*>.*?<\s*/\s*object\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"<\s*embed[^>]*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"vbscript\s*:", re.IGNORECASE),
    re.compile(r"data\s*:\s*text/html", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # onload=, onerror=, onclick=
]


def validate_and_sanitize_url(url: str) -> str:
    """Validate external source URLs to prevent SSRF and dangerous schemes.

    Args:
        url: The user-supplied or external document URL.

    Returns:
        The sanitized URL.

    Raises:
        ResearchSourceUrlUnsafeError: If the URL is unsafe, malformed, or accesses private networks.
    """
    if not url or not isinstance(url, str):
        raise ResearchSourceUrlUnsafeError("Source URL cannot be empty.")

    clean_url = url.strip()
    parsed = urllib.parse.urlparse(clean_url)

    # 1. Enforce allowed schemes: http, https only
    if parsed.scheme.lower() not in ("http", "https"):
        raise ResearchSourceUrlUnsafeError(
            f"Invalid URL scheme '{parsed.scheme}'. Only http and https are permitted."
        )

    # 2. Must contain valid hostname
    hostname = parsed.hostname
    if not hostname:
        raise ResearchSourceUrlUnsafeError("Source URL must contain a valid domain hostname.")

    hostname_lower = hostname.lower()

    # 3. Block localhost and cloud metadata endpoints
    if hostname_lower in BLOCKED_HOSTS or hostname_lower.endswith(".internal"):
        raise ResearchSourceUrlUnsafeError(
            f"Access to private/internal network destination '{hostname}' is prohibited."
        )

    # 4. Check for private/loopback/link-local IP addresses
    try:
        ip = ipaddress.ip_address(hostname_lower)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ResearchSourceUrlUnsafeError(
                f"Access to non-public IP address '{hostname}' is strictly prohibited."
            )
    except ValueError:
        # Not a raw IP literal; hostname is domain name
        pass

    return clean_url


def sanitize_markdown_text(text: str, max_length: int = MAX_NOTE_BODY_LENGTH) -> str:
    """Sanitize analyst-authored rich text or markdown to prevent script injection.

    Args:
        text: Raw user input text or markdown.
        max_length: Maximum allowed character length.

    Returns:
        Sanitized plain/markdown string.

    Raises:
        ResearchNoteContentInvalidError: If text exceeds length limits.
    """
    if not text:
        return ""

    if len(text) > max_length:
        raise ResearchNoteContentInvalidError(
            f"Content length ({len(text)} characters) exceeds maximum allowable limit of {max_length} characters."
        )

    sanitized = text
    for pattern in DANGEROUS_HTML_PATTERNS:
        sanitized = pattern.sub("", sanitized)

    return sanitized


def validate_analyst_text(
    field_name: str,
    text: Optional[str],
    max_length: int,
    required: bool = True,
) -> str:
    """Validate and sanitize a short text field (title, question, statement).

    Args:
        field_name: Name of the field for descriptive errors.
        text: Text to validate.
        max_length: Maximum length.
        required: Whether empty/blank is disallowed.

    Returns:
        Sanitized string.
    """
    if not text or not text.strip():
        if required:
            raise ResearchNoteContentInvalidError(f"Field '{field_name}' cannot be empty.")
        return ""

    clean = text.strip()
    if len(clean) > max_length:
        raise ResearchNoteContentInvalidError(
            f"Field '{field_name}' length ({len(clean)}) exceeds maximum of {max_length} characters."
        )

    for pattern in DANGEROUS_HTML_PATTERNS:
        clean = pattern.sub("", clean)

    return clean
