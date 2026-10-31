"""Master Service for ATLAS God's Eye Financial Intelligence (Stage 140).

Orchestrates:
- 8 Canonical Investigation Lenses
- Bounded Cross-Domain Queries (Events, Graph, Exposure, Scoring, Geography, Markets)
- Bitemporal "World Time Travel" Historical Reconstruction
- Strict Semantic Boundaries (no fake omniscience, no auto-trading, correlation != causation)
- AI Tool Execution (atlas.gods_eye.investigate)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.intelligence.gods_eye.domain import (
    INSTITUTIONAL_DISCLAIMERS,
    GodsEyeContext,
    GodsEyeHistoricalVintage,
    GodsEyeInvestigationResult,
    GodsEyeLensDefinition,
    GodsEyeLensType,
    GodsEyeViewMode,
)
from atlas.intelligence.gods_eye.errors import (
    GodsEyeEntityNotFoundError,
    GodsEyeLookAheadViolationError,
    GodsEyeTenantAccessDeniedError,
)
from atlas.intelligence.gods_eye.lenses import CANONICAL_LENSES, LensRegistry
from atlas.intelligence.gods_eye.orchestrator import GodsEyeOrchestrator


class AtlasGodsEyeService:
    """Master institutional service orchestrating God's Eye Financial Intelligence."""

    def __init__(self, orchestrator: Optional[GodsEyeOrchestrator] = None):
        self.orchestrator = orchestrator or GodsEyeOrchestrator()

    def get_capabilities(self) -> Dict[str, Any]:
        """Return authorized capabilities and institutional safety guarantees."""
        return {
            "stage": 140,
            "system_name": "ATLAS God's Eye Financial Intelligence",
            "version": "1.0.0",
            "supported_lenses": [lens.value for lens in GodsEyeLensType],
            "supported_view_modes": [mode.value for mode in GodsEyeViewMode],
            "guarantees": [
                "Bitemporal point-in-time integrity (zero look-ahead leakage)",
                "Multi-tenant private portfolio isolation",
                "Bounded knowledge graph traversals (depth <= 3, fanout capped)",
                "Observation vs causation separation",
                "Proximity vs confirmed damage separation (defaults to UNKNOWN)",
                "Source revocation enforcement and cache eviction",
                "Partial failure resilience across independent data sources",
                "No automated trading or execution capabilities",
            ],
            "disclaimers": dict(INSTITUTIONAL_DISCLAIMERS),
        }

    def list_lenses(self) -> List[GodsEyeLensDefinition]:
        """List all 8 canonical investigation lenses."""
        return LensRegistry.list_lenses()

    def get_lens(self, lens_id: str) -> GodsEyeLensDefinition:
        """Retrieve definition for a specific investigation lens."""
        return LensRegistry.get_lens(lens_id)

    def investigate(
        self,
        context: GodsEyeContext,
        principal: Optional[AuthPrincipal] = None,
    ) -> GodsEyeInvestigationResult:
        """Execute a full cross-domain investigation for the specified context."""
        return self.orchestrator.execute_investigation(context=context, principal=principal)

    def reconstruct_historical_world(
        self,
        as_of: datetime,
        lens: GodsEyeLensType = GodsEyeLensType.HISTORICAL_RESEARCH,
        entity_id: Optional[str] = None,
        principal: Optional[AuthPrincipal] = None,
    ) -> GodsEyeInvestigationResult:
        """Reconstruct global financial intelligence strictly as-of a historical timestamp."""
        ctx = GodsEyeContext(
            lens=lens,
            as_of=as_of,
            selected_entity_id=entity_id,
        )
        return self.orchestrator.execute_investigation(context=ctx, principal=principal)

    def compare_historical_vintages(
        self,
        entity_id: str,
        as_of_v1: datetime,
        as_of_v2: datetime,
        principal: Optional[AuthPrincipal] = None,
    ) -> Dict[str, Any]:
        """Compare knowledge graph topology and disclosures between two historical dates (Fixture L)."""
        res_v1 = self.investigate(
            GodsEyeContext(lens=GodsEyeLensType.HISTORICAL_RESEARCH, as_of=as_of_v1, selected_entity_id=entity_id),
            principal=principal,
        )
        res_v2 = self.investigate(
            GodsEyeContext(lens=GodsEyeLensType.HISTORICAL_RESEARCH, as_of=as_of_v2, selected_entity_id=entity_id),
            principal=principal,
        )

        return {
            "entity_id": entity_id,
            "vintage_1": {
                "as_of": as_of_v1.isoformat(),
                "node_count": res_v1.knowledge_graph_subgraph.get("node_count", 0),
                "edge_count": res_v1.knowledge_graph_subgraph.get("edge_count", 0),
                "nodes": res_v1.knowledge_graph_subgraph.get("nodes", []),
                "edges": res_v1.knowledge_graph_subgraph.get("edges", []),
            },
            "vintage_2": {
                "as_of": as_of_v2.isoformat(),
                "node_count": res_v2.knowledge_graph_subgraph.get("node_count", 0),
                "edge_count": res_v2.knowledge_graph_subgraph.get("edge_count", 0),
                "nodes": res_v2.knowledge_graph_subgraph.get("nodes", []),
                "edges": res_v2.knowledge_graph_subgraph.get("edges", []),
            },
            "topology_changed": res_v1.knowledge_graph_subgraph != res_v2.knowledge_graph_subgraph,
        }

    def execute_ai_investigation_tool(
        self,
        params: Dict[str, Any],
        principal: Optional[AuthPrincipal] = None,
    ) -> Dict[str, Any]:
        """Backend implementation for the read-only AI investigation tool 'atlas.gods_eye.investigate' (Fixture P)."""
        lens_str = params.get("lens", "GLOBAL_EVENTS")
        lens = LensRegistry.get_lens(lens_str).lens_id
        as_of_raw = params.get("as_of")
        as_of = datetime.fromisoformat(as_of_raw) if as_of_raw else None

        ctx = GodsEyeContext(
            lens=lens,
            as_of=as_of,
            selected_entity_id=params.get("entity_id"),
            selected_event_id=params.get("event_id"),
            selected_portfolio_id=params.get("portfolio_id"),
            max_graph_depth=params.get("max_depth", 2),
            search_query=params.get("query"),
        )

        result = self.investigate(ctx, principal=principal)

        return {
            "tool_name": "atlas.gods_eye.investigate",
            "status": "COMPLETED",
            "findings_summary": f"Executed situational awareness investigation across {len(result.events)} events, {len(result.map_features)} spatial features, and {result.knowledge_graph_subgraph.get('node_count', 0)} knowledge graph nodes under lens '{lens.value}'.",
            "events_count": len(result.events),
            "top_events": result.events[:3],
            "map_features_count": len(result.map_features),
            "primary_evidence_sources": [s["name"] for s in result.evidence_sources],
            "unknowns_and_limitations": [
                "Operational damage status for proximate physical facilities remains UNKNOWN pending certified inspection reports.",
                "Market context movements reflect observational correlation only, not causal attribution.",
            ],
            "disclaimers": result.disclaimers,
        }

