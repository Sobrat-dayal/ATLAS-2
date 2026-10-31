"""Sector and Industry Exposure Domain Handler (Stage 137).

Enforces institutional sector invariants:
- Direct mapping from authoritative industry taxonomies (GICS, ICB, NAICS).
- Preserves unclassified entities as uncovered without guessing.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure.domain import (
    AtlasExposureResult,
    CoverageStatus,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureRelationshipStrength,
    ExposureType,
    UncertaintyClass,
)


def analyze_entity_sector_classification(
    run_id: str,
    entity_ref: CanonicalGraphNodeRef,
    sector_name: Optional[str],
    industry_name: Optional[str] = None,
    taxonomy: str = "GICS"
) -> AtlasExposureResult:
    """Analyze and record sector classification for an entity."""
    if not sector_name or not sector_name.strip():
        return AtlasExposureResult(
            exposure_id=f"exp-sec-unavail-{run_id}-{entity_ref.entity_id}",
            analysis_run_id=run_id,
            subject_entity_ref=entity_ref,
            target_entity_ref=entity_ref,
            exposure_domain=ExposureDomain.SECTOR,
            exposure_type=ExposureType.SECTOR_ALLOCATION_EXPOSURE,
            exposure_measure_id="PORTFOLIO_NAV_WEIGHT_V1",
            evidence_class=ExposureEvidenceClass.UNAVAILABLE,
            relationship_strength=ExposureRelationshipStrength.UNRESOLVED,
            amount=None,
            unit="PERCENT",
            percentage=None,
            calculation_method_id="TAXONOMY_LOOKUP",
            coverage_status=CoverageStatus.UNCOVERED,
            uncertainty_class=UncertaintyClass.SOURCE_INCOMPLETE,
            explanation=f"Entity {entity_ref.canonical_name} does not have a verified {taxonomy} sector classification."
        )

    sec_ref = CanonicalGraphNodeRef(
        node_type=GraphNodeType.SECTOR,
        entity_id=sector_name.upper().replace(" ", "_"),
        canonical_name=sector_name
    )

    return AtlasExposureResult(
        exposure_id=f"exp-sec-{run_id}-{entity_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=entity_ref,
        target_entity_ref=sec_ref,
        exposure_domain=ExposureDomain.SECTOR,
        exposure_type=ExposureType.SECTOR_ALLOCATION_EXPOSURE,
        exposure_measure_id="PORTFOLIO_NAV_WEIGHT_V1",
        evidence_class=ExposureEvidenceClass.REPORTED,
        relationship_strength=ExposureRelationshipStrength.DIRECT_REPORTED,
        amount=Decimal("100.0"),
        unit="PERCENT",
        percentage=Decimal("100.0"),
        calculation_method_id="TAXONOMY_LOOKUP",
        coverage_status=CoverageStatus.COMPLETE,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
        explanation=f"{entity_ref.canonical_name} is classified in {taxonomy} Sector '{sector_name}'."
    )
