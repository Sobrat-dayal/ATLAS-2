"""Operator, owner, and occupancy relationship separation (Stage 132).

Guarantees:
- Legal ownership does not imply day-to-day operation.
- Facility operation does not imply property ownership.
- Leasing and occupancy are modeled as distinct legal relationships.
"""

from __future__ import annotations

from typing import Any

from atlas.maps.corporate.domain import FacilityEntityLink, FacilityRelationshipType


def get_facility_owners(links: list[FacilityEntityLink]) -> list[FacilityEntityLink]:
    """Retrieve verified property owners of the facility."""
    return [link for link in links if link.relationship_type == FacilityRelationshipType.OWNED_BY]


def get_facility_operators(links: list[FacilityEntityLink]) -> list[FacilityEntityLink]:
    """Retrieve verified operating entities of the facility."""
    return [link for link in links if link.relationship_type == FacilityRelationshipType.OPERATED_BY]


def get_facility_tenants_and_occupants(links: list[FacilityEntityLink]) -> list[FacilityEntityLink]:
    """Retrieve lessees, occupants, and tenant entities."""
    return [
        link
        for link in links
        if link.relationship_type in (FacilityRelationshipType.LEASED_BY, FacilityRelationshipType.OCCUPIED_BY)
    ]


def summarize_entity_roles(links: list[FacilityEntityLink]) -> dict[str, list[dict[str, Any]]]:
    """Summarize corporate entity links by their canonical relationship role."""
    summary: dict[str, list[dict[str, Any]]] = {
        "owners": [],
        "operators": [],
        "tenants": [],
        "headquarters": [],
        "other": [],
    }

    for link in links:
        payload = {
            "entity_id": link.legal_entity_id,
            "company_id": link.company_id,
            "role_description": link.role_description,
            "valid_from": link.valid_from.isoformat() if link.valid_from else None,
            "valid_to": link.valid_to.isoformat() if link.valid_to else None,
            "verification_status": link.verification_status.value,
        }
        if link.relationship_type == FacilityRelationshipType.OWNED_BY:
            summary["owners"].append(payload)
        elif link.relationship_type == FacilityRelationshipType.OPERATED_BY:
            summary["operators"].append(payload)
        elif link.relationship_type in (FacilityRelationshipType.LEASED_BY, FacilityRelationshipType.OCCUPIED_BY):
            summary["tenants"].append(payload)
        elif link.relationship_type in (
            FacilityRelationshipType.HEADQUARTERS_OF,
            FacilityRelationshipType.REGISTERED_ADDRESS_OF,
        ):
            summary["headquarters"].append(payload)
        else:
            summary["other"].append(payload)

    return summary

