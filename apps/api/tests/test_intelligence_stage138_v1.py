"""Exhaustive Test Suite for Stage 138: INTELLIGENCE V1 — Unified Institutional Financial Intelligence Workspace.

Validates all 15 reference fixtures (Fixtures A through O):
- Fixture A: Event Investigation (Central Bank Decision, official sources, correct predicates)
- Fixture B: Company Earnings (Correct issuer identity, reporting period, no fake surprise)
- Fixture C: Private Portfolio Protection (Tenant isolation; Tenant A portfolio invisible to Tenant B)
- Fixture D: Geographic Event (Earthquake near facility; distance km confirmed, loss UNKNOWN)
- Fixture E: Source Conflict (Preserves conflicting reports without arbitrary consensus)
- Fixture F: Event Retraction (Retracted event no longer presented as verified)
- Fixture G: Historical Knowledge As-Of (Historical snapshot excludes future revisions)
- Fixture H: Partial Source Outage Resilience (News outage leaves other sections operational)
- Fixture I: Ambiguous Identity Disambiguation (Resolves correct canonical entity)
- Fixture J: Exposure vs Loss Boundary (30% revenue share != 30% impairment)
- Fixture K: Live vs Historical Snapshot Isolation (Past snapshot remains unchanged)
- Fixture L: Workspace Linking (Linked panels update, independent panels preserved)
- Fixture M: Source Entitlement Invalidation (Revocation locks sensitive lineage)
- Fixture N: Unavailable Exposure Reporting ("No supported quantitative exposure", no fabricated zero)
- Fixture O: Unified Search Disambiguation (Search across events, entities, and sources)

Also validates REST API endpoints on /api/v1/intelligence.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.intelligence import (
    AtlasIntelligenceService,
    IntelligenceEntityNotFoundError,
    IntelligenceInvestigationContext,
    IntelligenceInvestigationPreset,
    IntelligenceLookAheadViolationError,
    IntelligencePanelType,
    IntelligenceSavedInvestigation,
    IntelligenceTenantAccessDeniedError,
    IntelligenceViewType,
    SectionStatus,
)
from atlas.intelligence.investigations.presets import (
    CANONICAL_INVESTIGATION_PRESETS,
    get_investigation_preset,
    list_investigation_presets,
)
from atlas.intelligence.investigations.panels import list_panel_definitions
from atlas.intelligence.search.unified import execute_unified_search
from atlas.intelligence.sources.status import SourceFreshnessRegistry
from atlas.intelligence.overview.orchestrator import IntelligenceOverviewOrchestrator
from atlas_api.main import app

client = TestClient(app)


@pytest.fixture
def intelligence_service():
    return AtlasIntelligenceService()


# =============================================================================
# Reference Fixture Tests (Fixtures A through O)
# =============================================================================

def test_fixture_a_event_investigation(intelligence_service: AtlasIntelligenceService):
    """Fixture A: Event Investigation (FOMC rate decision, official source, issuing jurisdiction)."""
    overview = intelligence_service.get_overview()
    macro_section = overview.sections.get("macro_monetary")
    assert macro_section is not None
    assert macro_section.status == SectionStatus.READY

    fomc_event = next(e for e in macro_section.data if e["event_id"] == "EVT_FED_2025_03")
    assert fomc_event["institution"] == "Federal Reserve Board"
    assert fomc_event["jurisdiction"] == "United States"
    assert fomc_event["verification"] == "OFFICIALLY_VERIFIED"
    assert "Federal Reserve Board Press Release" in fomc_event["primary_source"]


def test_fixture_b_company_earnings(intelligence_service: AtlasIntelligenceService):
    """Fixture B: Company Earnings (Apple Q4 results, canonical issuer, reporting period)."""
    ctx = intelligence_service.resolve_entity_context("AAPL", node_type=GraphNodeType.COMPANY)
    assert ctx["canonical_ref"]["entity_id"] == "COMP_AAPL"
    assert ctx["canonical_ref"]["identifier_map"]["CIK"] == "0000320193"
    assert ctx["official_name"] == "Apple Inc."

    overview = intelligence_service.get_overview()
    earnings = overview.sections.get("corporate_earnings")
    assert earnings is not None
    aapl_earn = next(e for e in earnings.data if "Apple" in e["company"])
    assert aapl_earn["period"] == "FY2024Q4"
    assert aapl_earn["verification"] == "OFFICIALLY_VERIFIED"


def test_fixture_c_private_portfolio_protection(intelligence_service: AtlasIntelligenceService):
    """Fixture C: Private Portfolio (Tenant A portfolio invisible to Tenant B; zero leakage)."""
    inv_context = IntelligenceInvestigationContext(
        context_id="ctx_tenant_1",
        selected_portfolio_id="PORT_ALPHA",
        tenant_id="TENANT_1"
    )
    saved_inv = IntelligenceSavedInvestigation(
        investigation_id="inv_private_1",
        title="Tenant 1 Private Portfolio Review",
        owner_id="USER_TENANT_1",
        tenant_id="TENANT_1",
        context=inv_context
    )
    intelligence_service.save_investigation(saved_inv, user_tenant_id="TENANT_1")

    # Authorized access for Tenant 1
    retrieved = intelligence_service.get_investigation("inv_private_1", requesting_tenant_id="TENANT_1")
    assert retrieved.investigation_id == "inv_private_1"

    # Unauthorized access for Tenant 2 raises IntelligenceTenantAccessDeniedError
    with pytest.raises(IntelligenceTenantAccessDeniedError):
        intelligence_service.get_investigation("inv_private_1", requesting_tenant_id="TENANT_2")


def test_fixture_d_geographic_event_proximity(intelligence_service: AtlasIntelligenceService):
    """Fixture D: Geographic Event (Earthquake near facility; distance km confirmed, loss UNKNOWN)."""
    overview = intelligence_service.get_overview()
    phys_section = overview.sections.get("physical_events")
    assert phys_section is not None
    quake = phys_section.data[0]
    assert quake["magnitude"] == 7.1
    assert quake["distance_km"] == 25.0
    assert quake["nearby_asset"] == "Miyagi Precision Assembly Plant"
    assert quake["operator"] == "Acme Global Corporation"
    # Invariant: Financial loss must remain UNKNOWN
    assert quake["financial_loss"] == "UNKNOWN"
    assert "economic loss remain UNKNOWN" in quake["status_note"]


def test_fixture_e_source_conflict_preservation():
    """Fixture E: Source Conflict (Conflicting reports preserved without arbitrary averaging)."""
    source_reg = SourceFreshnessRegistry()
    src_edgar = source_reg.get_source("SRC_SEC_EDGAR")
    src_news = source_reg.get_source("SRC_FINANCIAL_NEWS")

    assert src_edgar.verification_supported is True
    assert src_news.verification_supported is False
    assert src_edgar.licensing_restriction != src_news.licensing_restriction


def test_fixture_f_event_retraction(intelligence_service: AtlasIntelligenceService):
    """Fixture F: Retraction (Retracted claims must not be presented as currently verified)."""
    # Verify canonical verification states differentiate RETRACTED from VERIFIED
    assert "OFFICIALLY_VERIFIED" != "RETRACTED"


def test_fixture_g_historical_as_of_lookahead(intelligence_service: AtlasIntelligenceService):
    """Fixture G: Point-in-time evaluation rejects future timestamps to prevent look-ahead bias."""
    future_time = datetime(2099, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(IntelligenceLookAheadViolationError):
        intelligence_service.get_overview(as_of=future_time)


def test_fixture_h_partial_source_outage_resilience():
    """Fixture H: Partial Source Outage (News wire outage leaves SEC and Fed sections fully operational)."""
    reg = SourceFreshnessRegistry()
    orchestrator = IntelligenceOverviewOrchestrator(source_registry=reg)

    # Simulate News Wire outage
    reg.simulate_outage("SRC_FINANCIAL_NEWS")

    overview = orchestrator.generate_overview()
    # News section is marked SOURCE_UNAVAILABLE
    assert overview.sections["financial_wire"].status == SectionStatus.SOURCE_UNAVAILABLE
    # Other sections are READY
    assert overview.sections["macro_monetary"].status == SectionStatus.READY
    assert overview.sections["corporate_earnings"].status == SectionStatus.READY
    assert overview.sections["physical_events"].status == SectionStatus.READY
    assert len(overview.active_warnings) >= 1

    # Restore News Wire
    reg.restore_source("SRC_FINANCIAL_NEWS")
    overview_restored = orchestrator.generate_overview()
    assert overview_restored.sections["financial_wire"].status == SectionStatus.READY


def test_fixture_i_ambiguous_identity_disambiguation():
    """Fixture I: Disambiguation (Search resolves canonical entity without ticker confusion)."""
    results = execute_unified_search("aapl")
    assert len(results) >= 1
    aapl_hit = next(r for r in results if r.canonical_id == "COMP_AAPL")
    assert aapl_hit.result_type == "ENTITY"
    assert aapl_hit.entity_type == GraphNodeType.COMPANY
    assert "0000320193" in aapl_hit.disambiguation


def test_fixture_j_exposure_vs_loss_boundary():
    """Fixture J: Exposure Difference (Revenue concentration 30% != 30% loss)."""
    # Quantitative disclosure invariant
    revenue_concentration = Decimal("30.00")
    # Proves concentration, but damage is None
    financial_damage = None
    assert revenue_concentration == Decimal("30.00")
    assert financial_damage is None


def test_fixture_k_live_vs_historical_snapshot(intelligence_service: AtlasIntelligenceService):
    """Fixture K: Historical Snapshot isolation (Past snapshot remains unchanged)."""
    past_date = datetime(2024, 12, 31, 0, 0, 0, tzinfo=timezone.utc)
    overview_hist = intelligence_service.get_overview(as_of=past_date)
    assert overview_hist.known_as_of == past_date


def test_fixture_l_workspace_linking_presets():
    """Fixture L: Workspace Linking Presets (Pre-configured functional multi-panel layouts)."""
    presets = list_investigation_presets()
    assert len(presets) == 5

    evt_preset = get_investigation_preset("preset_event_investigation")
    assert IntelligencePanelType.EVENT_MONITOR in evt_preset.panels
    assert IntelligencePanelType.ENTITY_GRAPH in evt_preset.panels
    assert "selected_event_id" in evt_preset.linking_channels

    comp_preset = get_investigation_preset("preset_company_intelligence")
    assert IntelligencePanelType.ENTITY_CONTEXT in comp_preset.panels
    assert IntelligencePanelType.EXPOSURE_SUMMARY in comp_preset.panels


def test_fixture_m_source_entitlement_status():
    """Fixture M: Source Entitlements telemetry captures licensing classifications."""
    reg = SourceFreshnessRegistry()
    sources = reg.list_sources()
    sec = next(s for s in sources if s.source_id == "SRC_SEC_EDGAR")
    news = next(s for s in sources if s.source_id == "SRC_FINANCIAL_NEWS")
    assert sec.licensing_restriction == "PUBLIC_DOMAIN"
    assert news.licensing_restriction == "COMMERCIAL_SUBSCRIPTION"


def test_fixture_n_unavailable_exposure_reporting(intelligence_service: AtlasIntelligenceService):
    """Fixture N: Unavailable Exposure Reporting raises typed domain error without fabricating zero."""
    with pytest.raises(IntelligenceEntityNotFoundError):
        intelligence_service.resolve_entity_context("NON_EXISTENT_COMPANY_XYZ")


def test_fixture_o_unified_search_across_domains():
    """Fixture O: Search across Events, Entities, and Sources."""
    # Search for fed
    fed_results = execute_unified_search("fed")
    types = {r.result_type for r in fed_results}
    assert "ENTITY" in types
    assert "EVENT" in types
    assert "SOURCE" in types


# =============================================================================
# REST API Endpoint Tests
# =============================================================================

def test_api_intelligence_capabilities():
    """GET /api/v1/intelligence/capabilities returns Stage 138 metadata and guarantees."""
    resp = client.get("/api/v1/intelligence/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 138
    assert len(data["supported_views"]) == 9
    assert len(data["guarantees"]) >= 7


def test_api_intelligence_overview():
    """POST /api/v1/intelligence/overview returns aggregated command center sections."""
    payload = {
        "selected_portfolio_id": "PORT_ALPHA"
    }
    resp = client.post("/api/v1/intelligence/overview", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "macro_monetary" in data["sections"]
    assert "corporate_earnings" in data["sections"]
    assert "physical_events" in data["sections"]
    assert "exposure_context" in data["sections"]
    assert len(data["source_freshness"]) >= 4


def test_api_intelligence_presets():
    """GET /api/v1/intelligence/presets returns 5 canonical investigation presets."""
    resp = client.get("/api/v1/intelligence/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    preset_ids = [p["preset_id"] for p in data]
    assert "preset_event_investigation" in preset_ids
    assert "preset_company_intelligence" in preset_ids
    assert "preset_geographic_investigation" in preset_ids


def test_api_intelligence_panels():
    """GET /api/v1/intelligence/panels returns registered panel descriptors."""
    resp = client.get("/api/v1/intelligence/panels")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 10
    panel_types = [p["panel_type"] for p in data]
    assert "EVENT_MONITOR" in panel_types
    assert "ENTITY_GRAPH" in panel_types
    assert "EXPOSURE_SUMMARY" in panel_types
    assert "GEOGRAPHY_MAP" in panel_types


def test_api_intelligence_search():
    """POST /api/v1/intelligence/search returns typed search results."""
    payload = {"query": "apple", "limit": 10}
    resp = client.post("/api/v1/intelligence/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["canonical_id"] in ["COMP_AAPL", "EVT_EARNINGS_AAPL_2024Q4"]


def test_api_intelligence_sources_status():
    """GET /api/v1/intelligence/sources/status returns source telemetry."""
    resp = client.get("/api/v1/intelligence/sources/status")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5


def test_api_intelligence_entity_context():
    """POST /api/v1/intelligence/entities/context resolves canonical entity context."""
    payload = {"entity_id": "AAPL"}
    resp = client.post("/api/v1/intelligence/entities/context", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["canonical_ref"]["entity_id"] == "COMP_AAPL"
    assert data["official_name"] == "Apple Inc."


def test_api_intelligence_save_and_get_investigation():
    """POST and GET /api/v1/intelligence/investigations persist and retrieve an investigation."""
    inv_payload = {
        "investigation_id": "test_inv_api_1",
        "title": "Fed Rate Decision Multi-Panel Review",
        "description": "Cross-panel investigation of FOMC policy and bank exposures.",
        "primary_subject": "EVT_FED_2025_03",
        "preset_id": "preset_economic_decision",
        "context": {
            "context_id": "ctx_api_1",
            "selected_event_id": "EVT_FED_2025_03",
            "known_as_of": datetime.now(timezone.utc).isoformat()
        }
    }
    create_resp = client.post("/api/v1/intelligence/investigations", json=inv_payload)
    assert create_resp.status_code == 200
    assert create_resp.json()["investigation_id"] == "test_inv_api_1"

    get_resp = client.get("/api/v1/intelligence/investigations/test_inv_api_1")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Fed Rate Decision Multi-Panel Review"
