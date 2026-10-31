"""Canonical Corporate Facility Registry and spatial query repository (Stage 132)."""

from __future__ import annotations

import datetime
from typing import Any, Optional

from atlas.maps.corporate.domain import (
    CorporateFacility,
    CorporateFacilityStatus,
    CorporateFacilityType,
    FacilityEntityLink,
    GeographicPrecisionClass,
    VerificationStatus,
)
from atlas.maps.corporate.errors import (
    FacilityAccessDeniedError,
    FacilityNotFoundError,
)
from atlas.maps.corporate.facilities.history import (
    filter_links_by_as_of,
    get_status_as_of,
    parse_as_of_timestamp,
)


class CorporateFacilityRegistry:
    """Canonical registry holding verified corporate facilities and entity relationships."""

    def __init__(self, initial_facilities: list[CorporateFacility] | None = None) -> None:
        self._facilities: dict[str, CorporateFacility] = {}
        self._entity_to_facilities: dict[str, set[str]] = {}
        self._country_to_facilities: dict[str, set[str]] = {}

        if initial_facilities:
            for fac in initial_facilities:
                self.register_facility(fac)

    def register_facility(self, facility: CorporateFacility) -> None:
        """Register or update a corporate facility and its indexes."""
        self._facilities[facility.facility_id] = facility

        # Index by primary entity
        if facility.primary_entity_id:
            self._entity_to_facilities.setdefault(facility.primary_entity_id, set()).add(facility.facility_id)

        # Index by linked entities
        for link in facility.links:
            if link.legal_entity_id:
                self._entity_to_facilities.setdefault(link.legal_entity_id, set()).add(facility.facility_id)
            if link.company_id:
                self._entity_to_facilities.setdefault(link.company_id, set()).add(facility.facility_id)

        # Index by country
        if facility.country_code:
            self._country_to_facilities.setdefault(facility.country_code.upper(), set()).add(facility.facility_id)

    def get_facility(self, facility_id: str, tenant_id: str | None = None) -> CorporateFacility:
        """Retrieve a single facility with tenant isolation checks."""
        facility = self._facilities.get(facility_id)
        if not facility:
            raise FacilityNotFoundError(facility_id)

        if not facility.is_public:
            if tenant_id is None or facility.tenant_id != tenant_id:
                raise FacilityAccessDeniedError(facility_id, tenant_id)

        return facility

    def query_facilities(
        self,
        company_id: str | None = None,
        entity_ids: set[str] | None = None,
        facility_types: list[CorporateFacilityType] | None = None,
        statuses: list[CorporateFacilityStatus] | None = None,
        country_code: str | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        as_of: str | datetime.datetime | None = None,
        precision_classes: list[GeographicPrecisionClass] | None = None,
        verification_statuses: list[VerificationStatus] | None = None,
        tenant_id: str | None = None,
        limit: int = 1000,
    ) -> list[CorporateFacility]:
        """Query facilities matching composite filters, spatial bounds, and temporal as-of dates."""
        as_of_dt = parse_as_of_timestamp(as_of)

        candidate_ids: set[str]
        if entity_ids is not None:
            candidate_ids = set()
            for eid in entity_ids:
                candidate_ids.update(self._entity_to_facilities.get(eid, set()))
        elif company_id is not None:
            candidate_ids = set(self._entity_to_facilities.get(company_id, set()))
        elif country_code is not None:
            candidate_ids = set(self._country_to_facilities.get(country_code.upper(), set()))
        else:
            candidate_ids = set(self._facilities.keys())

        matched: list[CorporateFacility] = []

        for fac_id in candidate_ids:
            fac = self._facilities.get(fac_id)
            if not fac:
                continue

            # Tenant isolation
            if not fac.is_public:
                if tenant_id is None or fac.tenant_id != tenant_id:
                    continue

            # Historical as-of filtering
            if as_of_dt is not None:
                if fac.operating_start_date and fac.operating_start_date > as_of_dt.date():
                    continue
                active_links = filter_links_by_as_of(fac.links, as_of_dt)
                if entity_ids is not None or company_id is not None:
                    # Must have active link to queried entity as of as_of_dt
                    target_set = entity_ids if entity_ids is not None else {company_id}
                    has_link = any(
                        l.legal_entity_id in target_set or l.company_id in target_set
                        for l in active_links
                    )
                    if not has_link and fac.primary_entity_id not in target_set:
                        continue

                current_status = get_status_as_of(fac, as_of_dt)
            else:
                current_status = fac.facility_status

            # Facility type filter
            if facility_types and fac.facility_type not in facility_types:
                continue

            # Status filter
            if statuses and current_status not in statuses:
                continue

            # Country filter
            if country_code and fac.country_code.upper() != country_code.upper():
                continue

            # Precision filter
            if precision_classes and fac.precision_class not in precision_classes:
                continue

            # Verification status filter
            if verification_statuses and fac.verification_status not in verification_statuses:
                continue

            # Bounding box filter (min_lon, min_lat, max_lon, max_lat)
            if bbox is not None:
                if fac.longitude is None or fac.latitude is None:
                    continue
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (min_lon <= fac.longitude <= max_lon and min_lat <= fac.latitude <= max_lat):
                    continue

            matched.append(fac)
            if len(matched) >= limit:
                break

        return matched

    def count_facilities(self) -> int:
        """Return total number of registered facilities."""
        return len(self._facilities)
