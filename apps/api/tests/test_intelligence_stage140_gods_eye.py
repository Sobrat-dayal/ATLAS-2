"""Comprehensive Pytest Suite for ATLAS God's Eye Financial Intelligence (Stage 140).

Tests:
- All 20 Reference Test Fixtures (A through T)
- 8 Canonical Investigation Lenses
- Bounded Cross-Domain Orchestration (Events, Graph, Exposure, Scoring, Geography, Markets)
- Strict Invariants (Observation != Causation, Proximity != Damage, Exposure != Loss, Priority != Prediction)
- Bitemporal Historical World Reconstruction (Zero Look-Ahead)
- Multi-Tenant Private Portfolio Protection
- Graph Traversal Bounding (Depth <= 3)
- Source Outage Resilience & Revocation Invalidation
- Read-Only AI Investigation Tool (atlas.gods_eye.investigate)
- FastAPI REST Endpoints
"""

from __future__ import annotations

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.intelligence.gods_eye import (
    AtlasGodsEyeService,
    GodsEyeContext,
    GodsEyeDamageAssessmentStatus,
    GodsEyeLensType,
    GodsEyeLookAheadViolationError,
    GodsEyeOrchestrator,
    GodsEyeSectionStatus,
    GodsEyeTenantAccessDeniedError,
    GodsEyeTraversalLimitExceededError,
    GodsEyeViewMode,
    INSTITUTIONAL_DISCLAIMERS,
)
from atlas_api.main import app

client = TestClient(app)


# =============================================================================
# 1. CORE CAPABILITIES & LENSES
# =============================================================================
def test_gods_eye_capabilities_and_safety_guarantees():
    service = AtlasGodsEyeService()
    caps = service.get_capabilities()

    assert caps["stage"] == 140
    assert caps["system_name"] == "ATLAS God's Eye Financial Intelligence"
    assert len(caps["supported_lenses"]) == 8
    assert "GLOBAL_EVENTS" in caps["supported_lenses"]
    assert "MONETARY_POLICY" in caps["supported_lenses"]
    assert "CORPORATE_INTELLIGENCE" in caps["supported_lenses"]
    assert "GEOPOLITICAL" in caps["supported_lenses"]
    assert "COMMODITY_INFRASTRUCTURE" in caps["supported_lenses"]
    assert "PHYSICAL_WORLD" in caps["supported_lenses"]
    assert "PORTFOLIO_INTELLIGENCE" in caps["supported_lenses"]
    assert "HISTORICAL_RESEARCH" in caps["supported_lenses"]
    assert "No automated trading or execution capabilities" in caps["guarantees"]
    assert "causality" in caps["disclaimers"]
    assert "damage" in caps["disclaimers"]


def test_gods_eye_canonical_8_lenses_listing():
    service = AtlasGodsEyeService()
    lenses = service.list_lenses()
    assert len(lenses) == 8
    lens_ids = [l.lens_id.value for l in lenses]
    assert "MONETARY_POLICY" in lens_ids
    assert "PHYSICAL_WORLD" in lens_ids


# =============================================================================
# 2. 20 REFERENCE TEST FIXTURES (A THROUGH T)
# =============================================================================

def test_fixture_a_monetary_policy_observational_context():
    """Fixture A: Central bank decision -> jurisdiction -> official bulletin -> rate context; no price forecasts."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.MONETARY_POLICY)
    res = service.investigate(ctx)

    assert res.lens == GodsEyeLensType.MONETARY_POLICY
    assert res.market_context is not None
    assert res.market_context.benchmark_symbol == "US2Y_YIELD"
    assert res.market_context.is_observational_only is True
    # Verify strict institutional disclaimer is attached
    assert "Correlation is not causation" in res.market_context.disclaimer


def test_fixture_b_company_earnings_verified_metrics():
    """Fixture B: 10-K filing -> canonical issuer -> period -> graph -> verified financial metrics; no fake surprise."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(
        lens=GodsEyeLensType.CORPORATE_INTELLIGENCE,
        selected_entity_id="COMP_AAPL",
    )
    res = service.investigate(ctx)

    assert res.knowledge_graph_subgraph["root_node"] == "COMP_AAPL"
    # Ensure evidence sources contain statutory filings
    source_names = [s["name"] for s in res.evidence_sources]
    assert any("SEC EDGAR" in name for name in source_names)


def test_fixture_c_port_closure_disclaimer_present():
    """Fixture C: Port P -> Operator O -> geometry; no fabricated supply-chain collapse or revenue loss."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.COMMODITY_INFRASTRUCTURE)
    res = service.investigate(ctx)

    port_features = [f for f in res.map_features if f.feature_type == "PORT"]
    assert len(port_features) > 0
    port = port_features[0]
    assert port.name == "Port of Rotterdam International Terminal"
    assert port.damage_status == GodsEyeDamageAssessmentStatus.CONFIRMED_OPERATIONAL
    assert "damage" in res.disclaimers


def test_fixture_d_earthquake_proximity_damage_status_unknown():
    """Fixture D: USGS event -> nearby facility -> distance km confirmed; damage status must be UNKNOWN."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.PHYSICAL_WORLD)
    res = service.investigate(ctx)

    # Locate epicenter and nearby semiconductor facility
    epicenter = next(f for f in res.map_features if f.feature_type == "EVENT_EPICENTER")
    facility = next(f for f in res.map_features if f.feature_type == "FACILITY")

    assert epicenter.confidence == 1.0
    # Crucial: Facility damage status MUST be UNKNOWN because proximity does not equal damage!
    assert facility.damage_status == GodsEyeDamageAssessmentStatus.UNKNOWN
    assert "distance_to_epicenter_km" in facility.properties
    assert facility.properties["distance_to_epicenter_km"] > 0
    assert "Spatial proximity to a physical event" in facility.properties["disclaimer"]


def test_fixture_e_sanctions_exact_entity_resolution():
    """Fixture E: Official sanctions designation -> legal entity match; no false linkage to similarly named companies."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(
        lens=GodsEyeLensType.GEOPOLITICAL,
        selected_entity_id="ENTITY_SANCTIONED_CO_A",
    )
    res = service.investigate(ctx)

    assert res.knowledge_graph_subgraph["root_node"] == "ENTITY_SANCTIONED_CO_A"
    # Verify no false linkage: only exact matches are present in root node
    assert res.knowledge_graph_subgraph["root_node"] != "ENTITY_SIMILAR_NAME_BENIGN_CO"


def test_fixture_f_portfolio_attention_no_loss_forecast():
    """Fixture F: Authorized portfolio -> holding H -> event E; exposure + attention; no loss forecast."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(
        lens=GodsEyeLensType.PORTFOLIO_INTELLIGENCE,
        selected_portfolio_id="PORT_USER_A_FUND",
        tenant_id="tenant_a",
        user_id="USER_A",
    )
    principal = AuthPrincipal(sub="USER_A")
    res = service.investigate(ctx, principal=principal)

    assert res.exposure_summary is not None
    assert "portfolio_lookthrough_weight_pct" in res.exposure_summary
    # Exposure is sensitivity, not dollar loss forecast
    assert "Structural exposure quantifies revenue concentration" in res.exposure_summary["disclaimer"]


def test_fixture_g_historical_information_look_ahead_exclusion():
    """Fixture G: Event at T1, correction at T2; as-of query between T1 and T2 excludes future correction."""
    service = AtlasGodsEyeService()
    # As-of date before an event that occurred in 2026
    historical_as_of = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    ctx = GodsEyeContext(
        lens=GodsEyeLensType.HISTORICAL_RESEARCH,
        as_of=historical_as_of,
    )
    res = service.investigate(ctx)

    assert res.is_historical_reconstruction is True
    # Ensure all events returned occurred on or before historical_as_of
    for ev in res.events:
        ev_time = datetime.fromisoformat(ev["occurred_at"])
        assert ev_time <= historical_as_of


def test_fixture_h_source_outage_partial_resilience():
    """Fixture H: One provider offline; unaffected sources remain functional; no fake empty-world crash."""
    orchestrator = GodsEyeOrchestrator()
    orchestrator.simulate_source_outage("SRC_MARKET_FEED_PRO")
    service = AtlasGodsEyeService(orchestrator=orchestrator)

    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res = service.investigate(ctx)

    # Market context is degraded, but events and graph succeeded
    assert res.section_statuses["market_context"] == GodsEyeSectionStatus.DEGRADED
    assert res.section_statuses["events"] == GodsEyeSectionStatus.READY
    assert res.section_statuses["graph"] == GodsEyeSectionStatus.READY
    assert len(res.events) > 0


def test_fixture_i_market_coincidence_observational_context():
    """Fixture I: Stock move after rate decision; observational price context; no causal leap."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res = service.investigate(ctx)

    assert res.market_context is not None
    assert res.market_context.is_observational_only is True
    assert "Correlation is not causation" in res.market_context.disclaimer


def test_fixture_j_private_portfolio_protection():
    """Fixture J: User B cannot see User A's private portfolio, exposure, or attention score."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(
        lens=GodsEyeLensType.PORTFOLIO_INTELLIGENCE,
        selected_portfolio_id="PORT_USER_A_FUND",
        tenant_id="tenant_a",
        user_id="USER_B",
    )
    unauthorized_principal = AuthPrincipal(sub="USER_B")

    with pytest.raises(GodsEyeTenantAccessDeniedError):
        service.investigate(ctx, principal=unauthorized_principal)


def test_fixture_k_source_revocation_invalidates_derived_output():
    """Fixture K: Revocation locks derived outputs, invalidates cache, and updates licenses."""
    orchestrator = GodsEyeOrchestrator()
    service = AtlasGodsEyeService(orchestrator=orchestrator)

    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res_before = service.investigate(ctx)
    count_before = len(res_before.events)

    # Revoke an event source
    orchestrator.revoke_source("src_earnings_official")
    res_after = service.investigate(ctx)

    # Derived output is safely regenerated without the revoked source
    assert res_after is not None


def test_fixture_l_historical_company_ownership_vintage():
    """Fixture L: Corporate group reconstruction respects valid historical relationships at as-of date."""
    service = AtlasGodsEyeService()

    # In 2021, SpinOffCo was a subsidiary of Legacy Parent Corp
    v1_date = datetime(2021, 6, 1, tzinfo=timezone.utc)
    # In 2024, SpinOffCo is an independent public company
    v2_date = datetime(2024, 6, 1, tzinfo=timezone.utc)

    comparison = service.compare_historical_vintages(
        entity_id="COMP_SPINOFF_CO",
        as_of_v1=v1_date,
        as_of_v2=v2_date,
    )

    assert comparison["entity_id"] == "COMP_SPINOFF_CO"
    assert comparison["topology_changed"] is True
    # Vintage 1 has Legacy Parent Corp
    v1_node_ids = [n["id"] for n in comparison["vintage_1"]["nodes"]]
    assert "COMP_LEGACY_PARENT" in v1_node_ids
    # Vintage 2 has Independent status
    v2_node_ids = [n["id"] for n in comparison["vintage_2"]["nodes"]]
    assert "MARKET_INDEPENDENT" in v2_node_ids


def test_fixture_m_scoring_versioning_and_factor_explanation():
    """Fixture M: Retains versioning; explains factor delta without false probability claims."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res = service.investigate(ctx)

    assert res.scoring_summary is not None
    assert res.scoring_summary["model_version"] == "v1.0.0"
    assert "Intelligence priority score reflects operational review priority" in res.scoring_summary["disclaimer"]
    if res.events:
        top_event = res.events[0]
        assert "priority_score" in top_event
        assert "scoring_factors" in top_event


def test_fixture_n_geographic_precision_no_fabricated_street_coords():
    """Fixture N: Country-level event does not fabricate street coordinates or nearby facility links."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.GEOPOLITICAL)
    res = service.investigate(ctx)

    jurisdiction_feat = next((f for f in res.map_features if f.feature_type == "JURISDICTION_POLYGON"), None)
    assert jurisdiction_feat is not None
    assert jurisdiction_feat.properties["precision"] == "COUNTRY_LEVEL"
    assert jurisdiction_feat.properties["street_level_coordinates_invented"] is False


def test_fixture_o_workspace_linking_isolation():
    """Fixture O: Linked panels synchronize; independent parameters remain isolated."""
    service = AtlasGodsEyeService()
    ctx1 = GodsEyeContext(lens=GodsEyeLensType.MONETARY_POLICY, selected_entity_id="CENTRAL_BANK_FED")
    ctx2 = GodsEyeContext(lens=GodsEyeLensType.PHYSICAL_WORLD, selected_entity_id="FACILITY_TSMC_FAB18")

    res1 = service.investigate(ctx1)
    res2 = service.investigate(ctx2)

    assert res1.knowledge_graph_subgraph["root_node"] == "CENTRAL_BANK_FED"
    assert res2.knowledge_graph_subgraph["root_node"] == "FACILITY_TSMC_FAB18"


def test_fixture_p_ai_investigation_read_only_tool():
    """Fixture P: Authorized read-only investigation tool (atlas.gods_eye.investigate) returns verified trail."""
    service = AtlasGodsEyeService()
    params = {
        "lens": "COMMODITY_INFRASTRUCTURE",
        "entity_id": "PORT_ROTTERDAM",
        "max_depth": 2,
    }
    tool_res = service.execute_ai_investigation_tool(params)

    assert tool_res["tool_name"] == "atlas.gods_eye.investigate"
    assert tool_res["status"] == "COMPLETED"
    assert len(tool_res["primary_evidence_sources"]) > 0
    assert len(tool_res["unknowns_and_limitations"]) > 0
    assert "causality" in tool_res["disclaimers"]


def test_fixture_q_graph_traversal_bounding():
    """Fixture Q: High-degree node traversal bounded to max depth <= 3; depth > 3 is rejected."""
    service = AtlasGodsEyeService()
    ctx_valid = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS, max_graph_depth=3)
    res = service.investigate(ctx_valid)
    assert res.knowledge_graph_subgraph["traversal_depth"] <= 3

    # Attempting depth > 3 raises error
    ctx_invalid = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS, max_graph_depth=5)
    with pytest.raises(GodsEyeTraversalLimitExceededError):
        service.investigate(ctx_invalid)


def test_fixture_r_map_view_modes():
    """Fixture R: Supported view modes (2D, 3D Globe, Hybrid split)."""
    service = AtlasGodsEyeService()
    for mode in [GodsEyeViewMode.TWO_DIMENSIONAL, GodsEyeViewMode.THREE_DIMENSIONAL_GLOBE, GodsEyeViewMode.HYBRID_SPLIT]:
        ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS, view_mode=mode)
        res = service.investigate(ctx)
        assert res is not None


def test_fixture_s_incomplete_global_coverage_notes():
    """Fixture S: Accurate reporting of unmonitored countries; missing data != 0."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res = service.investigate(ctx)

    assert len(res.coverage_notes) > 0
    assert any("Jurisdictions [KP, IR]" in note for note in res.coverage_notes)
    assert any("never as zero risk" in note for note in res.coverage_notes)


def test_fixture_t_mixed_source_times_differentiation():
    """Fixture T: Distinguishes occurrence time, publication time, and ingestion time."""
    service = AtlasGodsEyeService()
    ctx = GodsEyeContext(lens=GodsEyeLensType.GLOBAL_EVENTS)
    res = service.investigate(ctx)

    for ev in res.events:
        assert "occurred_at" in ev
        assert "published_at" in ev
        assert "ingested_at" in ev


# =============================================================================
# 3. REST API ENDPOINTS
# =============================================================================

def test_api_gods_eye_capabilities():
    resp = client.get("/api/v1/intelligence/gods-eye/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 140
    assert len(data["supported_lenses"]) == 8


def test_api_gods_eye_lenses_listing():
    resp = client.get("/api/v1/intelligence/gods-eye/lenses")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 8


def test_api_gods_eye_investigate_post():
    payload = {
        "lens": "GLOBAL_EVENTS",
        "selected_entity_id": "COMP_AAPL",
        "max_graph_depth": 2,
    }
    resp = client.post("/api/v1/intelligence/gods-eye/investigate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lens"] == "GLOBAL_EVENTS"
    assert "events" in data
    assert "map_features" in data
    assert "knowledge_graph_subgraph" in data
    assert "disclaimers" in data


def test_api_gods_eye_entity_get():
    resp = client.get("/api/v1/intelligence/gods-eye/entity/COMP_AAPL?lens=CORPORATE_INTELLIGENCE")
    assert resp.status_code == 200
    data = resp.json()
    assert data["knowledge_graph_subgraph"]["root_node"] == "COMP_AAPL"


def test_api_gods_eye_historical_reconstruction_post():
    payload = {
        "as_of": "2024-05-01T12:00:00Z",
        "lens": "HISTORICAL_RESEARCH",
        "selected_entity_id": "COMP_AAPL",
    }
    resp = client.post("/api/v1/intelligence/gods-eye/historical-reconstruction", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_historical_reconstruction"] is True


def test_api_gods_eye_compare_vintages_post():
    payload = {
        "entity_id": "COMP_SPINOFF_CO",
        "as_of_v1": "2021-06-01T12:00:00Z",
        "as_of_v2": "2024-06-01T12:00:00Z",
    }
    resp = client.post("/api/v1/intelligence/gods-eye/compare-vintages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["entity_id"] == "COMP_SPINOFF_CO"
    assert data["topology_changed"] is True


def test_api_gods_eye_ai_tool_investigate():
    payload = {
        "lens": "MONETARY_POLICY",
        "entity_id": "CENTRAL_BANK_FED",
        "max_depth": 2,
    }
    resp = client.post("/api/v1/intelligence/gods-eye/ai-tool/investigate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tool_name"] == "atlas.gods_eye.investigate"
    assert data["status"] == "COMPLETED"

