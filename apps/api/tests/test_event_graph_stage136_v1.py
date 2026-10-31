"""Exhaustive Test Suite for Stage 136: Event-to-Entity Knowledge Graph & Relationship Intelligence Engine.

Validates all 20 institutional fixtures (Fixtures A through T):
- Fixture A: Earnings Issuer Linking (ANNOUNCED_BY, no security explosion)
- Fixture B: Multiple Share Classes (issuer event does not fabricate distinct equity class edges)
- Fixture C: Sanctions Exact Match / Collision Avoidance (innocent firms excluded)
- Fixture D: Central Bank Decision (DECIDED_BY, HAS_ISSUING_JURISDICTION)
- Fixture E: Economic Indicator Series (RELEASES_INDICATOR, statistical agency)
- Fixture F: Corporate Action Roles (Acquirer vs Target vs Regulator)
- Fixture G: Multi-Hop Subsidiary to Parent (Event -> Sub -> Parent without false relabeling)
- Fixture H: Earthquake Proximity (GEOGRAPHICALLY_NEAR with distance km, strictly NO DAMAGED edge)
- Fixture I: Geographic Precision / Missing Coordinate Protection (country-level event has no asset proximity)
- Fixture J: Commodity Mention (references Crude Oil without linking all derivatives)
- Fixture K: Historical Ownership (2022 query reflects 2022 parent, not changed 2024 status)
- Fixture L: Knowledge As-Of (T1 query excludes T2 amendment)
- Fixture M: Multi-Source Evidence Corroboration (1 logical edge, 3 evidence records)
- Fixture N: Disputed / Conflicting Identity (conflicting sources recorded under CONFLICTED status)
- Fixture O: Revoked Data Source (license loss revokes edge and invalidates query)
- Fixture P: Multi-Tenant Private Graph (Tenant A private edge invisible to Tenant B)
- Fixture Q: Graph Cycle Detection and Prevention (cross-holding cycle terminates cleanly)
- Fixture R: Stage 135 Event Retraction (dependent edges invalidated non-destructively)
- Fixture S: Reused Ticker Disambiguation (resolves correct entity valid at event epoch)
- Fixture T: Factual Path Explanation (Event -> Asset -> Operator with zero speculative loss claims)

Also verifies prohibited predicate protection, maximum traversal depth enforcement,
and all FastAPI REST endpoints under /api/v1/knowledge-graph.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from atlas.event_graph import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    EventEntityKnowledgeGraphService,
    GraphNodeType,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from atlas.event_graph.errors import (
    IdentityResolutionError,
    NodeNotFoundError,
    ProhibitedPredicateError,
    RelationshipNotFoundError,
    TenantAccessDeniedError,
    TraversalDepthExceededError,
)
from atlas.event_graph.predicates.registry import validate_predicate_allowed
from atlas_api.main import app

client = TestClient(app)


@pytest.fixture
def graph_service():
    """Initializes a fresh knowledge graph service populated with canonical fixtures."""
    return EventEntityKnowledgeGraphService(populate_seed_data=True)


# =============================================================================
# Domain & Fixture Tests (Fixtures A through T)
# =============================================================================

def test_fixture_a_earnings_issuer_linking(graph_service: EventEntityKnowledgeGraphService):
    """Fixture A: Event links to Apple Inc. as issuer with primary instrument, without security explosion."""
    neighbors = graph_service.get_event_neighbors("EVT-EARNINGS-AAPL-2024Q3")
    target_ids = {r.target_node.entity_id for r in neighbors}
    predicates = {r.predicate for r in neighbors}

    assert "COMP-AAPL" in target_ids
    assert "INSTR-AAPL-US" in target_ids
    assert PredicateType.ANNOUNCED_BY in predicates
    assert PredicateType.CONCERNS_INSTRUMENT in predicates
    # Verify no random unmentioned instruments or options
    assert len(neighbors) == 3  # Company, Instrument, Country


def test_fixture_b_multiple_share_classes(graph_service: EventEntityKnowledgeGraphService):
    """Fixture B: Issuer-level governance event links to Alphabet, not individual share classes (GOOG vs GOOGL)."""
    neighbors = graph_service.get_event_neighbors("EVT-CORP-GOOGL-GOV")
    target_ids = {r.target_node.entity_id for r in neighbors}

    assert "COMP-GOOGL" in target_ids
    assert "INSTR-GOOGL-A" not in target_ids
    assert "INSTR-GOOG-C" not in target_ids


def test_fixture_c_sanctions_exact_match(graph_service: EventEntityKnowledgeGraphService):
    """Fixture C: Sanction designation matches exact Volga Russian entity; innocent UK company excluded."""
    neighbors = graph_service.get_event_neighbors("EVT-SANCTION-VOLGA-PETRO")
    target_ids = {r.target_node.entity_id for r in neighbors}

    assert "LEGAL-VOLGA-PETRO-RU" in target_ids
    assert "REG-OFAC" in target_ids
    assert "COMP-VOLGA-PETRO-UK" not in target_ids  # Zero fuzzy false positives!

    # Direct resolution exact check
    with pytest.raises(IdentityResolutionError):
        graph_service.resolve_entity("Volga Petroleum Retail", require_exact=True)


def test_fixture_d_central_bank_decision(graph_service: EventEntityKnowledgeGraphService):
    """Fixture D: Rate decision links to Federal Reserve (DECIDED_BY) and US (HAS_ISSUING_JURISDICTION)."""
    neighbors = graph_service.get_event_neighbors("EVT-FOMC-20230726")
    pred_map = {r.predicate: r.target_node.entity_id for r in neighbors}

    assert pred_map[PredicateType.DECIDED_BY] == "CB-FRB"
    assert pred_map[PredicateType.HAS_ISSUING_JURISDICTION] == "COUNTRY-US"


def test_fixture_e_economic_indicator(graph_service: EventEntityKnowledgeGraphService):
    """Fixture E: CPI release links to US CPI indicator and BLS statistical agency."""
    neighbors = graph_service.get_event_neighbors("EVT-CPI-US-202406")
    pred_map = {r.predicate: r.target_node.entity_id for r in neighbors}

    assert pred_map[PredicateType.RELEASES_INDICATOR] == "IND-CPI-US"
    assert pred_map[PredicateType.ANNOUNCED_BY] == "AGENCY-BLS"


def test_fixture_f_corporate_action_roles(graph_service: EventEntityKnowledgeGraphService):
    """Fixture F: Merger event separates Acquirer (Microsoft), Target (Activision), and Regulator (FTC)."""
    neighbors = graph_service.get_event_neighbors("EVT-MERGER-MSFT-ATVI")
    role_map = {r.relationship_role: r.target_node.entity_id for r in neighbors}

    assert role_map["ACQUIRER"] == "COMP-MSFT"
    assert role_map["TARGET"] == "COMP-ATVI"
    assert role_map["REVIEWING_REGULATOR"] == "REG-FTC"


def test_fixture_g_subsidiary_to_parent_multihop(graph_service: EventEntityKnowledgeGraphService):
    """Fixture G: Gemini launch announced by DeepMind, which links structurally to Alphabet.
    Alphabet is reachable via 2 hops but is NOT falsely relabeled as direct announcer.
    """
    direct_neighbors = graph_service.get_event_neighbors("EVT-PRODUCT-DEEPMIND-GEMINI")
    direct_targets = {r.target_node.entity_id for r in direct_neighbors}
    assert "LEGAL-DEEPMIND-UK" in direct_targets
    assert "COMP-GOOGL" not in direct_targets

    # Multi-hop path discovery
    paths = graph_service.find_paths(
        source_node_type=GraphNodeType.EVENT,
        source_id="EVT-PRODUCT-DEEPMIND-GEMINI",
        target_node_type=GraphNodeType.COMPANY,
        target_id="COMP-GOOGL",
        max_depth=3,
    )
    assert len(paths) >= 1
    assert paths[0].total_hops == 2
    assert paths[0].hops[0].to_node.entity_id == "LEGAL-DEEPMIND-UK"
    assert paths[0].hops[1].to_node.entity_id == "COMP-GOOGL"
    assert paths[0].hops[1].predicate == PredicateType.SUBSIDIARY_OF


def test_fixture_h_earthquake_proximity(graph_service: EventEntityKnowledgeGraphService):
    """Fixture H: Sendai earthquake links to Onagawa NPP via GEOGRAPHICALLY_NEAR; strictly NO DAMAGED predicate."""
    neighbors = graph_service.get_event_neighbors("EVT-QUAKE-SENDAI-2024")
    near_rels = [r for r in neighbors if r.predicate == PredicateType.GEOGRAPHICALLY_NEAR]

    assert len(near_rels) >= 1
    rel = near_rels[0]
    assert rel.target_node.entity_id == "INFRA-ONAGAWA-NPP"
    assert rel.proximity_metadata is not None
    assert "distance_km" in rel.proximity_metadata
    assert rel.proximity_metadata["distance_km"] < 100.0
    # Strict invariant: No causal damage predicate
    predicates = [r.predicate.value for r in neighbors]
    assert "DAMAGED" not in predicates
    assert "AFFECTS" not in predicates


def test_fixture_i_geographic_precision_protection(graph_service: EventEntityKnowledgeGraphService):
    """Fixture I: Country-level German tax event does not fabricate asset proximity."""
    neighbors = graph_service.get_event_neighbors("EVT-TAX-DE-2024")
    near_rels = [r for r in neighbors if r.predicate == PredicateType.GEOGRAPHICALLY_NEAR]
    assert len(near_rels) == 0  # No coordinates -> No proximity fabricated!


def test_fixture_j_commodity_mention(graph_service: EventEntityKnowledgeGraphService):
    """Fixture J: OPEC+ output event links to Brent Crude without linking all oil companies."""
    neighbors = graph_service.get_event_neighbors("EVT-OPEC-2024Q2")
    commodities = [r for r in neighbors if r.predicate == PredicateType.REFERENCES_COMMODITY]
    assert len(commodities) == 1
    assert commodities[0].target_node.entity_id == "COMM-BRENT-CRUDE"


def test_fixture_k_historical_ownership_asof(graph_service: EventEntityKnowledgeGraphService):
    """Fixture K: ARM was 100% subsidiary of SoftBank in 2022; querying as-of 2022 returns SoftBank."""
    as_of_2022 = datetime(2022, 6, 1, tzinfo=timezone.utc)
    paths = graph_service.find_paths(
        source_node_type=GraphNodeType.COMPANY,
        source_id="COMP-ARM",
        target_node_type=GraphNodeType.COMPANY,
        target_id="COMP-SOFTBANK",
        max_depth=2,
        as_of=as_of_2022,
    )
    assert len(paths) >= 1
    assert paths[0].hops[0].predicate == PredicateType.SUBSIDIARY_OF

    # Querying after expiration (2024) excludes this historical exclusive subsidiary edge
    as_of_2024 = datetime(2024, 6, 1, tzinfo=timezone.utc)
    paths_2024 = graph_service.find_paths(
        source_node_type=GraphNodeType.COMPANY,
        source_id="COMP-ARM",
        target_node_type=GraphNodeType.COMPANY,
        target_id="COMP-SOFTBANK",
        max_depth=2,
        as_of=as_of_2024,
    )
    assert len(paths_2024) == 0


def test_fixture_l_knowledge_asof_zero_lookahead(graph_service: EventEntityKnowledgeGraphService):
    """Fixture L: Knowledge horizon at T1 excludes T2 amendment."""
    t1 = datetime(2024, 1, 11, 0, 0, tzinfo=timezone.utc)
    neighbors_t1 = graph_service.get_event_neighbors("EVT-FILING-TESLA-SEC", as_of=t1)
    target_ids_t1 = {r.target_node.entity_id for r in neighbors_t1}

    # At T1, only FTC regulator edge is known
    assert "REG-FTC" in target_ids_t1
    assert "COMP-AAPL" not in target_ids_t1

    # At T2 in future, Apple amendment edge is visible
    t2 = datetime(2024, 1, 16, 0, 0, tzinfo=timezone.utc)
    neighbors_t2 = graph_service.get_event_neighbors("EVT-FILING-TESLA-SEC", as_of=t2)
    target_ids_t2 = {r.target_node.entity_id for r in neighbors_t2}
    assert "COMP-AAPL" in target_ids_t2


def test_fixture_m_multisource_corroboration(graph_service: EventEntityKnowledgeGraphService):
    """Fixture M: 1 logical edge to TSMC backed by 3 distinct evidence records."""
    neighbors = graph_service.get_event_neighbors("EVT-TSMC-AZ-FAB")
    tsmc_rel = [r for r in neighbors if r.target_node.entity_id == "COMP-TSMC"][0]
    assert len(tsmc_rel.evidence_ids) == 3
    assert "EVID-TSMC-6K-202409" in tsmc_rel.evidence_ids
    assert "EVID-NIKKEI-DISPATCH" in tsmc_rel.evidence_ids


def test_fixture_n_conflicted_rumor_review_queue(graph_service: EventEntityKnowledgeGraphService):
    """Fixture N: Disputed takeover rumor is marked CONFLICTED or CANDIDATE and added to review queue."""
    neighbors = graph_service.get_event_neighbors("EVT-RUMOR-EU-UTIL")
    assert len(neighbors) >= 1
    assert any(r.verification_status in [RelationshipVerificationStatus.CANDIDATE, RelationshipVerificationStatus.CONFLICTED] for r in neighbors)

    queue = graph_service.get_review_queue()
    assert len(queue) >= 1
    queue_event_ids = {item["event_id"] for item in queue}
    assert "EVT-RUMOR-EU-UTIL" in queue_event_ids


def test_fixture_o_revoked_source_edge_exclusion(graph_service: EventEntityKnowledgeGraphService):
    """Fixture O: Revoked edge is omitted from standard query."""
    neighbors = graph_service.get_event_neighbors("EVT-LEAK-DEFENSE")
    assert len(neighbors) == 0  # Edge was revoked


def test_fixture_p_multitenant_isolation(graph_service: EventEntityKnowledgeGraphService):
    """Fixture P: Tenant Alpha private note is hidden from Tenant Beta."""
    # Query with Tenant Alpha
    alpha_rels = graph_service.get_event_neighbors("EVT-TENANT-ALPHA-NOTE", tenant_id="tenant-alpha-fund")
    assert len(alpha_rels) >= 1

    # Query with Tenant Beta
    beta_rels = graph_service.get_event_neighbors("EVT-TENANT-ALPHA-NOTE", tenant_id="tenant-beta-pension")
    assert len(beta_rels) == 0

    # Query without tenant
    anon_rels = graph_service.get_event_neighbors("EVT-TENANT-ALPHA-NOTE", tenant_id=None)
    assert len(anon_rels) == 0


def test_fixture_q_cycle_detection(graph_service: EventEntityKnowledgeGraphService):
    """Fixture Q: Cross-holding cycle between Alpha Corp and Beta Corp terminates safely without infinite loop."""
    paths = graph_service.find_paths(
        source_node_type=GraphNodeType.COMPANY,
        source_id="COMP-CYCLE-X",
        target_node_type=GraphNodeType.COMPANY,
        target_id="COMP-CYCLE-Y",
        max_depth=3,
    )
    assert len(paths) >= 1
    # Path should have exactly 1 hop (X -> Y) and not infinite loops
    assert paths[0].total_hops == 1


def test_fixture_r_event_retraction(graph_service: EventEntityKnowledgeGraphService):
    """Fixture R: Stage 135 event retraction revokes all dependent graph edges."""
    neighbors = graph_service.get_event_neighbors("EVT-RETRACTED-TSUNAMI-FALSE")
    assert len(neighbors) == 0  # Inactive because retracted


def test_fixture_s_reused_ticker_disambiguation(graph_service: EventEntityKnowledgeGraphService):
    """Fixture S: Reused ticker 'META' resolves to Meta Financial Group in 2020 and Meta Platforms in 2023."""
    as_of_2020 = datetime(2020, 5, 1, tzinfo=timezone.utc)
    node_2020 = graph_service.resolve_entity("META", id_type="TICKER", as_of=as_of_2020)
    assert node_2020.entity_id == "COMP-META-FINANCIAL"

    as_of_2023 = datetime(2023, 5, 1, tzinfo=timezone.utc)
    node_2023 = graph_service.resolve_entity("META", id_type="TICKER", as_of=as_of_2023)
    assert node_2023.entity_id == "COMP-META-PLATFORMS"


def test_fixture_t_path_explanation(graph_service: EventEntityKnowledgeGraphService):
    """Fixture T: Path explanation explains Colonial Pipeline outage to operator with zero loss claims."""
    paths = graph_service.find_paths(
        source_node_type=GraphNodeType.EVENT,
        source_id="EVT-PIPELINE-OUTAGE-COLONIAL",
        target_node_type=GraphNodeType.COMPANY,
        target_id="COMP-COLONIAL-PIPELINE-CO",
        max_depth=3,
    )
    assert len(paths) >= 1
    explanation = paths[0].factual_explanation
    assert "Colonial Pipeline" in explanation
    assert "OPERATED_BY" in explanation or "DIRECT_SUBJECT" in explanation
    # Strict invariant: No financial loss claim
    assert "loss" not in explanation.lower() or "no economic exposure" in explanation.lower()


# =============================================================================
# Boundary and Error Tests
# =============================================================================

def test_prohibited_predicates():
    """Attempting to use prohibited predicates (e.g. AFFECTS, DAMAGED) raises ProhibitedPredicateError."""
    with pytest.raises(ProhibitedPredicateError):
        validate_predicate_allowed("AFFECTS", GraphNodeType.EVENT, GraphNodeType.COMPANY)

    with pytest.raises(ProhibitedPredicateError):
        validate_predicate_allowed("DAMAGED", GraphNodeType.EVENT, GraphNodeType.INFRASTRUCTURE_ASSET)


def test_traversal_depth_exceeded(graph_service: EventEntityKnowledgeGraphService):
    """Requesting traversal depth > 5 raises TraversalDepthExceededError."""
    with pytest.raises(TraversalDepthExceededError):
        graph_service.find_paths(
            source_node_type=GraphNodeType.EVENT,
            source_id="EVT-EARNINGS-AAPL-2024Q3",
            target_node_type=GraphNodeType.COMPANY,
            target_id="COMP-AAPL",
            max_depth=6,
        )


# =============================================================================
# REST API Endpoint Tests (/api/v1/knowledge-graph)
# =============================================================================

def test_api_capabilities():
    """GET /api/v1/knowledge-graph/capabilities returns subsystem boundaries."""
    resp = client.get("/api/v1/knowledge-graph/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == "136"
    assert "EVENT" in data["supported_node_types"]
    assert "AFFECTS" in data["prohibited_predicates"]


def test_api_node_types_and_predicates():
    """GET /api/v1/knowledge-graph/node-types and /predicates."""
    resp_nt = client.get("/api/v1/knowledge-graph/node-types")
    assert resp_nt.status_code == 200
    assert len(resp_nt.json()["node_types"]) >= 10

    resp_p = client.get("/api/v1/knowledge-graph/predicates")
    assert resp_p.status_code == 200
    assert "approved_predicates" in resp_p.json()


def test_api_resolve_entity():
    """POST /api/v1/knowledge-graph/resolve-entity resolves ticker and LEI."""
    resp = client.post(
        "/api/v1/knowledge-graph/resolve-entity",
        json={"identifier": "AAPL", "id_type": "TICKER"},
    )
    assert resp.status_code == 200
    assert resp.json()["entity_id"] == "COMP-AAPL"


def test_api_event_neighbors_and_entity_events():
    """GET /events/{id}/neighbors and /entities/{type}/{id}/events."""
    resp_neighbors = client.get("/api/v1/knowledge-graph/events/EVT-EARNINGS-AAPL-2024Q3/neighbors")
    assert resp_neighbors.status_code == 200
    assert len(resp_neighbors.json()) >= 1

    resp_events = client.get("/api/v1/knowledge-graph/entities/COMPANY/COMP-AAPL/events")
    assert resp_events.status_code == 200
    assert len(resp_events.json()) >= 1


def test_api_paths_and_neighborhood():
    """POST /api/v1/knowledge-graph/paths and /neighborhood."""
    resp_paths = client.post(
        "/api/v1/knowledge-graph/paths",
        json={
            "source_node_type": "EVENT",
            "source_id": "EVT-PRODUCT-DEEPMIND-GEMINI",
            "target_node_type": "COMPANY",
            "target_id": "COMP-GOOGL",
            "max_depth": 3,
        },
    )
    assert resp_paths.status_code == 200
    assert len(resp_paths.json()) >= 1

    resp_hood = client.post(
        "/api/v1/knowledge-graph/neighborhood",
        json={"node_type": "COMPANY", "entity_id": "COMP-AAPL", "depth": 1},
    )
    assert resp_hood.status_code == 200
    assert resp_hood.json()["total_nodes"] >= 1


def test_api_as_of_and_review_queue():
    """POST /api/v1/knowledge-graph/as-of and GET /review-queue."""
    resp_asof = client.post(
        "/api/v1/knowledge-graph/as-of",
        json={"as_of_time": "2024-08-05T00:00:00Z"},
    )
    assert resp_asof.status_code == 200
    assert len(resp_asof.json()) >= 1

    resp_queue = client.get("/api/v1/knowledge-graph/review-queue")
    assert resp_queue.status_code == 200
    assert isinstance(resp_queue.json(), list)
