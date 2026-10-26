"""Canonical URL, Text, and Timestamp Normalization & Security Guard (Stage 99).

Provides:
- URL canonicalization with tracking parameter stripping
- SSRF prevention & external URL validation
- HTML markup sanitization and XSS prevention
- Timestamp normalization to UTC
"""

from __future__ import annotations

import html
import ipaddress
import re
from datetime import date, datetime, timezone
from typing import Optional, Set
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Query parameters commonly used for tracking, analytics, and session affiliation
_TRACKING_QUERY_PARAMS: Set[str] = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_cid",
    "utm_reader",
    "fbclid",
    "gclid",
    "gclsrc",
    "dclid",
    "msclkid",
    "ref",
    "source",
    "campaign",
    "_hsenc",
    "_hsmi",
    "mc_cid",
    "mc_eid",
    "igshid",
    "ncid",
    "cmpid",
}

# Regex to strip script and style tags along with their inner code
_SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
# Regex to strip remaining HTML tags
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Whitespace collapse regex
_WHITESPACE_RE = re.compile(r"\s+")
# Dangerous URI schemes
_DANGEROUS_SCHEMES: Set[str] = {"javascript", "data", "file", "vbscript", "about"}


def normalize_canonical_url(raw_url: str) -> str:
    """
    Normalizes a news article URL into a stable canonical URL for identity
    and deduplication. Strips analytics query parameters and fragments.
    """
    if not raw_url or not raw_url.strip():
        return ""

    raw_url = raw_url.strip()
    parsed = urlparse(raw_url)

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        scheme = "https"

    netloc = parsed.netloc.lower()
    # Strip default ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Normalize path
    path = parsed.path
    if not path:
        path = "/"
    elif path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Filter out tracking parameters
    query_params = []
    if parsed.query:
        for k, v in parse_qsl(parsed.query, keep_blank_values=True):
            if k.lower() not in _TRACKING_QUERY_PARAMS:
                query_params.append((k, v))

    # Sort query parameters for deterministic canonical identity
    query_params.sort(key=lambda item: item[0])
    query_str = urlencode(query_params)

    # Omit fragment
    canonical = urlunparse((scheme, netloc, path, parsed.params, query_str, ""))
    return canonical


def validate_external_url(raw_url: str) -> tuple[bool, Optional[str]]:
    """
    Validates an external URL for SSRF security before storage or redirection.
    Rejects:
    - Dangerous schemes (javascript, file, data, etc.)
    - Private IP addresses, loopbacks, link-local, AWS metadata endpoints
    - Embedded credentials
    """
    if not raw_url or not raw_url.strip():
        return False, "URL is empty"

    raw_url = raw_url.strip()
    parsed = urlparse(raw_url)

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported or dangerous URL scheme: '{parsed.scheme}'"

    if parsed.username or parsed.password:
        return False, "URLs with embedded credentials are not permitted"

    hostname = parsed.hostname
    if not hostname:
        return False, "URL missing valid hostname"

    hostname_lower = hostname.lower()

    # Reject localhost or internal names
    if hostname_lower in ("localhost", "local", "internal", "corp", "localdomain"):
        return False, "Internal and loopback hosts are not permitted"

    # Check for IP address literals
    try:
        ip = ipaddress.ip_address(hostname)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False, f"Private or loopback IP destination rejected: {ip}"
        # Block cloud metadata addresses (e.g. 169.254.169.254)
        if str(ip) == "169.254.169.254":
            return False, "Cloud metadata endpoint is strictly prohibited"
    except ValueError:
        # Hostname is a domain name, not an IP literal
        pass

    return True, None


def sanitize_plain_text(raw_text: Optional[str], max_length: int = 500) -> str:
    """
    Strips all HTML tags, script markup, and entities to produce clean, safe
    plain text suitable for headlines and excerpts without XSS risks.
    """
    if not raw_text:
        return ""

    # Strip script and style blocks completely including inner text
    text = _SCRIPT_STYLE_RE.sub(" ", raw_text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Strip block-level HTML tags with space
    text = re.sub(r"<(div|p|br|h[1-6]|li|blockquote|tr|td)[^>]*>", " ", text, flags=re.I)
    text = re.sub(r"</(div|p|h[1-6]|li|blockquote|tr|td)>", " ", text, flags=re.I)
    # Strip inline and remaining HTML tags without adding spaces
    text = _HTML_TAG_RE.sub("", text)
    # Re-unescape residual entities
    text = html.unescape(text)
    # Strip dangerous protocols if present in text
    for scheme in _DANGEROUS_SCHEMES:
        text = re.sub(rf"(?i){scheme}:", "", text)
    # Collapse multiple spaces and linebreaks
    text = _WHITESPACE_RE.sub(" ", text).strip()

    if len(text) > max_length:
        text = text[:max_length].rstrip() + "..."

    return text


def normalize_timestamp(val: datetime | date | str | int | float | None) -> datetime:
    """
    Normalizes diverse timestamp representations into a timezone-aware UTC datetime.
    Ensures that publication and ingestion timestamps preserve true instants.
    """
    if val is None:
        return datetime.now(timezone.utc)

    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    if isinstance(val, date):
        return datetime(val.year, val.month, val.day, 0, 0, 0, tzinfo=timezone.utc)

    if isinstance(val, (int, float)):
        # Epoch timestamp in seconds or milliseconds
        if val > 1e11:  # Milliseconds
            val = val / 1000.0
        return datetime.fromtimestamp(val, tz=timezone.utc)

    if isinstance(val, str):
        val = val.strip()
        # ISO string handling
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass

        # Try date-only format YYYY-MM-DD
        try:
            d = datetime.strptime(val, "%Y-%m-%d").date()
            return datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=timezone.utc)
        except ValueError:
            pass

    return datetime.now(timezone.utc)
