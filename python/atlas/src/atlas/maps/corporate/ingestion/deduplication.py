"""Facility candidate matching and deduplication (Stage 132).

Prevents duplicate facility inflation while ensuring unrelated corporate entities
sharing a commercial building or office park are NOT merged.
"""

from __future__ import annotations

import math
from typing import Optional

from atlas.maps.corporate.domain import CorporateFacility
from atlas.maps.corporate.ingestion.geocoding import normalize_address


def haversine_distance_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate great-circle distance between two points on the WGS84 sphere in meters."""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def find_matching_facility(
    candidate: CorporateFacility,
    existing_facilities: list[CorporateFacility],
    distance_threshold_meters: float = 75.0,
) -> Optional[CorporateFacility]:
    """Find existing canonical facility matching candidate based on proximity, address, and entity.

    Guarantees:
    - Same address/proximity with SAME primary entity or linked corporate group is recognized as duplicate.
    - Two unrelated companies sharing the same commercial building are NOT merged.
    """
    candidate_norm_addr = normalize_address(candidate.address_text)
    candidate_norm_name = candidate.canonical_name.lower().strip()

    for existing in existing_facilities:
        # Check entity compatibility: must share at least one corporate entity link
        shared_entities = False
        if candidate.primary_entity_id and existing.primary_entity_id:
            if candidate.primary_entity_id == existing.primary_entity_id:
                shared_entities = True

        candidate_links = {l.legal_entity_id for l in candidate.links} | {l.company_id for l in candidate.links}
        existing_links = {l.legal_entity_id for l in existing.links} | {l.company_id for l in existing.links}
        if candidate_links & existing_links:
            shared_entities = True

        if not shared_entities:
            # Different unrelated businesses at same address -> do NOT merge
            continue

        # Proximity check
        dist = None
        if (
            candidate.longitude is not None
            and candidate.latitude is not None
            and existing.longitude is not None
            and existing.latitude is not None
        ):
            dist = haversine_distance_meters(
                candidate.longitude, candidate.latitude, existing.longitude, existing.latitude
            )

        if dist is not None and dist <= distance_threshold_meters:
            return existing

        # Address match
        existing_norm_addr = normalize_address(existing.address_text)
        if candidate_norm_addr and existing_norm_addr and candidate_norm_addr == existing_norm_addr:
            return existing

        # Name match within same locality
        if (
            candidate.locality
            and existing.locality
            and candidate.locality.lower() == existing.locality.lower()
            and candidate_norm_name == existing.canonical_name.lower().strip()
        ):
            return existing

    return None

