import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

from .types import ProvenanceSourceKind, ProvenanceRecordKind, EvidenceRole


class ProvenanceSourceResponse(BaseModel):
    source_id: uuid.UUID
    source_key: Optional[str]
    name: str
    source_kind: str
    base_url: Optional[str]
    is_system: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ProvenanceRecordResponse(BaseModel):
    provenance_id: uuid.UUID
    source: ProvenanceSourceResponse
    record_kind: str
    source_reference: Optional[str]
    source_uri: Optional[str]
    source_locator: Optional[str]
    published_at: Optional[datetime.datetime]
    observed_at: Optional[datetime.datetime]
    retrieved_at: datetime.datetime
    license_name: Optional[str]
    license_url: Optional[str]
    attribution_text: Optional[str]
    content_hash_sha256: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ProvenanceLinkResponse(BaseModel):
    provenance: ProvenanceRecordResponse
    evidence_role: str
    confidence_score: Optional[float]

    class Config:
        from_attributes = True


class TargetProvenanceListResponse(BaseModel):
    items: List[ProvenanceLinkResponse]
    total: int


class ProvenanceSourceListResponse(BaseModel):
    items: List[ProvenanceSourceResponse]
    total: int
