"""Approved source registry, licensing policies, and source manifests (Stage 132)."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SourceLicensingPolicy(str, Enum):
    """Categorical licensing classes governing data ingestion and display."""

    OFFICIAL_DISCLOSURE = "OFFICIAL_DISCLOSURE"
    REGULATORY_PUBLIC = "REGULATORY_PUBLIC"
    GLEIF_OPEN = "GLEIF_OPEN"
    ODBL_OPENSTREETMAP = "ODBL_OPENSTREETMAP"
    COMMERCIAL_RESTRICTED = "COMMERCIAL_RESTRICTED"
    TENANT_PRIVATE = "TENANT_PRIVATE"


@dataclass
class FacilitySourceManifest:
    """Canonical metadata for a registered evidence source provider or document."""

    source_manifest_id: str
    source_name: str
    publisher: str
    licensing_policy: SourceLicensingPolicy
    attribution: str
    source_url: Optional[str] = None
    is_revoked: bool = False
    valid_until: Optional[datetime.datetime] = None
    registered_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def is_valid_now(self) -> bool:
        """Verify the source has not been revoked or expired."""
        if self.is_revoked:
            return False
        if self.valid_until is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if self.valid_until.tzinfo is None:
                vu = self.valid_until.replace(tzinfo=datetime.timezone.utc)
            else:
                vu = self.valid_until
            if vu < now:
                return False
        return True


CANONICAL_SOURCE_REGISTRY: dict[str, FacilitySourceManifest] = {
    "src_sec_edgar_10k": FacilitySourceManifest(
        source_manifest_id="src_sec_edgar_10k",
        source_name="SEC EDGAR Annual Filings (Form 10-K Item 2: Properties)",
        publisher="U.S. Securities and Exchange Commission",
        licensing_policy=SourceLicensingPolicy.REGULATORY_PUBLIC,
        attribution="U.S. SEC EDGAR Public Domain Disclosures",
    ),
    "src_gleif_lei": FacilitySourceManifest(
        source_manifest_id="src_gleif_lei",
        source_name="Global Legal Entity Identifier Foundation Golden Copy",
        publisher="GLEIF",
        licensing_policy=SourceLicensingPolicy.GLEIF_OPEN,
        attribution="Global Legal Entity Identifier Foundation (GLEIF) CC0 1.0",
        source_url="https://www.gleif.org",
    ),
    "src_company_ir_disclosures": FacilitySourceManifest(
        source_manifest_id="src_company_ir_disclosures",
        source_name="Official Corporate Investor Relations & Annual Reports",
        publisher="Corporate Disclosures",
        licensing_policy=SourceLicensingPolicy.OFFICIAL_DISCLOSURE,
        attribution="Corporate Investor Relations Published Materials",
    ),
    "src_osm_facilities": FacilitySourceManifest(
        source_manifest_id="src_osm_facilities",
        source_name="OpenStreetMap Corporate Geometries",
        publisher="OpenStreetMap Contributors",
        licensing_policy=SourceLicensingPolicy.ODBL_OPENSTREETMAP,
        attribution="© OpenStreetMap contributors, licensed under ODbL",
        source_url="https://www.openstreetmap.org",
    ),
}

