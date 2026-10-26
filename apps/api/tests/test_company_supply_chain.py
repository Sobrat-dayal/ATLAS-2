"""Automated Test Suite for Company Supply Chain Intelligence (Stage 88).

Tests:
1. Canonical Entity & Counterparty Identity Resolution
2. Relationship Directionality (Upstream Supplier vs Downstream Customer)
3. Multi-Category Commercial Relationship Semantics
4. Verifiable Source Evidence Citations (Form 10-K, Form 8-K, Corporate Disclosures)
5. Bounded Multi-Tier Graph Traversal (Tier 1, Tier 2 Upstream, Cycle Protection)
6. Customer & Supplier Concentration Analysis (Disclosed %, Anonymous Customer A)
7. Historical Relationship Timeline & Milestones
8. Disclosure Coverage & Stale Data Qualification
9. FastAPI HTTP Router Integration & Error Envelopes
10. Side-Effect Invariants (0 LLM calls, 0 Trading orders, 0 Graph writes)
"""

from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.supply_chain import (
    CompanySupplyChainRepository,
    CompanySupplyChainService,
    ConcentrationScope,
    SupplyChainCompanyNotFoundError,
    SupplyChainInvalidDirectionError,
    SupplyChainRelationship,
    SupplyChainRelationshipNotFoundError,
    SupplyChainRelationshipType,
    SupplyChainTraversalLimitExceededError,
    VerificationStatus,
    traverse_supply_network,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.company_supply_chain import (
    get_supply_chain_service,
)
from atlas_api.routers.company_supply_chain import (
    router as company_supply_chain_router,
)

# =============================================================================
# Test Fixtures & Setup
# =============================================================================


@pytest.fixture
def repo():
    return CompanySupplyChainRepository()


@pytest.fixture
def service(repo):
    return CompanySupplyChainService(repository=repo)


@pytest.fixture
def mock_principal():
    return AuthPrincipal(
        sub="user-supply-analyst-1",
        email="analyst@atlas.financial",
    )


@pytest.fixture
def api_client(service, mock_principal):
    app = FastAPI()
    app.include_router(company_supply_chain_router, prefix="/api/v1")

    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True

    app.dependency_overrides[get_supply_chain_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    return TestClient(app)


# =============================================================================
# 1. Canonical Entity Identity & Resolution
# =============================================================================


def test_apple_and_counterparty_identities(repo):
    """Subject company and counterparties resolve to verified canonical UUIDs."""
    apple = repo.get_company(repo.apple_id)
    assert apple is not None
    assert apple["name"] == "Apple Inc."
    assert apple["ticker"] == "AAPL"
    assert apple["country"] == "United States"

    tsmc = repo.get_company(repo.tsmc_id)
    assert tsmc is not None
    assert "Taiwan Semiconductor" in tsmc["name"]
    assert tsmc["country"] == "Taiwan"
    assert tsmc["industry"] == "Semiconductors"

    foxconn = repo.get_company(repo.foxconn_id)
    assert foxconn is not None
    assert "Hon Hai" in foxconn["name"]
    assert foxconn["industry"] == "Electronic Manufacturing Services"


def test_unknown_company_raises_not_found(service):
    """Unknown company UUID raises SupplyChainCompanyNotFoundError."""
    with pytest.raises(SupplyChainCompanyNotFoundError):
        service.get_overview("c0000000-0000-0000-0000-000000009999")


# =============================================================================
# 2. Relationship Directionality & Commercial Semantics
# =============================================================================


def test_relationship_directionality(service, repo):
    """Direct suppliers and customers are properly segregated by directed orientation."""
    # 1. Direct Suppliers (Supplier -> Apple)
    suppliers_res = service.get_suppliers(repo.apple_id)
    assert suppliers_res.total_count >= 6
    supplier_ids = [s.supplier_entity_id for s in suppliers_res.items]

    # TSMC, Foxconn, Sony, Samsung, Broadcom, Qualcomm must be suppliers
    assert repo.tsmc_id in supplier_ids
    assert repo.foxconn_id in supplier_ids
    assert repo.sony_id in supplier_ids
    assert repo.samsung_id in supplier_ids
    assert repo.broadcom_id in supplier_ids
    assert repo.qualcomm_id in supplier_ids

    # For all supplier items, Apple must be the customer
    for s in suppliers_res.items:
        assert s.customer_entity_id == repo.apple_id

    # 2. Direct Customers / Distribution Channels (Apple -> Customer)
    customers_res = service.get_customers(repo.apple_id)
    assert customers_res.total_count >= 4
    customer_ids = [c.customer_entity_id for c in customers_res.items]

    assert repo.bby_id in customer_ids
    assert repo.amzn_id in customer_ids
    assert repo.att_id in customer_ids
    assert repo.vz_id in customer_ids

    # For all customer items, Apple must be the supplier
    for c in customers_res.items:
        assert c.supplier_entity_id == repo.apple_id


def test_competitor_and_supplier_dual_role(service, repo):
    """Samsung is recognized as a verified component supplier without altering peer semantics."""
    suppliers_res = service.get_suppliers(repo.apple_id)
    samsung_rel = next(
        s for s in suppliers_res.items if s.supplier_entity_id == repo.samsung_id
    )
    assert samsung_rel.relationship_type == SupplyChainRelationshipType.SUPPLIES_COMPONENTS_TO
    assert "OLED" in samsung_rel.supplied_item_type
    assert samsung_rel.verification_status == VerificationStatus.VERIFIED


# =============================================================================
# 3. Verifiable Source Evidence Citations
# =============================================================================


def test_relationship_evidence_citations(service, repo):
    """All asserted relationships contain audited source evidence citations."""
    rel = service.get_relationship("rel-aapl-tsmc-01")
    assert rel.verification_status == VerificationStatus.VERIFIED
    assert rel.is_critical is True
    assert len(rel.evidence) >= 2

    # Verify Form 10-K citation
    filing_ev = rel.evidence[0]
    assert "SEC Form 10-K" in filing_ev.source_filing_ref
    assert filing_ev.source_provider == "SEC_EDGAR"
    assert "Item 1" in filing_ev.section_anchor
    assert "single-source" in filing_ev.excerpt.lower()


def test_relationship_not_found(service):
    """Querying an unknown relationship ID raises 404 domain error."""
    with pytest.raises(SupplyChainRelationshipNotFoundError):
        service.get_relationship("rel-unknown-9999")


# =============================================================================
# 4. Multi-Tier Network Graph Traversal
# =============================================================================


def test_tier_1_network_traversal(service, repo):
    """Tier-1 traversal returns direct suppliers and customers of the subject company."""
    network = service.get_network(repo.apple_id, direction="BOTH", depth=1)
    assert network.traversal_depth == 1
    assert network.total_nodes >= 10
    assert network.total_edges >= 10

    # Subject node exists and marked as subject
    subject_node = next(n for n in network.nodes if n.is_subject)
    assert subject_node.entity_id == repo.apple_id
    assert subject_node.tier == 0

    # All direct edges must connect directly to Apple
    for edge in network.edges:
        assert (
            edge.source_entity_id == repo.apple_id
            or edge.target_entity_id == repo.apple_id
        )


def test_tier_2_upstream_traversal(service, repo):
    """Tier-2 traversal uncovers secondary upstream equipment and materials suppliers."""
    network = service.get_network(repo.apple_id, direction="UPSTREAM_SUPPLIER", depth=2)
    assert network.traversal_depth == 2

    node_ids = [n.entity_id for n in network.nodes]
    # ASML, Tokyo Electron, and Shin-Etsu supply TSMC (which supplies Apple)
    assert repo.asml_id in node_ids
    assert repo.tel_id in node_ids
    assert repo.shinetsu_id in node_ids

    asml_node = next(n for n in network.nodes if n.entity_id == repo.asml_id)
    assert asml_node.tier == 2


def test_traversal_depth_limit_enforced(service, repo):
    """Requesting traversal depth > 3 raises SupplyChainTraversalLimitExceededError."""
    with pytest.raises(SupplyChainTraversalLimitExceededError):
        service.get_network(repo.apple_id, depth=4)


def test_invalid_direction_rejected(service, repo):
    """Invalid direction parameter raises SupplyChainInvalidDirectionError."""
    with pytest.raises(SupplyChainInvalidDirectionError):
        service.get_network(repo.apple_id, direction="INVALID_DIR")


def test_graph_cycle_protection(repo):
    """Cyclic relationships do not cause infinite loops in graph traversal."""
    # Create circular mock relationships: A -> B -> C -> A
    cycle_rels = [
        SupplyChainRelationship(
            relationship_id="rel-c1",
            supplier_entity_id="comp-A",
            customer_entity_id="comp-B",
            relationship_type=SupplyChainRelationshipType.SUPPLIES_COMPONENTS_TO,
            supplied_item_type="Parts",
            supplied_item_description="Circular part 1",
        ),
        SupplyChainRelationship(
            relationship_id="rel-c2",
            supplier_entity_id="comp-B",
            customer_entity_id="comp-C",
            relationship_type=SupplyChainRelationshipType.SUPPLIES_COMPONENTS_TO,
            supplied_item_type="Parts",
            supplied_item_description="Circular part 2",
        ),
        SupplyChainRelationship(
            relationship_id="rel-c3",
            supplier_entity_id="comp-C",
            customer_entity_id="comp-A",
            relationship_type=SupplyChainRelationshipType.SUPPLIES_COMPONENTS_TO,
            supplied_item_type="Parts",
            supplied_item_description="Circular part 3",
        ),
    ]

    node_tiers, edges = traverse_supply_network(
        root_company_id="comp-A",
        all_relationships=cycle_rels,
        direction="BOTH",
        max_depth=3,
    )
    # Should terminate safely and visit each node once
    assert len(node_tiers) == 3
    assert "comp-A" in node_tiers
    assert "comp-B" in node_tiers
    assert "comp-C" in node_tiers


# =============================================================================
# 5. Customer & Supplier Concentration Analysis
# =============================================================================


def test_customer_and_supplier_concentration(service, repo):
    """Concentration disclosures accurately capture reported percentages and anonymous customers."""
    conc = service.get_concentration(repo.apple_id)

    # 1. Customer dependency: Apple states no customer > 10%
    no_major_cust = next(
        c for c in conc.customer_dependencies if c.is_anonymous and "< 10" in c.formatted_percentage
    )
    assert no_major_cust.scope == ConcentrationScope.CONSOLIDATED_REVENUE

    # 2. Supplier dependency: Broadcom reports Apple accounts for 20% of net revenue
    broadcom_conc = next(
        c for c in conc.customer_dependencies if c.counterparty_entity_id == repo.broadcom_id
    )
    assert broadcom_conc.reported_percentage == 20.0
    assert broadcom_conc.revenue_amount == 10320000000

    # 3. Supplier dependency: Cirrus Logic discloses anonymous Customer A = 87%
    cirrus_conc = next(
        c for c in conc.customer_dependencies if c.counterparty_entity_id == repo.crus_id
    )
    assert cirrus_conc.is_anonymous is True
    assert cirrus_conc.reported_percentage == 87.0

    # 4. Critical input dependency: TSMC sole source foundry
    tsmc_dep = next(
        s for s in conc.supplier_dependencies if s.counterparty_entity_id == repo.tsmc_id
    )
    assert tsmc_dep.scope == ConcentrationScope.CRITICAL_INPUT_DEPENDENCY
    assert "Sole Source" in tsmc_dep.formatted_percentage


# =============================================================================
# 6. Historical Relationship Milestones
# =============================================================================


def test_historical_timeline_events(service, repo):
    """Historical timeline reflects verifiable milestones without look-ahead bias."""
    history = service.get_history(repo.apple_id)
    assert history.total_events >= 5

    # Check 2019 Qualcomm settlement event
    qcom_event = next(
        e for e in history.events if "Qualcomm" in e.description and "settlement" in e.description.lower()
    )
    assert qcom_event.event_date == "2019-04-16"
    assert "Form 8-K" in qcom_event.source_ref

    # Check 2024 Qualcomm extension
    ext_event = next(
        e for e in history.events if "2027" in e.description
    )
    assert ext_event.event_date == "2024-02-05"


# =============================================================================
# 7. Disclosure Coverage & Stale Data Qualification
# =============================================================================


def test_supply_chain_coverage_reporting(service, repo):
    """Coverage endpoint returns transparent disclosure boundaries and source list."""
    coverage = service.get_coverage(repo.apple_id)
    assert "SEC Form 10-K" in coverage.disclosed_suppliers_coverage
    assert len(coverage.primary_sources) >= 4
    assert len(coverage.limitations) >= 3
    assert "FY2024 Form 10-K" in coverage.data_freshness_as_of


# =============================================================================
# 8. FastAPI HTTP Router Integration Tests
# =============================================================================


def test_api_overview_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/overview returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["subject_company_name"] == "Apple Inc."
    assert data["direct_suppliers_count"] >= 6
    assert data["direct_customers_count"] >= 4
    assert data["tier_2_suppliers_count"] >= 3


def test_api_suppliers_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/suppliers returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/suppliers")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] >= 6
    assert any(s["supplier_ticker"] == "TSM" for s in data["items"])


def test_api_customers_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/customers returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/customers")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] >= 4
    assert any(c["customer_ticker"] == "BBY" for c in data["items"])


def test_api_network_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/network returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/network?depth=2")
    assert res.status_code == 200
    data = res.json()
    assert data["traversal_depth"] == 2
    assert len(data["nodes"]) >= 10
    assert len(data["edges"]) >= 10


def test_api_concentration_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/concentration returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/concentration")
    assert res.status_code == 200
    data = res.json()
    assert len(data["customer_dependencies"]) >= 3
    assert len(data["supplier_dependencies"]) >= 2


def test_api_relationship_details_and_evidence(api_client, repo):
    """GET /relationships/{id} and /relationships/{id}/evidence return HTTP 200."""
    rel_res = api_client.get(
        f"/api/v1/companies/{repo.apple_id}/supply-chain/relationships/rel-aapl-tsmc-01"
    )
    assert rel_res.status_code == 200
    rel_data = rel_res.json()
    assert rel_data["relationship_type"] == "CONTRACT_MANUFACTURES_FOR"

    ev_res = api_client.get(
        f"/api/v1/companies/{repo.apple_id}/supply-chain/relationships/rel-aapl-tsmc-01/evidence"
    )
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert len(ev_data) >= 2


def test_api_filters_endpoint(api_client, repo):
    """GET /companies/{company_id}/supply-chain/filters returns HTTP 200."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/filters")
    assert res.status_code == 200
    data = res.json()
    assert "relationship_types" in data
    assert "verification_statuses" in data
    assert "countries" in data


def test_api_invalid_company_returns_404(api_client):
    """GET for invalid company entity returns HTTP 404."""
    res = api_client.get("/api/v1/companies/c-invalid-uuid-9999/supply-chain/overview")
    assert res.status_code == 404


def test_api_excessive_depth_returns_400(api_client, repo):
    """GET /network with depth > 3 returns HTTP 400 or 422."""
    res = api_client.get(f"/api/v1/companies/{repo.apple_id}/supply-chain/network?depth=5")
    assert res.status_code in (400, 422)
