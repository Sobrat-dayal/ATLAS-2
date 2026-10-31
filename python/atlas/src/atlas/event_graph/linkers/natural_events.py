"""Natural Events Relationship Linker (Stage 136).

Links earthquakes, storms, and natural occurrences to geographic jurisdictions
and nearby infrastructure assets or corporate facilities via GEOGRAPHICALLY_NEAR.

Enforces institutional invariants:
1. Records verifiable proximity metadata (distance_km, calculation basis, precision tier).
2. NEVER claims physical damage, destruction, operational loss, or economic impairment (strictly Stage 137).
3. Strictly prohibits assigning proximity to assets when event coordinates lack required precision.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional

from atlas.events.domain import AtlasUniversalEvent, GeographicScopeType
from ..domain import (
    AtlasEventEntityRelationship,
    GraphNodeType,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from .base import BaseEventRelationshipLinker


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in kilometers."""
    r = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


class NaturalEventRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for natural disasters and physical-world observations."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}
        geo = event.geographic_scope

        # 1. Geographic Jurisdiction / Country
        if geo.country_code:
            try:
                country_node = self.resolver.resolve(geo.country_code, id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.OCCURRED_IN,
                    origin=RelationshipOrigin.GEOSPATIAL_CALCULATION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="EVENT_JURISDICTION",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        # 2. Check for Point Coordinates before proximity calculation
        event_lat = geo.latitude
        event_lon = geo.longitude
        if event_lat is None and geo.coordinates and len(geo.coordinates) >= 2:
            event_lon, event_lat = geo.coordinates[0], geo.coordinates[1]

        # Only evaluate proximity if coordinates exist and scope is not coarse country/global
        has_precise_point = (
            event_lat is not None
            and event_lon is not None
            and geo.scope_type in [GeographicScopeType.POINT, GeographicScopeType.COORDINATES]
        )

        if has_precise_point:
            # Check candidate nearby facilities or infrastructure assets registered in resolver
            max_proximity_radius_km = float(payload.get("proximity_radius_km", 100.0))
            for node in self.resolver.list_all_nodes():
                if node.node_type in [GraphNodeType.INFRASTRUCTURE_ASSET, GraphNodeType.CORPORATE_FACILITY]:
                    target_lat = node.metadata.get("latitude")
                    target_lon = node.metadata.get("longitude")
                    if target_lat is not None and target_lon is not None:
                        dist = haversine_distance_km(event_lat, event_lon, float(target_lat), float(target_lon))
                        if dist <= max_proximity_radius_km:
                            proximity_meta = {
                                "distance_km": dist,
                                "calculation_basis": "HAVERSINE_GREAT_CIRCLE",
                                "event_coordinates": [event_lon, event_lat],
                                "asset_coordinates": [float(target_lon), float(target_lat)],
                                "threshold_radius_km": max_proximity_radius_km,
                                "disclaimer": "Proximity reflects spatial distance only; no physical damage or economic impairment asserted.",
                            }
                            rel_near = self.build_relationship(
                                event=event,
                                target_node=node,
                                predicate=PredicateType.GEOGRAPHICALLY_NEAR,
                                origin=RelationshipOrigin.GEOSPATIAL_CALCULATION,
                                verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                                relationship_role="SPATIALLY_PROXIMATE_ASSET",
                                evidence_ids=evidence_ids,
                                derivation_method="GEOSPATIAL_RADIUS_CALCULATION",
                                proximity_metadata=proximity_meta,
                            )
                            relationships.append(rel_near)

        return relationships

