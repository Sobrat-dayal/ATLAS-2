"""Universal Event Model Domain Definitions (Stage 135).

Provides canonical domain models, categories, lifecycle states, verification statuses,
bitemporal models, evidence structures, claim schemas, and universal event envelopes.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    """Primary canonical event categories across the ATLAS platform."""
    FINANCIAL = "FINANCIAL"
    CORPORATE = "CORPORATE"
    ECONOMIC = "ECONOMIC"
    MONETARY_POLICY = "MONETARY_POLICY"
    REGULATORY = "REGULATORY"
    SANCTIONS = "SANCTIONS"
    GEOPOLITICAL = "GEOPOLITICAL"
    NEWS_REPORTED = "NEWS_REPORTED"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    PHYSICAL_WORLD = "PHYSICAL_WORLD"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    OTHER_VERIFIED_EVENT = "OTHER_VERIFIED_EVENT"


class EventLifecycleStatus(str, Enum):
    """Context-appropriate event lifecycle states."""
    SCHEDULED = "SCHEDULED"
    PROPOSED = "PROPOSED"
    ANNOUNCED = "ANNOUNCED"
    REPORTED = "REPORTED"
    OCCURRED = "OCCURRED"
    CONFIRMED = "CONFIRMED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"
    DISPUTED = "DISPUTED"
    STATUS_UNKNOWN = "STATUS_UNKNOWN"


class EventVerificationStatus(str, Enum):
    """Institutional evidence-based verification tier."""
    OFFICIALLY_CONFIRMED = "OFFICIALLY_CONFIRMED"
    INDEPENDENTLY_CORROBORATED = "INDEPENDENTLY_CORROBORATED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"


class DatePrecision(str, Enum):
    """Precision tier for occurrence or scheduling timestamps."""
    EXACT_TIMESTAMP = "EXACT_TIMESTAMP"
    DATE_ONLY = "DATE_ONLY"
    MONTH_ONLY = "MONTH_ONLY"
    YEAR_ONLY = "YEAR_ONLY"
    TIME_UNKNOWN = "TIME_UNKNOWN"


class EvidenceRole(str, Enum):
    """Functional role of supporting source evidence."""
    PRIMARY_SOURCE = "PRIMARY_SOURCE"
    OFFICIAL_CONFIRMATION = "OFFICIAL_CONFIRMATION"
    CORROBORATING_SOURCE = "CORROBORATING_SOURCE"
    CONTRADICTING_SOURCE = "CONTRADICTING_SOURCE"
    CORRECTION_SOURCE = "CORRECTION_SOURCE"
    RETRACTION_SOURCE = "RETRACTION_SOURCE"
    CONTEXTUAL_SOURCE = "CONTEXTUAL_SOURCE"


class ClaimConflictStatus(str, Enum):
    """Status of cross-source factual claim agreement."""
    NO_CONFLICT = "NO_CONFLICT"
    MINOR_DISCREPANCY = "MINOR_DISCREPANCY"
    CONFLICTED = "CONFLICTED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    RESOLVED = "RESOLVED"


class GeographicScopeType(str, Enum):
    """Geographic representation scope."""
    POINT = "POINT"
    COORDINATES = "COORDINATES"
    POLYGON = "POLYGON"
    MULTIPOLYGON = "MULTIPOLYGON"
    ADMINISTRATIVE_AREA = "ADMINISTRATIVE_AREA"
    REGION = "REGION"
    CONTINENT = "CONTINENT"
    COUNTRY = "COUNTRY"
    GLOBAL = "GLOBAL"
    GLOBAL_SCOPE = "GLOBAL_SCOPE"
    UNKNOWN = "UNKNOWN"


class EventGeographicScope(BaseModel):
    """Geographic footprint and jurisdiction of an event."""
    scope_type: GeographicScopeType = GeographicScopeType.GLOBAL_SCOPE
    country_code: Optional[str] = None
    jurisdiction: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    coordinates: Optional[List[float]] = None  # [lon, lat]
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON Point / Polygon
    area_name: Optional[str] = None


class EventSourceRecord(BaseModel):
    """Metadata representing an external source document, release, or feed."""
    source_record_id: str
    source_id: str
    publisher: str
    title: str
    original_url: Optional[str] = None
    published_at: Optional[datetime] = None
    retrieved_at: datetime
    source_version: int = 1
    license_name: str = "PROPRIETARY_OR_PUBLIC"
    retention_policy: str = "PERMANENT"
    access_policy: str = "PUBLIC"
    attribution: str = ""


class EventEvidence(BaseModel):
    """Link connecting a canonical event to an authorized source document."""
    evidence_id: str
    event_id: str
    source_record_id: str
    evidence_role: EvidenceRole
    source_version: int = 1
    verification_status: EventVerificationStatus = EventVerificationStatus.SOURCE_REPORTED
    snippet: Optional[str] = None
    locator: Optional[str] = None
    recorded_at: datetime


class EventClaim(BaseModel):
    """A granular factual claim asserted by a specific source record."""
    claim_id: str
    event_id: str
    source_record_id: str
    predicate: str
    claim_value: Any
    value_type: str = "STRING"
    units: Optional[str] = None
    qualifiers: Dict[str, Any] = Field(default_factory=dict)
    published_at: Optional[datetime] = None
    extracted_at: datetime
    verification_status: EventVerificationStatus = EventVerificationStatus.SOURCE_REPORTED


class EventRevision(BaseModel):
    """Non-destructive historical revision audit entry."""
    event_revision_id: str
    event_id: str
    revision_number: int
    changed_fields: Dict[str, Any]
    previous_revision_id: Optional[str] = None
    reason: str
    recorded_at: datetime
    published_at: Optional[datetime] = None


class AtlasUniversalEvent(BaseModel):
    """Universal canonical event entity across the ATLAS platform."""
    event_id: str
    canonical_event_key: str
    event_type: str
    event_subtype: str
    event_category: EventCategory
    title: str
    factual_summary: str
    lifecycle_status: EventLifecycleStatus
    verification_status: EventVerificationStatus
    occurred_at: Optional[datetime] = None
    date_precision: DatePrecision = DatePrecision.EXACT_TIMESTAMP
    announced_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    effective_at: Optional[datetime] = None
    source_published_at: Optional[datetime] = None
    first_public_at: Optional[datetime] = None
    first_observed_at: Optional[datetime] = None
    first_ingested_at: datetime
    updated_at: datetime
    geographic_scope: EventGeographicScope = Field(default_factory=EventGeographicScope)
    primary_source_id: str
    event_payload: Dict[str, Any] = Field(default_factory=dict)
    source_count: int = 1
    claim_conflict_status: ClaimConflictStatus = ClaimConflictStatus.NO_CONFLICT
    current_revision_number: int = 1
    schema_version: str = "v1.0"
    tenant_id: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    is_retracted: bool = False
    retraction_reason: Optional[str] = None
