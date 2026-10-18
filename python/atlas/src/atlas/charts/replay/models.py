"""Pydantic models, DTOs, and schemas for ATLAS Historical Chart Replay V1 (Stage 75).

Defines:
- Ephemeral replay session data contracts
- Strict future-data boundary requests/responses
- Capability discovery models
- Step/Seek command structures
- Replay source metadata snapshots
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..models import ChartBarDTO


class ReplaySessionStatus(str, Enum):
    """Lifecycle status of a historical chart replay session."""

    INITIALIZING = "INITIALIZING"
    READY = "READY"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    END_OF_DATA = "END_OF_DATA"
    ERROR = "ERROR"
    CLOSED = "CLOSED"


class ReplayStepDirection(str, Enum):
    """Direction for single or multi-bar replay progression."""

    FORWARD = "forward"
    BACKWARD = "backward"


class ReplaySourceSnapshot(BaseModel):
    """Immutable snapshot of the historical market data source for a replay session."""

    model_config = ConfigDict(frozen=True)

    instrument_entity_id: UUID = Field(..., description="Canonical instrument entity UUID")
    display_symbol: str = Field(..., description="Primary display symbol (e.g. SPY, BTCUSDT)")
    canonical_market_series_identity: Dict[str, Any] = Field(
        default_factory=dict, description="Market series dimensions (venue, basis, units)"
    )
    interval: str = Field(..., description="Selected canonical interval (e.g. 1d, 1h, 5m)")
    provider: str = Field("canonical_clickhouse", description="Authoritative data provider")
    venue: str = Field("GLOBAL", description="Primary market exchange or venue")
    price_basis: str = Field("CLOSE", description="Price quotation basis")
    adjustment_basis: str = Field("SPLIT_ADJUSTED", description="Corporate action adjustment basis")
    quote_unit: str = Field("USD", description="Currency or quotation asset")
    source_revision_fingerprint: str = Field(
        ..., description="Fingerprint of the authoritative historical dataset revision"
    )


class ReplaySessionDTO(BaseModel):
    """Public transfer object representing an active historical replay session."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID = Field(..., description="Unique replay session UUID")
    owner_user_id: UUID = Field(..., description="Authenticated user identity owning this session")
    target_panel_id: str = Field(..., description="Target Stage 72 panel ID (e.g. panel-1)")
    instrument_entity_id: UUID = Field(..., description="Canonical instrument entity ID")
    display_symbol: str = Field(..., description="Instrument display symbol")
    interval: str = Field(..., description="Active chart interval")
    status: ReplaySessionStatus = Field(..., description="Current playback state")
    cursor_index: int = Field(..., description="Current 0-indexed position of revealed bar")
    start_index: int = Field(..., description="Initial starting bar index of the session")
    cursor_bar: Optional[ChartBarDTO] = Field(
        None, description="The most recently revealed finalized bar at cursor position"
    )
    revealed_bars_count: int = Field(..., description="Total count of revealed bars up to cursor")
    total_bars: int = Field(..., description="Total bars available in the historical series")
    playback_speed: float = Field(1.0, description="Playback speed in bars per second")
    source_snapshot: ReplaySourceSnapshot = Field(
        ..., description="Authoritative historical data snapshot"
    )
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp (TTL)")


class ReplayStartRequest(BaseModel):
    """Client request to initialize a new historical replay session."""

    panel_id: str = Field("panel-1", max_length=50, description="Stage 72 panel identity")
    instrument_id: Optional[str] = Field(None, description="Canonical instrument entity UUID")
    symbol: Optional[str] = Field(None, description="Alternative ticker symbol parameter")
    interval: str = Field("1d", max_length=10, description="Requested canonical interval")
    start_time: Optional[datetime] = Field(
        None, description="Requested starting timestamp for replay playback"
    )
    start_index: Optional[int] = Field(
        None, ge=0, description="Alternative 0-based bar index to start playback"
    )
    history_window: int = Field(
        100, ge=10, le=500, description="Pre-revealed historical context window preceding start bar"
    )
    playback_speed: float = Field(
        1.0, ge=0.1, le=10.0, description="Initial playback speed (bars per second)"
    )


class ReplayStartResponse(BaseModel):
    """Response returned upon successful creation of a replay session."""

    session: ReplaySessionDTO = Field(..., description="Created replay session metadata")
    revealed_bars: List[ChartBarDTO] = Field(
        ..., description="Qualified historical bars revealed up to start bar (NO FUTURE BARS)"
    )


class ReplayStepRequest(BaseModel):
    """Client request to advance or step back the replay cursor."""

    direction: ReplayStepDirection = Field(
        default=ReplayStepDirection.FORWARD, description="Step direction: forward or backward"
    )
    count: int = Field(default=1, ge=1, le=10, description="Number of bars to advance or reverse")
    expected_cursor_index: Optional[int] = Field(
        None, description="Optimistic concurrency verification for client cursor position"
    )


class ReplayStepResponse(BaseModel):
    """Response returned upon advancing or stepping backward."""

    session_id: UUID = Field(..., description="Replay session UUID")
    status: ReplaySessionStatus = Field(..., description="Updated playback status")
    cursor_index: int = Field(..., description="Updated 0-indexed cursor position")
    cursor_bar: Optional[ChartBarDTO] = Field(
        None, description="The newly revealed or active cursor bar"
    )
    direction: str = Field(..., description="Executed step direction")
    revealed_bar: Optional[ChartBarDTO] = Field(
        None, description="The newly revealed bar when stepping forward (NULL on backward)"
    )
    removed_bar_index: Optional[int] = Field(
        None, description="The index of the bar removed from visibility when stepping backward"
    )
    is_end_of_data: bool = Field(..., description="True if cursor reached latest available bar")
    is_start_of_data: bool = Field(..., description="True if cursor reached earliest available bar")
    revealed_bars_count: int = Field(..., description="Total count of currently revealed bars")
    total_bars: int = Field(..., description="Total bars available in historical series")


class ReplaySeekRequest(BaseModel):
    """Client request to relocate the replay cursor to a target historical position."""

    target_index: Optional[int] = Field(None, ge=0, description="Target 0-based bar index")
    target_time: Optional[datetime] = Field(None, description="Target timestamp coordinate")


class ReplaySeekResponse(BaseModel):
    """Response returned upon seeking to a new replay position."""

    session: ReplaySessionDTO = Field(..., description="Updated replay session metadata")
    revealed_bars: List[ChartBarDTO] = Field(
        ..., description="Bounded historical bars revealed up to target position (NO FUTURE BARS)"
    )


class ReplayCapabilityResponse(BaseModel):
    """Discovered replay capabilities and historical coverage for an instrument/interval."""

    instrument_id: UUID = Field(..., description="Canonical instrument entity UUID")
    display_symbol: str = Field(..., description="Display symbol")
    is_replay_supported: bool = Field(
        ..., description="True if sufficient historical bars exist for replay"
    )
    supported_intervals: List[str] = Field(
        ..., description="List of supported canonical intervals for replay"
    )
    earliest_available_bar: Optional[datetime] = Field(
        None, description="Earliest qualified historical observation timestamp"
    )
    latest_available_bar: Optional[datetime] = Field(
        None, description="Latest qualified historical observation timestamp"
    )
    total_bars_available: int = Field(..., description="Total count of stored historical bars")
    point_in_time_guarantee: bool = Field(
        False, description="Explicit flag indicating playback uses current revised history"
    )
    methodological_notice: str = Field(
        ..., description="Disclosure regarding historical data revisions vs point-in-time claims"
    )
