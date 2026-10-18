"""Saved Chart Layouts Module (Stage 74).

Provides persistent multi-chart workspace documents backed by PostgreSQL JSONB.
"""

from .migrations import UnsupportedSchemaVersionError, migrate_layout_document
from .models import ChartLayoutModel
from .normalization import InvalidLayoutNameError, normalize_layout_name, sanitize_display_name
from .repository import ChartLayoutRepository
from .schemas import (
    ChartLayoutCreateRequest,
    ChartLayoutDetailResponse,
    ChartLayoutDuplicateRequest,
    ChartLayoutExportEnvelope,
    ChartLayoutListResponse,
    ChartLayoutMetadataPatchRequest,
    ChartLayoutSummaryResponse,
    ChartLayoutUpdateRequest,
    SavedChartLayoutDocumentV1,
    SavedChartPanelV1,
    SavedDrawingAnchorV1,
    SavedDrawingObjectV1,
    SavedIndicatorInstanceV1,
    SavedPriceScaleSettingsV1,
    SavedSyncGroupV1,
    SavedViewportV1,
)
from .service import (
    ChartLayoutService,
    LayoutNameConflictError,
    LayoutNotFoundError,
    LayoutRevisionConflictError,
)
from .validation import (
    ForbiddenFieldDetectedError,
    JsonNestingDepthExceededError,
    LayoutPayloadTooLargeError,
    LayoutQuotaExceededError,
    validate_document_size,
    validate_json_depth,
    validate_layout_document_payload,
)

__all__ = [
    "ChartLayoutModel",
    "ChartLayoutRepository",
    "ChartLayoutService",
    "ChartLayoutCreateRequest",
    "ChartLayoutUpdateRequest",
    "ChartLayoutMetadataPatchRequest",
    "ChartLayoutDuplicateRequest",
    "ChartLayoutSummaryResponse",
    "ChartLayoutDetailResponse",
    "ChartLayoutListResponse",
    "ChartLayoutExportEnvelope",
    "SavedChartLayoutDocumentV1",
    "SavedChartPanelV1",
    "SavedIndicatorInstanceV1",
    "SavedDrawingAnchorV1",
    "SavedDrawingObjectV1",
    "SavedPriceScaleSettingsV1",
    "SavedSyncGroupV1",
    "SavedViewportV1",
    "LayoutNotFoundError",
    "LayoutNameConflictError",
    "LayoutRevisionConflictError",
    "LayoutQuotaExceededError",
    "LayoutPayloadTooLargeError",
    "ForbiddenFieldDetectedError",
    "JsonNestingDepthExceededError",
    "InvalidLayoutNameError",
    "UnsupportedSchemaVersionError",
    "normalize_layout_name",
    "sanitize_display_name",
    "validate_layout_document_payload",
    "validate_document_size",
    "validate_json_depth",
    "migrate_layout_document",
]
