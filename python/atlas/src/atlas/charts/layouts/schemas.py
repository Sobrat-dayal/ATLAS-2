"""Pydantic schemas and serialization contracts for Saved Chart Layouts (Stage 74).

Enforces:
- Strict canonical layout document schema V1
- Resource bounds (panels, indicators, drawings, sync groups)
- Rejection of forbidden fields (credentials, raw OHLCV, quotes, calculated arrays, browser objects)
- REST request/response contracts for layout CRUD, concurrency and export/import envelopes
"""

import datetime
import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Supported layout preset identifiers (from Stage 72)
VALID_LAYOUT_IDS = {
    "single",
    "two-columns",
    "two-rows",
    "three-left-focus",
    "three-top-focus",
    "four-grid",
}

# Supported chart types (from Stage 68)
VALID_CHART_TYPES = {
    "candlestick",
    "bar",
    "ohlc",
    "line",
    "area",
}

# Max resource limits per layout
MAX_PANELS_PER_LAYOUT = 4
MAX_INDICATORS_PER_PANEL = 12
MAX_DRAWINGS_PER_PANEL = 250
MAX_SYNC_GROUPS_PER_LAYOUT = 4
MAX_LAYOUT_NAME_LENGTH = 100
MAX_DOCUMENT_BYTES = 512 * 1024  # 512 KiB

FORBIDDEN_KEYWORDS = {
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "credentials",
    "access_token",
    "refresh_token",
    "session_id",
    "bars_array",
    "ohlcv_data",
    "calculated_series",
    "indicator_cache",
}


# ---------------------------------------------------------------------------
# 1. Document V1 Sub-Schemas
# ---------------------------------------------------------------------------


class SavedViewportV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    visible_start: Optional[str] = None
    visible_end: Optional[str] = None
    following_latest: bool = True


class SavedPriceScaleSettingsV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = "normal"
    invert: bool = False
    logarithmic: bool = False


class SavedIndicatorInstanceV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instance_id: str = Field(..., min_length=1, max_length=64)
    indicator_id: str = Field(..., min_length=1, max_length=64)
    version: int = Field(default=1, ge=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
    color: Optional[str] = Field(default=None, max_length=32)
    line_width: Optional[int] = Field(default=None, ge=1, le=8)


class SavedDrawingAnchorV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    time: Union[int, str]
    price: float


class SavedDrawingObjectV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64)
    type: str = Field(..., min_length=1, max_length=64)
    version: int = Field(default=1, ge=1)
    anchors: List[SavedDrawingAnchorV1] = Field(default_factory=list, max_length=10)
    style: Dict[str, Any] = Field(default_factory=dict)
    visible: bool = True
    locked: bool = False
    z_index: int = Field(default=1, ge=1, le=1000)


class SavedChartPanelV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    panel_id: str = Field(..., min_length=1, max_length=32)
    instrument_entity_id: Optional[str] = Field(default=None, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=32)
    asset_class: Optional[str] = Field(default=None, max_length=32)
    interval: str = Field(default="1d", min_length=1, max_length=16)
    chart_type: str = Field(default="candlestick", min_length=1, max_length=32)
    viewport: Optional[SavedViewportV1] = None
    price_scale_settings: Optional[SavedPriceScaleSettingsV1] = None
    indicators: List[SavedIndicatorInstanceV1] = Field(
        default_factory=list, max_length=MAX_INDICATORS_PER_PANEL
    )
    drawings: List[SavedDrawingObjectV1] = Field(
        default_factory=list, max_length=MAX_DRAWINGS_PER_PANEL
    )

    @field_validator("chart_type")
    @classmethod
    def validate_chart_type(cls, v: str) -> str:
        if v.lower() not in VALID_CHART_TYPES:
            raise ValueError(
                f"Unsupported chart_type '{v}'. Must be one of {sorted(VALID_CHART_TYPES)}"
            )
        return v.lower()


class SavedSyncGroupV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=64)
    member_panel_ids: List[str] = Field(default_factory=list, max_length=MAX_PANELS_PER_LAYOUT)
    settings: Dict[str, bool] = Field(default_factory=dict)
    enabled: bool = False
    color: str = Field(default="#06b6d4", max_length=32)


# ---------------------------------------------------------------------------
# 2. Canonical Layout Document V1 Aggregate
# ---------------------------------------------------------------------------


class SavedChartLayoutDocumentV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    layout_id: str = Field(..., min_length=1, max_length=32)
    panel_order: List[str] = Field(..., min_length=1, max_length=MAX_PANELS_PER_LAYOUT)
    split_ratios: Dict[str, float] = Field(default_factory=dict)
    active_panel_id: str = Field(..., min_length=1, max_length=32)
    panels: List[SavedChartPanelV1] = Field(..., min_length=1, max_length=MAX_PANELS_PER_LAYOUT)
    synchronization_groups: List[SavedSyncGroupV1] = Field(
        default_factory=list, max_length=MAX_SYNC_GROUPS_PER_LAYOUT
    )

    @field_validator("layout_id")
    @classmethod
    def validate_layout_id(cls, v: str) -> str:
        if v not in VALID_LAYOUT_IDS:
            raise ValueError(f"Invalid layout_id '{v}'. Must be one of {sorted(VALID_LAYOUT_IDS)}")
        return v

    @field_validator("split_ratios")
    @classmethod
    def validate_split_ratios(cls, ratios: Dict[str, float]) -> Dict[str, float]:
        for k, val in ratios.items():
            if val is None or not (0.05 <= val <= 0.95):
                raise ValueError(
                    f"Split ratio for '{k}' must be between 0.05 and 0.95, got {val}"
                )
        return ratios

    @model_validator(mode="after")
    def validate_panel_consistency(self) -> "SavedChartLayoutDocumentV1":
        panel_map = {p.panel_id: p for p in self.panels}
        if len(panel_map) != len(self.panels):
            raise ValueError("Duplicate panel_id detected in layout document panels list.")

        # Ensure panel_order entries exist in panels
        for pid in self.panel_order:
            if pid not in panel_map:
                raise ValueError(f"Panel '{pid}' in panel_order does not exist in panels list.")

        # Ensure active_panel_id is in panel_order
        if self.active_panel_id not in self.panel_order:
            raise ValueError(
                f"active_panel_id '{self.active_panel_id}' must belong to panel_order."
            )

        # Ensure sync group members exist in panel_order
        for g in self.synchronization_groups:
            for member_id in g.member_panel_ids:
                if member_id not in panel_map:
                    raise ValueError(
                        f"Sync group '{g.group_id}' references unknown panel '{member_id}'"
                    )

        return self


# ---------------------------------------------------------------------------
# 3. API Request / Response DTOs
# ---------------------------------------------------------------------------


class ChartLayoutCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=MAX_LAYOUT_NAME_LENGTH)
    description: Optional[str] = Field(default=None, max_length=500)
    document: SavedChartLayoutDocumentV1
    is_default: bool = False


class ChartLayoutUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: SavedChartLayoutDocumentV1
    expected_revision: int = Field(
        ..., ge=1, description="Expected record revision for optimistic concurrency"
    )


class ChartLayoutMetadataPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1, max_length=MAX_LAYOUT_NAME_LENGTH)
    description: Optional[str] = Field(default=None, max_length=500)
    is_default: Optional[bool] = None


class ChartLayoutDuplicateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    new_name: Optional[str] = Field(default=None, min_length=1, max_length=MAX_LAYOUT_NAME_LENGTH)


class ChartLayoutSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    layout_type: str
    chart_count: int
    is_default: bool
    revision: int
    document_schema_version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ChartLayoutDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_user_id: uuid.UUID
    name: str
    normalized_name: str
    description: Optional[str] = None
    layout_type: str
    chart_count: int
    is_default: bool
    revision: int
    document_schema_version: int
    document: SavedChartLayoutDocumentV1
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ChartLayoutListResponse(BaseModel):
    items: List[ChartLayoutSummaryResponse]
    total: int
    page: int
    page_size: int


class ChartLayoutExportEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal["atlas_chart_layout"] = "atlas_chart_layout"
    export_version: Literal[1] = 1
    exported_at: str
    layout_name: str
    document_schema_version: int = 1
    layout_document: SavedChartLayoutDocumentV1
