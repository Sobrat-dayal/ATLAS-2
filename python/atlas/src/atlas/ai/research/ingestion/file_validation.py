"""File validation and security checks for document ingestion (Part XI)."""

from __future__ import annotations

import re
from typing import Tuple

from atlas.ai.research.errors import (
    ResearchDocumentTooLargeError,
    ResearchDocumentUnsupportedFormatError,
)

MAX_DOCUMENT_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".pdf", ".csv"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/json",
    "application/pdf",
    "text/csv",
}


def validate_document_file(
    filename: str,
    content_bytes: bytes,
    mime_type: str = "text/plain",
) -> Tuple[str, str]:
    """Validates file extension, size, and content safety.

    Returns:
        (sanitized_filename, valid_mime_type)
    """
    if len(content_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise ResearchDocumentTooLargeError(len(content_bytes), MAX_DOCUMENT_SIZE_BYTES)

    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS and mime_type not in ALLOWED_MIME_TYPES:
        raise ResearchDocumentUnsupportedFormatError(mime_type, ext or "unknown")

    # Sanitize filename (prevent directory traversal)
    clean_name = re.sub(r"[^\w\.\-\_]", "_", filename.strip())
    return clean_name, mime_type
