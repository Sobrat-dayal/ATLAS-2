"""Lineage and Mathematical Provenance Tracking (Stage 137).

Enforces institutional provenance invariants:
- Every exposure calculation produces an auditable lineage record referencing exact input identifiers,
  formal mathematical formulas, filing citations, and knowledge graph paths.
- Verifies source entitlement licenses; invalidates calculation lineage if a source is revoked.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from atlas.exposure.errors import SourceLicenseRevokedError


class ExposureLineageItem(BaseModel):
    lineage_id: str
    exposure_id: str
    analysis_run_id: str
    calculation_method: str
    formula_expression: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    source_ids: List[str] = Field(default_factory=list)
    graph_edge_ids: List[str] = Field(default_factory=list)
    as_of: Optional[str] = None
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_entitled: bool = True
    tenant_id: Optional[str] = None


class ExposureProvenanceRegistry:
    """In-memory audit registry for exposure calculation lineage."""
    def __init__(self):
        self._items: Dict[str, ExposureLineageItem] = {}
        self._revoked_sources: set[str] = set()

    def record_lineage(self, item: ExposureLineageItem) -> None:
        for sid in item.source_ids:
            if sid in self._revoked_sources:
                raise SourceLicenseRevokedError(source_id=sid)
        self._items[item.exposure_id] = item

    def get_lineage(self, exposure_id: str) -> Optional[ExposureLineageItem]:
        item = self._items.get(exposure_id)
        if not item:
            return None
        for sid in item.source_ids:
            if sid in self._revoked_sources:
                raise SourceLicenseRevokedError(source_id=sid)
        return item

    def revoke_source(self, source_id: str) -> None:
        """Mark a data provider or source entitlement as revoked."""
        self._revoked_sources.add(source_id)

    def restore_source(self, source_id: str) -> None:
        self._revoked_sources.discard(source_id)

