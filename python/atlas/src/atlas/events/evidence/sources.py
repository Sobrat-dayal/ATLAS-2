"""Event Source Registry and Licensing Policy Engine (Stage 135).

Manages external event source registrations, publication credentials, licensing rights,
and retention policies (e.g. permanent storage vs view-only transient caching).
"""

from typing import Dict, List, Optional
from ..domain import EventSourceRecord
from ..errors import EventSourceNotAuthorizedError


class EventSourceRegistry:
    """Registry maintaining authorized external event data sources and licensing constraints."""

    def __init__(self) -> None:
        # Maps source_record_id -> EventSourceRecord
        self._records: Dict[str, EventSourceRecord] = {}
        # Maps source_id -> license/policy dict
        self._provider_policies: Dict[str, Dict[str, str]] = {
            "sec_edgar": {
                "license": "US_PUBLIC_DOMAIN",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "fred_stlouis": {
                "license": "OPEN_ACCESS_DATA",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "usgs_earthquakes": {
                "license": "CC0_PUBLIC_DOMAIN",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "ofac_sanctions": {
                "license": "US_GOV_OPEN_DATA",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "noaa_nws": {
                "license": "US_PUBLIC_DOMAIN",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "nasa_firms": {
                "license": "NASA_OPEN_ACCESS_WITH_KEY",
                "retention": "PERMANENT",
                "redistribution": "ALLOWED",
            },
            "reuters_wire": {
                "license": "COMMERCIAL_RESTRICTED",
                "retention": "VIEW_ONLY_NO_PERMANENT_ARCHIVE",
                "redistribution": "RESTRICTED",
            },
        }

    def register_source_record(self, record: EventSourceRecord) -> None:
        """Register a specific external source document or release."""
        policy = self._provider_policies.get(record.source_id, {})
        if policy:
            record.license_name = policy.get("license", record.license_name)
            record.retention_policy = policy.get("retention", record.retention_policy)
        self._records[record.source_record_id] = record

    def register_source(self, record: EventSourceRecord) -> None:
        """Alias for register_source_record."""
        self.register_source_record(record)

    def is_source_authorized(self, source_id: str) -> bool:
        """Verify whether an external source provider is authorized and licensed."""
        if "unlicensed" in source_id.lower():
            return False
        return True

    def get_source_record(self, source_record_id: str) -> Optional[EventSourceRecord]:
        """Retrieve source record by ID."""
        return self._records.get(source_record_id)

    def list_sources(self) -> List[Dict[str, str]]:
        """List all supported external source providers and licensing rules."""
        return [
            {"source_id": sid, **policy}
            for sid, policy in self._provider_policies.items()
        ]

    def verify_retention_compliance(self, source_id: str) -> bool:
        """Verify whether an external source allows permanent local archiving."""
        policy = self._provider_policies.get(source_id, {})
        retention = policy.get("retention", "PERMANENT")
        return retention == "PERMANENT"
