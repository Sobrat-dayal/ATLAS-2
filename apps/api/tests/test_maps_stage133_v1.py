"""Comprehensive Test Suite for ATLAS Stage 133 - Global Physical Infrastructure Intelligence.

Validates all 14 Reference Fixtures (Fixtures A through N), Bounded Network Topology,
Dimensional Capacity Rules, Multi-Sector Assets, Security/RLS, and REST API Endpoints.
"""

from __future__ import annotations

import pytest
from atlas.maps.infrastructure.analytics.company_exposure import compute_company_infrastructure_exposure
from atlas.maps.infrastructure.analytics.comparison import compare_infrastructure_assets
from atlas.maps.infrastructure.analytics.h3_infrastructure import aggregate_infrastructure_to_h3
from atlas.maps.infrastructure.analytics.regional import compute_regional_infrastructure_summary
from atlas.maps.infrastructure.assets.hierarchy import count_distinct_infrastructure_assets, resolve_asset_hierarchy
from atlas.maps.infrastructure.assets.history import get_asset_state_at, validate_historical_as_of_date
from atlas.maps.infrastructure.assets.registry import asset_registry
from atlas.maps.infrastructure.capacity.aggregation import (
    add_capacity_records,
    aggregate_asset_capacities,
    aggregate_fleet_capacity,
    rollup_plant_units_capacity,
)
from atlas.maps.infrastructure.capacity.units import (
    assert_compatible_dimensions,
    convert_to_canonical_unit,
    get_metric_dimension,
)
from atlas.maps.infrastructure.domain import (
    CapacityBasis,
    CapacityMetric,
    ConnectivityClass,
    EntityRole,
    GeographicPrecisionClass,
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureCapacityRecord,
    InfrastructureNetwork,
    InfrastructureSector,
    InfrastructureStatus,
    LicensingClass,
    NetworkEdge,
    NetworkNode,
)
from atlas.maps.infrastructure.errors import (
    CommercialUseProhibitedError,
    EntitlementRevokedError,
    IncompatibleCapacityUnitError,
    InvalidHistoricalAsOfError,
    InvalidTopologyError,
    SensitiveAssetAccessDeniedError,
    TraversalDepthExceededError,
)
from atlas.maps.infrastructure.networks.queries import BoundedNetworkQueryEngine
from atlas.maps.infrastructure.networks.registry import network_registry
from atlas.maps.infrastructure.networks.topology import validate_network_topology, verify_crossing_separation
from atlas.maps.infrastructure.sectors.airports import create_airport_facility
from atlas.maps.infrastructure.sectors.datacenters import create_data_center_asset
from atlas.maps.infrastructure.sectors.electrical import create_transmission_substation
from atlas.maps.infrastructure.sectors.logistics import create_logistics_asset
from atlas.maps.infrastructure.sectors.mining import create_mining_asset
from atlas.maps.infrastructure.sectors.pipelines import create_pipeline_asset
from atlas.maps.infrastructure.sectors.ports import create_port_facility
from atlas.maps.infrastructure.sectors.power import create_power_plant
from atlas.maps.infrastructure.sectors.rail import create_rail_asset
from atlas.maps.infrastructure.seed import seed_infrastructure_system
from atlas.maps.infrastructure.service import infrastructure_service
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_infrastructure_fixtures():
    """Ensure clean reference state before every test."""
    seed_infrastructure_system()


# =============================================================================
# FIXTURE A: POWER PLANT AND GENERATOR UNITS (Plant P, G1=100 MW, G2=200 MW)
# =============================================================================
def test_fixture_a_power_plant_hierarchy():
    """Plant P (300 MW) with G1 (100 MW) and G2 (200 MW) must not be counted as 3 separate plants."""
    plant = asset_registry.get_asset("INF-PWR-PLANT-P")
    g1 = asset_registry.get_asset("INF-PWR-GEN-G1")
    g2 = asset_registry.get_asset("INF-PWR-GEN-G2")

    rollup = rollup_plant_units_capacity(plant, [g1, g2])
    assert rollup["plant_reported_capacity"] == 300.0
    assert rollup["units_summed_capacity"] == 300.0
    assert rollup["deduplicated_effective_capacity"] == 300.0
    assert rollup["has_reconciliation_gap"] is False

    fleet_total = aggregate_fleet_capacity([plant, g1, g2], CapacityMetric.POWER_MW)
    assert fleet_total == 300.0  # Does NOT double count to 600 MW!

    counts = count_distinct_infrastructure_assets([plant, g1, g2])
    assert counts["facility_count"] == 1
    assert counts["unit_count"] == 2
    assert counts["total_records"] == 3


# =============================================================================
# FIXTURE B: MW VS MWH (Rate of transfer vs Stored work)
# =============================================================================
def test_fixture_b_power_vs_energy_separation():
    """Battery Power (100 MW) and Storage (400 MWh) must never be added as 500 MW."""
    battery = asset_registry.get_asset("INF-PWR-BESS-001")

    mw_rec = next(r for r in battery.capacity_records if r.metric == CapacityMetric.POWER_MW)
    mwh_rec = next(r for r in battery.capacity_records if r.metric == CapacityMetric.ENERGY_MWH)

    assert mw_rec.value == 100.0
    assert mwh_rec.value == 400.0

    # Adding MW and MWh must raise IncompatibleCapacityUnitError
    with pytest.raises(IncompatibleCapacityUnitError):
        add_capacity_records(mw_rec, mwh_rec)

    with pytest.raises(IncompatibleCapacityUnitError):
        assert_compatible_dimensions(mw_rec.metric, mwh_rec.metric)


# =============================================================================
# FIXTURE C: PIPELINE CROSSING (Line crossing is not a topology junction)
# =============================================================================
def test_fixture_c_pipeline_crossing_separation():
    """Two crossing pipeline routes remain disconnected in authoritative topology."""
    network = network_registry.get_network("NET-CROSSING-TEST")
    edge_a = next(e for e in network.edges if e.edge_id == "EDGE-PIPE-A-MAIN")
    edge_b = next(e for e in network.edges if e.edge_id == "EDGE-PIPE-B-MAIN")

    is_connected = verify_crossing_separation(edge_a, edge_b, network.nodes)
    assert is_connected is False

    engine = BoundedNetworkQueryEngine(network)
    path = engine.find_shortest_path("NODE-PA-START", "NODE-PB-EAST")
    assert path is None  # No path exists across the crossing lines


# =============================================================================
# FIXTURE D: RAIL CROSSING (Overpass does not form junction)
# =============================================================================
def test_fixture_d_rail_crossing_separation():
    """Rail bridge crossing another track does not create a false switch junction."""
    nodes = [
        NetworkNode("N-R1", "NET-R", "Track 1 North", "station", 50.0, 10.0),
        NetworkNode("N-R2", "NET-R", "Track 1 South", "station", 50.2, 10.0),
        NetworkNode("N-R3", "NET-R", "Track 2 West", "station", 50.1, 9.8),
        NetworkNode("N-R4", "NET-R", "Track 2 East", "station", 50.1, 10.2),
    ]
    edges = [
        NetworkEdge("E-R1", "NET-R", "N-R1", "N-R2", "rail_main"),
        NetworkEdge("E-R2", "NET-R", "N-R3", "N-R4", "rail_overpass"),
    ]
    rail_net = InfrastructureNetwork("NET-R", "Rail Crossing Test", InfrastructureSector.RAILWAYS, "DE", nodes, edges)
    network_registry.register_network(rail_net)

    engine = BoundedNetworkQueryEngine(rail_net)
    assert engine.find_shortest_path("N-R1", "N-R4") is None


# =============================================================================
# FIXTURE E: PORT LOCATION VS TERMINAL IDENTIFIERS
# =============================================================================
def test_fixture_e_port_locode_vs_terminal():
    """UN/LOCODE represents trade location, separate from specific terminal identifiers."""
    trade_loc = asset_registry.get_asset("INF-PRT-LOC-USLAX")
    terminal = asset_registry.get_asset("INF-PRT-TERM-LAX-400")

    assert trade_loc.identifiers["UN_LOCODE"] == "USLAX"
    assert "TERMINAL_CODE" not in trade_loc.identifiers

    assert terminal.identifiers["TERMINAL_CODE"] == "PIER-400-LAX"
    assert terminal.parent_asset_id == trade_loc.asset_id
    assert terminal.asset_type == InfrastructureAssetType.CONTAINER_TERMINAL


# =============================================================================
# FIXTURE F: CAPACITY BASIS (Nameplate vs Net)
# =============================================================================
def test_fixture_f_capacity_basis_distinction():
    """Nameplate 500 MW and Net 450 MW must not be treated as identical definitions."""
    plant_a = asset_registry.get_asset("INF-PWR-BASIS-A")
    plant_b = asset_registry.get_asset("INF-PWR-BASIS-B")

    rec_a = plant_a.capacity_records[0]
    rec_b = plant_b.capacity_records[0]

    assert rec_a.basis == CapacityBasis.NAMEPLATE
    assert rec_b.basis == CapacityBasis.NET_SUMMER

    comparison = compare_infrastructure_assets([plant_a, plant_b])
    assert len(comparison["basis_discrepancies"]) > 0
    assert "differing_bases" in comparison["basis_discrepancies"][0]


# =============================================================================
# FIXTURE G: OWNERSHIP VS OPERATION
# =============================================================================
def test_fixture_g_owner_vs_operator_roles():
    """Distinct roles for Owner (Company A) and Operator (Company B)."""
    asset = asset_registry.get_asset("INF-PWR-MULTIROLE-001")

    owner_link = next(l for l in asset.entity_links if l.role == EntityRole.OWNER)
    operator_link = next(l for l in asset.entity_links if l.role == EntityRole.OPERATOR)

    assert owner_link.entity_id == "COMP-ALPHA-INVESTORS"
    assert owner_link.ownership_pct == 100.0

    assert operator_link.entity_id == "COMP-BETA-OPERATIONS"
    assert operator_link.ownership_pct == 0.0

    exposure_b = compute_company_infrastructure_exposure("COMP-BETA-OPERATIONS", [asset])
    assert exposure_b["owned_asset_count"] == 0
    assert exposure_b["operated_asset_count"] == 1


# =============================================================================
# FIXTURE H: APPROXIMATE PIPELINE ROUTE
# =============================================================================
def test_fixture_h_approximate_pipeline_precision():
    """Generalized pipeline route marked with ROUTE_CORRIDOR and is_approximate_route=True."""
    pipe = asset_registry.get_asset("INF-PIPE-APPROX-001")
    assert pipe.is_approximate_route is True
    assert pipe.precision == GeographicPrecisionClass.ROUTE_CORRIDOR


# =============================================================================
# FIXTURE I: H3 ASSET COUNT (Plant Count = 1, Unit Count = 3)
# =============================================================================
def test_fixture_i_h3_distinct_asset_counting():
    """Plant with 3 units in same cell reports facility_count=1 and unit_count=3 without inflation."""
    tri_plant = asset_registry.get_asset("INF-PWR-TRI-PLANT")
    u1 = asset_registry.get_asset("INF-PWR-TRI-U1")
    u2 = asset_registry.get_asset("INF-PWR-TRI-U2")
    u3 = asset_registry.get_asset("INF-PWR-TRI-U3")

    cells = aggregate_infrastructure_to_h3([tri_plant, u1, u2, u3], resolution=7)
    assert len(cells) == 1
    cell = cells[0]

    assert cell["facility_count"] == 1
    assert cell["unit_count"] == 3
    assert cell["total_records"] == 4
    assert cell["density_per_km2"] > 0


# =============================================================================
# FIXTURE J: HISTORICAL STATUS (Under construction in 2023, Operational in 2025)
# =============================================================================
def test_fixture_j_historical_status_evaluation():
    """Asset under construction in 2023 and operational in 2025."""
    asset = asset_registry.get_asset("INF-PWR-HIST-001")

    # In June 2023 -> UNDER_CONSTRUCTION
    status_2023 = get_asset_state_at(asset, "2023-06-01")
    assert status_2023 == InfrastructureStatus.UNDER_CONSTRUCTION

    # In June 2025 -> OPERATIONAL
    status_2025 = get_asset_state_at(asset, "2025-06-01")
    assert status_2025 == InfrastructureStatus.OPERATIONAL

    # In 2021 before proposal -> UNKNOWN
    status_2021 = get_asset_state_at(asset, "2021-01-01")
    assert status_2021 == InfrastructureStatus.UNKNOWN

    # Future date raises InvalidHistoricalAsOfError
    with pytest.raises(InvalidHistoricalAsOfError):
        get_asset_state_at(asset, "2099-01-01")


# =============================================================================
# FIXTURE K: UNKNOWN CAPACITY (Airport without throughput)
# =============================================================================
def test_fixture_k_unknown_capacity_preservation():
    """Airport without reported passenger throughput displays None, never fabricated numbers."""
    airport = asset_registry.get_asset("INF-AIR-UNKNOWN-CAP")
    pax_records = [r for r in airport.capacity_records if r.metric == CapacityMetric.PASSENGERS_YEAR]
    assert len(pax_records) == 0

    comparison = compare_infrastructure_assets([airport])
    asset_card = comparison["assets"][0]
    cap = asset_card["capacities"][0]
    assert cap["value"] is None
    assert cap["display"] == "Not available"


# =============================================================================
# FIXTURE L: PRIVATE NETWORK & TENANT ISOLATION
# =============================================================================
def test_fixture_l_private_network_access_denial():
    """Private network and asset inaccessible to unauthorized tenants."""
    # Tenant match succeeds
    net = network_registry.get_network("NET-PRIVATE-SECURE-001", actor_tenant_id="TENANT-DEFENSE-CORP")
    assert net is not None

    # Mismatched or missing tenant raises SensitiveAssetAccessDeniedError
    with pytest.raises(SensitiveAssetAccessDeniedError):
        network_registry.get_network("NET-PRIVATE-SECURE-001", actor_tenant_id="TENANT-CIVILIAN")

    with pytest.raises(SensitiveAssetAccessDeniedError):
        asset_registry.get_asset("INF-PWR-PRIVATE-001", actor_tenant_id="TENANT-CIVILIAN")


# =============================================================================
# FIXTURE M: SOURCE LICENSING RESTRICTION (Non-Commercial Dataset)
# =============================================================================
def test_fixture_m_non_commercial_licensing_enforcement():
    """Non-commercial dataset cannot be accessed in commercial mode without rights."""
    # Academic/non-commercial context succeeds
    asset = asset_registry.get_asset("INF-MIN-NONCOMM-001", is_commercial_context=False)
    assert asset is not None

    # Commercial context raises CommercialUseProhibitedError
    with pytest.raises(CommercialUseProhibitedError):
        asset_registry.get_asset("INF-MIN-NONCOMM-001", is_commercial_context=True)


# =============================================================================
# FIXTURE N: SOURCE REVOCATION (Revoked source renders derived data inaccessible)
# =============================================================================
def test_fixture_n_source_revocation():
    """Revoking dataset entitlement blocks asset lookup and derived H3 aggregates."""
    asset_registry.revoke_source_entitlement("REVOCABLE_PROPRIETARY_FEED")

    with pytest.raises(EntitlementRevokedError):
        asset_registry.get_asset("INF-DC-REVOCABLE-001")

    # H3 aggregation with revoked source raises EntitlementRevokedError
    revocable_asset = InfrastructureAsset(
        asset_id="TEST-REV-1",
        name="Revoked",
        sector=InfrastructureSector.DATA_CENTERS,
        asset_type=InfrastructureAssetType.DATA_CENTER_FACILITY,
        country="US",
        latitude=39.0,
        longitude=-77.0,
        source_id="REVOCABLE_PROPRIETARY_FEED",
    )
    with pytest.raises(EntitlementRevokedError):
        aggregate_infrastructure_to_h3([revocable_asset], revoked_sources={"REVOCABLE_PROPRIETARY_FEED"})


# =============================================================================
# TOPOLOGY AND GRAPH BOUNDS
# =============================================================================
def test_bounded_network_traversal_depth():
    """Graph traversal strictly respects maximum depth limits and cycle protection."""
    nodes = [NetworkNode(f"N{i}", "NET-LINE", f"Node {i}", "substation", 40.0 + i * 0.1, -80.0) for i in range(10)]
    edges = [
        NetworkEdge(f"E{i}", "NET-LINE", f"N{i}", f"N{i+1}", "line", length_km=10.0)
        for i in range(9)
    ]
    linear_net = InfrastructureNetwork("NET-LINE", "Linear Test", InfrastructureSector.ELECTRICITY_NETWORKS, "US", nodes, edges)

    engine = BoundedNetworkQueryEngine(linear_net, max_depth=5)
    subgraph = engine.get_reachable_subgraph("N0", max_hops=4)
    assert subgraph["depth_reached"] == 4
    assert subgraph["node_count"] == 5

    # Exceeding maximum authorized depth raises TraversalDepthExceededError
    with pytest.raises(TraversalDepthExceededError):
        engine.get_reachable_subgraph("N0", max_hops=8)


# =============================================================================
# ALL 9 SECTOR COVERAGE VERIFICATION
# =============================================================================
def test_all_nine_sectors_represented():
    """Verify assets exist and are categorized across all 9 canonical sectors."""
    assets = asset_registry.list_assets(limit=1000)
    sectors_found = {a.sector for a in assets}

    for sector in InfrastructureSector:
        assert sector in sectors_found, f"Missing asset representation for sector {sector.value}"


# =============================================================================
# REST API ENDPOINTS INTEGRATION TESTS
# =============================================================================
def test_fastapi_infrastructure_endpoints():
    """Validate FastAPI router endpoints using TestClient."""
    from atlas_api.main import app

    client = TestClient(app)

    # 1. Categories
    resp = client.get("/api/v1/maps/infrastructure/categories")
    assert resp.status_code == 200
    assert resp.json()["total_sectors"] == 9

    # 2. Datasets
    resp = client.get("/api/v1/maps/infrastructure/datasets")
    assert resp.status_code == 200
    assert len(resp.json()) >= 5

    # 3. List Assets
    resp = client.get("/api/v1/maps/infrastructure/assets?sector=power_generation")
    assert resp.status_code == 200
    assert resp.json()["count"] > 0

    # 4. Single Asset
    resp = client.get("/api/v1/maps/infrastructure/assets/INF-PWR-PLANT-P")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Horizon Clean Energy Center (Plant P)"

    # 5. Asset History
    resp = client.get("/api/v1/maps/infrastructure/assets/INF-PWR-HIST-001/history")
    assert resp.status_code == 200
    assert len(resp.json()) >= 3

    # 6. Asset Relationships
    resp = client.get("/api/v1/maps/infrastructure/assets/INF-PWR-MULTIROLE-001/relationships")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    # 7. Spatial Query
    resp = client.post(
        "/api/v1/maps/infrastructure/assets/spatial-query",
        json={"min_lng": -125.0, "min_lat": 30.0, "max_lng": -110.0, "max_lat": 40.0},
    )
    assert resp.status_code == 200
    assert resp.json()["count"] > 0

    # 8. Compare Assets
    resp = client.post(
        "/api/v1/maps/infrastructure/assets/compare",
        json={"asset_ids": ["INF-PWR-BASIS-A", "INF-PWR-BASIS-B"]},
    )
    assert resp.status_code == 200
    assert len(resp.json()["basis_discrepancies"]) > 0

    # 9. List Networks
    resp = client.get("/api/v1/maps/infrastructure/networks")
    assert resp.status_code == 200
    assert len(resp.json()) > 0

    # 10. Query Network
    resp = client.post(
        "/api/v1/maps/infrastructure/networks/NET-CROSSING-TEST/query",
        json={"start_node_id": "NODE-PA-START", "max_hops": 2},
    )
    assert resp.status_code == 200
    assert resp.json()["node_count"] == 2

    # 11. H3 Aggregates
    resp = client.post(
        "/api/v1/maps/infrastructure/aggregates",
        json={"resolution": 7},
    )
    assert resp.status_code == 200
    assert resp.json()["cell_count"] > 0

    # 12. Regional Summary
    resp = client.post(
        "/api/v1/maps/infrastructure/regional-summary",
        json={"region_name": "North America"},
    )
    assert resp.status_code == 200
    assert resp.json()["total_assets"] > 0
