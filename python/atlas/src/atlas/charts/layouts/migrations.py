"""Layout Document Schema Migrations (Stage 74).

Manages forward-compatible migration and upgrade pipelines for layout documents.
- Schema Version 1 is the canonical initial baseline for Stage 74.
- Unsupported future versions (> 1) are explicitly rejected to prevent data corruption.
"""

from typing import Any, Dict

from .schemas import SavedChartLayoutDocumentV1
from .validation import validate_layout_document_payload

SUPPORTED_SCHEMA_VERSIONS = {1}
CURRENT_SCHEMA_VERSION = 1


class UnsupportedSchemaVersionError(ValueError):
    """Raised when a document schema version is not supported by this ATLAS version."""

    pass


def migrate_layout_document(raw_doc: Dict[str, Any]) -> SavedChartLayoutDocumentV1:
    """
    Migrates a raw layout document into the canonical active in-memory schema (V1).

    If the document has an unknown or higher schema version than CURRENT_SCHEMA_VERSION,
    raises UnsupportedSchemaVersionError.
    """
    if not isinstance(raw_doc, dict):
        raise ValueError("Layout document must be a JSON dictionary.")

    version = raw_doc.get("schema_version", 1)

    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise UnsupportedSchemaVersionError(
            f"Unsupported document schema version '{version}'. "
            f"This ATLAS build supports schema versions: {sorted(SUPPORTED_SCHEMA_VERSIONS)}. "
            f"Please upgrade ATLAS to open layouts from newer versions."
        )

    # For V1, perform full security, size and structural validation
    return validate_layout_document_payload(raw_doc)
