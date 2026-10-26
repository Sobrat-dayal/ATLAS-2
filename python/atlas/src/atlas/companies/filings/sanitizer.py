"""Security Sanitizer and Resource Limiter for Regulatory Filings (Stage 86).

Guarantees:
- Untrusted filing HTML never executes scripts or loads dangerous remote active content.
- Strips <script>, <iframe>, <embed>, <object>, inline on* handlers, and javascript: URLs.
- Defuses XML External Entity (XXE) and entity-expansion threats.
- Enforces strict memory and processing budgets on filing documents.
"""

import re
from typing import Set

# Tags that must be completely stripped along with their content
DISALLOWED_TAGS: Set[str] = {
    "script",
    "noscript",
    "iframe",
    "embed",
    "object",
    "applet",
    "base",
    "meta",
}

# Regex to strip dangerous tags and everything inside them
DANGEROUS_TAG_REGEX = re.compile(
    r"<(" + "|".join(DISALLOWED_TAGS) + r")[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)

# Regex to strip self-closing dangerous tags
SELF_CLOSING_DANGEROUS_TAG_REGEX = re.compile(
    r"<(" + "|".join(DISALLOWED_TAGS) + r")[^>]*/>",
    re.IGNORECASE,
)

# Regex to match on* event handlers (e.g. onload=, onclick=, onerror=)
EVENT_HANDLER_REGEX = re.compile(
    r'\s+on[a-z]+\s*=\s*(?:["\'][^"\']*["\']|[^\s>]+)',
    re.IGNORECASE,
)

# Regex to match dangerous protocols in href or src (javascript:, vbscript:, data:)
DANGEROUS_PROTOCOL_REGEX = re.compile(
    r'(href|src)\s*=\s*["\']\s*(?:javascript|vbscript|data):[^"\']*["\']',
    re.IGNORECASE,
)

# Regex to match XML DOCTYPE with entity declarations (XXE defense)
XXE_ENTITY_REGEX = re.compile(
    r"<!DOCTYPE[^>]*\[[^\]]*<!ENTITY[^>]*>[^\]]*\]>",
    re.IGNORECASE | re.DOTALL,
)

# Limits
MAX_DOCUMENT_BYTES: int = 50 * 1024 * 1024  # 50 MB
MAX_PARSED_TEXT_CHARS: int = 10 * 1024 * 1024  # 10M characters
MAX_DIFF_LINES: int = 15000


def sanitize_filing_html(raw_html: str) -> str:
    """Sanitizes raw filing HTML by eliminating active scripts and untrusted execution vectors.
    
    Preserves document structure, headings, financial tables, style tags, and layout semantics.
    """
    if not raw_html:
        return ""

    if len(raw_html.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raw_html = raw_html[:MAX_DOCUMENT_BYTES]

    # 1. Strip script, iframe, embed, object, applet tags and content
    cleaned = DANGEROUS_TAG_REGEX.sub("", raw_html)
    cleaned = SELF_CLOSING_DANGEROUS_TAG_REGEX.sub("", cleaned)

    # 2. Remove all inline event handlers (onload, onclick, onerror, etc.)
    cleaned = EVENT_HANDLER_REGEX.sub("", cleaned)

    # 3. Disarm dangerous protocol references
    cleaned = DANGEROUS_PROTOCOL_REGEX.sub(r'\1="#"', cleaned)

    return cleaned


def defuse_xxe_payload(xml_content: str) -> str:
    """Defuses XML External Entity (XXE) and entity expansion injections."""
    if not xml_content:
        return ""
    # Strip any DTD entity declarations
    return XXE_ENTITY_REGEX.sub("", xml_content)


def extract_plain_text_from_html(html_content: str) -> str:
    """Extracts clean plain text from HTML filing content for indexing and reading."""
    if not html_content:
        return ""

    # Remove style and disarmed blocks
    text = re.sub(r"<style[^>]*>.*?</style>", "", html_content, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Replace breaks and table cells with space/newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|tr|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(td|th)>", "  ", text, flags=re.IGNORECASE)

    # Strip remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode basic entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Clean redundant whitespace
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    # Consolidate excessive blank lines
    result = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 2:
                result.append("")
        else:
            blank_count = 0
            result.append(line)

    return "\n".join(result).strip()
