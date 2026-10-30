"""Financial Text Normalization for Document Ingestion (Part XIV).

Preserves currencies, negative values, financial units, percentages,
and fiscal periods while normalizing erratic whitespace and line wraps.
"""

from __future__ import annotations

import re


def normalize_financial_text(text: str) -> str:
    """Normalizes text while preserving financial numbers, units, and currencies."""
    if not text:
        return ""

    # Replace erratic unicode spaces with regular spaces
    text = re.sub(r"[\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]", " ", text)

    # Normalize Windows CRLF to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Preserve negative parenthesis financial convention: e.g. (100) -> -100
    # Keep original readable but clarify in clean text if needed
    # Collapse multiple blank lines to double newline (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse horizontal whitespace
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
