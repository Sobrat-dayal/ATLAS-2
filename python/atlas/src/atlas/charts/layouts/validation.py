"""Layout Document and Resource Bounds Validation (Stage 74).

Validates:
- Maximum document payload size (512 KiB)
- Maximum JSON nesting depth
- Explicit forbidden field rejection (credentials, tokens, OHLCV data, calculated outputs)
- Per-user quota limits (max 50 saved layouts)
"""

import json
from typing import Any, Dict

from .schemas import (
    FORBIDDEN_KEYWORDS,
    MAX_DOCUMENT_BYTES,
    SavedChartLayoutDocumentV1,
)

MAX_LAYOUTS_PER_USER = 50
MAX_JSON_DEPTH = 10


class LayoutPayloadTooLargeError(ValueError):
    """Raised when serialized layout document exceeds size budget."""

    pass


class LayoutQuotaExceededError(ValueError):
    """Raised when user exceeds maximum saved layout quota."""

    pass


class ForbiddenFieldDetectedError(ValueError):
    """Raised when layout document contains unauthorized or sensitive fields."""

    pass


class JsonNestingDepthExceededError(ValueError):
    """Raised when layout JSON depth exceeds safe bounds."""

    pass


def validate_json_depth(obj: Any, current_depth: int = 1) -> None:
    """Recursively checks that JSON structure does not exceed MAX_JSON_DEPTH."""
    if current_depth > MAX_JSON_DEPTH:
        raise JsonNestingDepthExceededError(
            f"Layout document exceeds maximum allowed nesting depth of {MAX_JSON_DEPTH}."
        )

    if isinstance(obj, dict):
        for val in obj.values():
            validate_json_depth(val, current_depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            validate_json_depth(item, current_depth + 1)


def scan_for_forbidden_fields(obj: Any) -> None:
    """
    Scans dictionaries recursively to prevent storage of credentials,
    authentication tokens, raw OHLCV arrays or calculated indicator arrays.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            for forbidden in FORBIDDEN_KEYWORDS:
                if forbidden in key_lower:
                    raise ForbiddenFieldDetectedError(
                        f"Forbidden field or keyword '{key}' detected in layout document. "
                        "Saved layouts must not store credentials, raw market data, "
                        "or calculated indicator caches."
                    )
            scan_for_forbidden_fields(value)
    elif isinstance(obj, list):
        for item in obj:
            scan_for_forbidden_fields(item)


def validate_document_size(document_dict: Dict[str, Any]) -> None:
    """Checks that serialized JSON payload does not exceed 512 KiB."""
    serialized = json.dumps(document_dict, separators=(",", ":"))
    size_bytes = len(serialized.encode("utf-8"))
    if size_bytes > MAX_DOCUMENT_BYTES:
        raise LayoutPayloadTooLargeError(
            f"Layout document size ({size_bytes} bytes) exceeds maximum "
            f"permitted limit of {MAX_DOCUMENT_BYTES} bytes."
        )


def validate_layout_document_payload(document_dict: Dict[str, Any]) -> SavedChartLayoutDocumentV1:
    """
    Complete security and boundary verification pipeline for untrusted layout documents.
    """
    # 1. Payload size check
    validate_document_size(document_dict)

    # 2. JSON nesting depth check
    validate_json_depth(document_dict)

    # 3. Forbidden field check
    scan_for_forbidden_fields(document_dict)

    # 4. Strict Pydantic model validation
    return SavedChartLayoutDocumentV1.model_validate(document_dict)
