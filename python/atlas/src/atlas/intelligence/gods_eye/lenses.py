"""Canonical Investigation Lenses for God's Eye Financial Intelligence (Stage 140).

Registers and configures the 8 canonical lenses:
1. GLOBAL_EVENTS
2. MONETARY_POLICY
3. CORPORATE_INTELLIGENCE
4. GEOPOLITICAL
5. COMMODITY_INFRASTRUCTURE
6. PHYSICAL_WORLD
7. PORTFOLIO_INTELLIGENCE
8. HISTORICAL_RESEARCH
"""

from __future__ import annotations

from typing import Dict, List, Optional
from atlas.intelligence.gods_eye.domain import (
    GodsEyeLensDefinition,
    GodsEyeLensType,
    GodsEyeViewMode,
)

CANONICAL_LENSES: Dict[GodsEyeLensType, GodsEyeLensDefinition] = {
    GodsEyeLensType.GLOBAL_EVENTS: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.GLOBAL_EVENTS,
        label="Global Events Situational Awareness",
        description="Comprehensive cross-domain global surveillance across macro, corporate, geopolitical, and physical events.",
        primary_event_categories=[
            "FINANCIAL",
            "CORPORATE",
            "ECONOMIC",
            "MONETARY_POLICY",
            "GEOPOLITICAL",
            "NATURAL_DISASTER",
            "INFRASTRUCTURE",
        ],
        default_layers=["global_event_clusters", "macro_economic_tint", "major_facilities"],
        default_view_mode=GodsEyeViewMode.TWO_DIMENSIONAL,
        requires_portfolio=False,
        supported_graph_predicates=["IMPACTS_SECTOR", "OCCURRED_IN_JURISDICTION", "AFFECTS_ENTITY"],
    ),
    GodsEyeLensType.MONETARY_POLICY: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.MONETARY_POLICY,
        label="Monetary Policy & Central Banks",
        description="Official central bank rate decisions, statements, balance sheets, and yield curve contextual observations.",
        primary_event_categories=["MONETARY_POLICY", "ECONOMIC"],
        default_layers=["central_bank_headquarters", "sovereign_yield_spreads", "currency_regimes"],
        default_view_mode=GodsEyeViewMode.TWO_DIMENSIONAL,
        requires_portfolio=False,
        supported_graph_predicates=["ISSUED_BY_CENTRAL_BANK", "SETS_POLICY_RATE_FOR", "CORRELATES_WITH_YIELD"],
    ),
    GodsEyeLensType.CORPORATE_INTELLIGENCE: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.CORPORATE_INTELLIGENCE,
        label="Corporate Intelligence & Filings",
        description="Audited 10-K/10-Q disclosures, earnings releases, corporate group structures, and facility footprints.",
        primary_event_categories=["CORPORATE", "FINANCIAL"],
        default_layers=["corporate_headquarters", "operational_facilities", "supply_chain_hops"],
        default_view_mode=GodsEyeViewMode.TWO_DIMENSIONAL,
        requires_portfolio=False,
        supported_graph_predicates=["FILED_DISCLOSURE", "OPERATES_FACILITY", "OWNS_SUBSIDIARY", "SUPPLIES_TO"],
    ),
    GodsEyeLensType.GEOPOLITICAL: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.GEOPOLITICAL,
        label="Geopolitical & Sanctions Intelligence",
        description="Official sanctions designations, export controls, trade tariffs, diplomatic accords, and cross-border frictions.",
        primary_event_categories=["SANCTIONS", "GEOPOLITICAL", "REGULATORY"],
        default_layers=["sanctioned_jurisdictions", "disputed_borders", "strategic_trade_routes"],
        default_view_mode=GodsEyeViewMode.TWO_DIMENSIONAL,
        requires_portfolio=False,
        supported_graph_predicates=["DESIGNATED_BY_AUTHORITY", "RESTRICTS_TRADE_WITH", "LOCATED_IN_SANCTIONED_ZONE"],
    ),
    GodsEyeLensType.COMMODITY_INFRASTRUCTURE: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.COMMODITY_INFRASTRUCTURE,
        label="Commodity & Physical Infrastructure",
        description="Global maritime chokepoints, container ports, oil & gas pipelines, refineries, and electrical transmission grids.",
        primary_event_categories=["INFRASTRUCTURE", "ECONOMIC"],
        default_layers=["maritime_ports", "strategic_chokepoints", "pipeline_networks", "refineries"],
        default_view_mode=GodsEyeViewMode.THREE_DIMENSIONAL_GLOBE,
        requires_portfolio=False,
        supported_graph_predicates=["TRANSPORTS_COMMODITY", "OPERATES_INFRASTRUCTURE", "CONGESTION_POINT_FOR"],
    ),
    GodsEyeLensType.PHYSICAL_WORLD: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.PHYSICAL_WORLD,
        label="Physical World & Natural Hazards",
        description="USGS earthquakes, NOAA severe weather, tropical storm tracks, and spatial hazard perimeters.",
        primary_event_categories=["NATURAL_DISASTER", "PHYSICAL_WORLD"],
        default_layers=["usgs_seismic_epicenters", "hazard_impact_radii", "critical_facilities_overlay"],
        default_view_mode=GodsEyeViewMode.THREE_DIMENSIONAL_GLOBE,
        requires_portfolio=False,
        supported_graph_predicates=["PROXIMATE_TO_FACILITY", "LOCATED_WITHIN_HAZARD_RADIUS"],
    ),
    GodsEyeLensType.PORTFOLIO_INTELLIGENCE: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.PORTFOLIO_INTELLIGENCE,
        label="Portfolio Holdings Look-Through",
        description="Private tenant-authorized portfolio exposure mapping, direct holding vulnerabilities, and entity prioritization.",
        primary_event_categories=["FINANCIAL", "CORPORATE", "MONETARY_POLICY", "INFRASTRUCTURE"],
        default_layers=["portfolio_facility_exposure", "supply_chain_dependencies"],
        default_view_mode=GodsEyeViewMode.HYBRID_SPLIT,
        requires_portfolio=True,
        supported_graph_predicates=["HELD_IN_PORTFOLIO", "EXPOSED_TO_RISK", "SUPPLIES_HOLDING"],
    ),
    GodsEyeLensType.HISTORICAL_RESEARCH: GodsEyeLensDefinition(
        lens_id=GodsEyeLensType.HISTORICAL_RESEARCH,
        label="Historical Point-in-Time Reconstruction",
        description="Zero look-ahead bitemporal world reconstruction, vintage analysis, and historical disclosure comparison.",
        primary_event_categories=[
            "FINANCIAL",
            "CORPORATE",
            "ECONOMIC",
            "MONETARY_POLICY",
            "GEOPOLITICAL",
            "NATURAL_DISASTER",
            "INFRASTRUCTURE",
        ],
        default_layers=["historical_event_timeline", "vintage_graph_topology"],
        default_view_mode=GodsEyeViewMode.TWO_DIMENSIONAL,
        requires_portfolio=False,
        supported_graph_predicates=["HISTORICALLY_OWNED", "PRIOR_DISCLOSURE", "SUPERSEDED_BY"],
    ),
}


class LensRegistry:
    """Registry providing lens lookup, listing, and validation."""

    @classmethod
    def list_lenses(cls) -> List[GodsEyeLensDefinition]:
        return list(CANONICAL_LENSES.values())

    @classmethod
    def get_lens(cls, lens_id: str | GodsEyeLensType) -> GodsEyeLensDefinition:
        if isinstance(lens_id, str):
            try:
                lens_id = GodsEyeLensType(lens_id.upper())
            except ValueError:
                # Default fallback
                lens_id = GodsEyeLensType.GLOBAL_EVENTS
        return CANONICAL_LENSES.get(lens_id, CANONICAL_LENSES[GodsEyeLensType.GLOBAL_EVENTS])

