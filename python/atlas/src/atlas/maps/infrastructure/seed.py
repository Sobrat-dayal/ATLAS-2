"""Institutional Reference Dataset and Fixture Seeding for Physical Infrastructure (Stage 133)."""

from __future__ import annotations

from atlas.maps.infrastructure.assets.registry import asset_registry
from atlas.maps.infrastructure.domain import (
    CapacityBasis,
    CapacityMetric,
    ConnectivityClass,
    EntityRole,
    GeographicPrecisionClass,
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureCapacityRecord,
    InfrastructureEntityLink,
    InfrastructureNetwork,
    InfrastructureSector,
    InfrastructureStatus,
    InfrastructureStatusHistory,
    LicensingClass,
    NetworkEdge,
    NetworkNode,
)
from atlas.maps.infrastructure.networks.registry import network_registry
from atlas.maps.infrastructure.sectors.airports import create_airport_facility
from atlas.maps.infrastructure.sectors.datacenters import create_data_center_asset
from atlas.maps.infrastructure.sectors.electrical import create_transmission_substation
from atlas.maps.infrastructure.sectors.logistics import create_logistics_asset
from atlas.maps.infrastructure.sectors.mining import create_mining_asset
from atlas.maps.infrastructure.sectors.pipelines import create_pipeline_asset
from atlas.maps.infrastructure.sectors.ports import create_port_facility
from atlas.maps.infrastructure.sectors.power import create_power_plant
from atlas.maps.infrastructure.sectors.rail import create_rail_asset


def seed_infrastructure_system() -> None:
    """Populate authoritative physical infrastructure datasets including all 14 Reference Fixtures."""
    asset_registry.clear()
    network_registry.clear()

    # =========================================================================
    # FIXTURE A: POWER PLANT AND GENERATOR UNITS (Plant P, G1=100 MW, G2=200 MW)
    # =========================================================================
    plant_p = create_power_plant(
        asset_id="INF-PWR-PLANT-P",
        name="Horizon Clean Energy Center (Plant P)",
        country="US",
        latitude=35.1200,
        longitude=-101.8800,
        primary_fuel="solar_storage",
        capacity_mw=300.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
        child_asset_ids=["INF-PWR-GEN-G1", "INF-PWR-GEN-G2"],
        source_id="GEM_POWER_US",
    )
    gen_g1 = create_power_plant(
        asset_id="INF-PWR-GEN-G1",
        name="Horizon Generator G1",
        country="US",
        latitude=35.1205,
        longitude=-101.8802,
        primary_fuel="solar_pv",
        asset_type=InfrastructureAssetType.GENERATING_UNIT,
        capacity_mw=100.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
        parent_asset_id="INF-PWR-PLANT-P",
        source_id="GEM_POWER_US",
    )
    gen_g2 = create_power_plant(
        asset_id="INF-PWR-GEN-G2",
        name="Horizon Generator G2",
        country="US",
        latitude=35.1210,
        longitude=-101.8805,
        primary_fuel="solar_pv",
        asset_type=InfrastructureAssetType.GENERATING_UNIT,
        capacity_mw=200.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
        parent_asset_id="INF-PWR-PLANT-P",
        source_id="GEM_POWER_US",
    )
    asset_registry.register_asset(plant_p)
    asset_registry.register_asset(gen_g1)
    asset_registry.register_asset(gen_g2)

    # =========================================================================
    # FIXTURE B: POWER (MW) VS ENERGY STORAGE (MWh) (100 MW, 400 MWh)
    # =========================================================================
    battery_b = create_power_plant(
        asset_id="INF-PWR-BESS-001",
        name="Iron Springs Battery Energy Storage System",
        country="US",
        latitude=34.0500,
        longitude=-117.2000,
        primary_fuel="battery_storage",
        asset_type=InfrastructureAssetType.BATTERY_STORAGE,
        capacity_mw=100.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
        storage_mwh=400.0,
        source_id="CAISO_MASTER",
    )
    asset_registry.register_asset(battery_b)

    # =========================================================================
    # FIXTURES C & D: CROSSING SEPARATION (Pipelines & Rail Overpass)
    # =========================================================================
    pipeline_a = create_pipeline_asset(
        asset_id="INF-PIPE-ROUTE-A",
        name="Trans-Midwest Crude Pipeline A",
        country="US",
        commodity="crude_oil",
        latitude=41.5000,
        longitude=-87.5000,
        diameter_inches=30.0,
        throughput_bpd=450000.0,
        is_approximate_route=False,
    )
    pipeline_b = create_pipeline_asset(
        asset_id="INF-PIPE-ROUTE-B",
        name="Great Lakes Natural Gas Pipeline B",
        country="US",
        commodity="natural_gas",
        latitude=41.5000,
        longitude=-87.5000,
        diameter_inches=36.0,
        throughput_mmcfd=1200.0,
        is_approximate_route=False,
    )
    asset_registry.register_asset(pipeline_a)
    asset_registry.register_asset(pipeline_b)

    # Networks for Fixtures C and D demonstrating topology disconnection
    crossing_network = InfrastructureNetwork(
        network_id="NET-CROSSING-TEST",
        name="Midwest Pipeline & Rail Crossing Verification Testbed",
        sector=InfrastructureSector.OIL_GAS,
        country="US",
        nodes=[
            NetworkNode("NODE-PA-START", "NET-CROSSING-TEST", "Pipeline A Inlet", "pumping_station", 41.20, -87.50),
            NetworkNode("NODE-PA-END", "NET-CROSSING-TEST", "Pipeline A Outlet", "refinery_junction", 41.80, -87.50),
            NetworkNode("NODE-PB-WEST", "NET-CROSSING-TEST", "Pipeline B Compressor West", "compressor_station", 41.50, -87.80),
            NetworkNode("NODE-PB-EAST", "NET-CROSSING-TEST", "Pipeline B Header East", "metering_station", 41.50, -87.20),
        ],
        edges=[
            NetworkEdge(
                edge_id="EDGE-PIPE-A-MAIN",
                network_id="NET-CROSSING-TEST",
                from_node_id="NODE-PA-START",
                to_node_id="NODE-PA-END",
                edge_type="crude_pipeline",
                coordinates=[[-87.50, 41.20], [-87.50, 41.80]],
                length_km=66.7,
                connectivity_evidence=ConnectivityClass.VERIFIED,
            ),
            NetworkEdge(
                edge_id="EDGE-PIPE-B-MAIN",
                network_id="NET-CROSSING-TEST",
                from_node_id="NODE-PB-WEST",
                to_node_id="NODE-PB-EAST",
                edge_type="gas_pipeline",
                coordinates=[[-87.80, 41.50], [-87.20, 41.50]],
                length_km=50.2,
                connectivity_evidence=ConnectivityClass.VERIFIED,
            ),
        ],
    )
    network_registry.register_network(crossing_network)

    # =========================================================================
    # FIXTURE E: PORT LOCATION VS SPECIFIC TERMINAL (UN/LOCODE vs Terminal)
    # =========================================================================
    port_trade_loc = create_port_facility(
        asset_id="INF-PRT-LOC-USLAX",
        name="Port of Los Angeles Trade Location",
        country="US",
        latitude=33.7432,
        longitude=-118.2673,
        un_locode="USLAX",
        asset_type=InfrastructureAssetType.TRADE_LOCATION,
        teu_capacity=10600000.0,
    )
    port_terminal_400 = create_port_facility(
        asset_id="INF-PRT-TERM-LAX-400",
        name="APM Terminals Pier 400 (Terminal 400)",
        country="US",
        latitude=33.7258,
        longitude=-118.2435,
        terminal_code="PIER-400-LAX",
        asset_type=InfrastructureAssetType.CONTAINER_TERMINAL,
        teu_capacity=3400000.0,
        max_draft_meters=16.8,
        berth_count=4,
        parent_asset_id="INF-PRT-LOC-USLAX",
    )
    asset_registry.register_asset(port_trade_loc)
    asset_registry.register_asset(port_terminal_400)

    # =========================================================================
    # FIXTURE F: CAPACITY BASIS (Plant A Nameplate 500 MW vs Plant B Net 450 MW)
    # =========================================================================
    plant_basis_a = create_power_plant(
        asset_id="INF-PWR-BASIS-A",
        name="Prairie Wind Power Station Alpha",
        country="US",
        latitude=40.8000,
        longitude=-96.6000,
        primary_fuel="onshore_wind",
        capacity_mw=500.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
    )
    plant_basis_b = create_power_plant(
        asset_id="INF-PWR-BASIS-B",
        name="Riverfront Combined Cycle Plant Beta",
        country="US",
        latitude=40.8500,
        longitude=-96.5500,
        primary_fuel="natural_gas",
        capacity_mw=450.0,
        capacity_basis=CapacityBasis.NET_SUMMER,
    )
    asset_registry.register_asset(plant_basis_a)
    asset_registry.register_asset(plant_basis_b)

    # =========================================================================
    # FIXTURE G: OWNERSHIP VS OPERATION (Owner Company A, Operator Company B)
    # =========================================================================
    owned_operated_asset = create_power_plant(
        asset_id="INF-PWR-MULTIROLE-001",
        name="Keystone Energy Infrastructure Facility",
        country="US",
        latitude=39.9500,
        longitude=-75.1600,
        primary_fuel="nuclear",
        capacity_mw=1200.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
    )
    owned_operated_asset.entity_links = [
        InfrastructureEntityLink(
            entity_id="COMP-ALPHA-INVESTORS",
            entity_name="Alpha Global Infrastructure Partners LLC",
            role=EntityRole.OWNER,
            ownership_pct=100.0,
            evidence_source="SEC_10K_2025",
        ),
        InfrastructureEntityLink(
            entity_id="COMP-BETA-OPERATIONS",
            entity_name="Beta Power Operations Corp",
            role=EntityRole.OPERATOR,
            ownership_pct=0.0,
            evidence_source="FERC_FORM_1",
        ),
    ]
    asset_registry.register_asset(owned_operated_asset)

    # =========================================================================
    # FIXTURE H: APPROXIMATE PIPELINE ROUTE
    # =========================================================================
    approx_pipeline = create_pipeline_asset(
        asset_id="INF-PIPE-APPROX-001",
        name="Northern Plains Generalized Gas Corridor",
        country="US",
        commodity="natural_gas",
        latitude=46.8000,
        longitude=-100.7000,
        diameter_inches=42.0,
        throughput_mmcfd=2400.0,
        is_approximate_route=True,
    )
    approx_pipeline.precision = GeographicPrecisionClass.ROUTE_CORRIDOR
    asset_registry.register_asset(approx_pipeline)

    # =========================================================================
    # FIXTURE I: H3 ASSET COUNT (1 Plant + 3 Units in Same Location)
    # =========================================================================
    tri_plant = create_power_plant(
        asset_id="INF-PWR-TRI-PLANT",
        name="Tri-County Thermal Generating Station",
        country="US",
        latitude=32.7767,
        longitude=-96.7970,
        primary_fuel="natural_gas",
        capacity_mw=600.0,
        capacity_basis=CapacityBasis.NAMEPLATE,
        child_asset_ids=["INF-PWR-TRI-U1", "INF-PWR-TRI-U2", "INF-PWR-TRI-U3"],
    )
    tri_u1 = create_power_plant(
        asset_id="INF-PWR-TRI-U1",
        name="Tri-County Unit 1",
        country="US",
        latitude=32.7767,
        longitude=-96.7970,
        primary_fuel="natural_gas",
        asset_type=InfrastructureAssetType.GENERATING_UNIT,
        capacity_mw=200.0,
        parent_asset_id="INF-PWR-TRI-PLANT",
    )
    tri_u2 = create_power_plant(
        asset_id="INF-PWR-TRI-U2",
        name="Tri-County Unit 2",
        country="US",
        latitude=32.7767,
        longitude=-96.7970,
        primary_fuel="natural_gas",
        asset_type=InfrastructureAssetType.GENERATING_UNIT,
        capacity_mw=200.0,
        parent_asset_id="INF-PWR-TRI-PLANT",
    )
    tri_u3 = create_power_plant(
        asset_id="INF-PWR-TRI-U3",
        name="Tri-County Unit 3",
        country="US",
        latitude=32.7767,
        longitude=-96.7970,
        primary_fuel="natural_gas",
        asset_type=InfrastructureAssetType.GENERATING_UNIT,
        capacity_mw=200.0,
        parent_asset_id="INF-PWR-TRI-PLANT",
    )
    asset_registry.register_asset(tri_plant)
    asset_registry.register_asset(tri_u1)
    asset_registry.register_asset(tri_u2)
    asset_registry.register_asset(tri_u3)

    # =========================================================================
    # FIXTURE J: HISTORICAL STATUS (Under construction in 2023, Operational in 2025)
    # =========================================================================
    historical_asset = create_power_plant(
        asset_id="INF-PWR-HIST-001",
        name="Sunbelt Solar Mega-Array 1",
        country="US",
        latitude=33.4500,
        longitude=-112.0700,
        primary_fuel="solar_pv",
        capacity_mw=400.0,
    )
    historical_asset.status = InfrastructureStatus.OPERATIONAL
    historical_asset.status_history = [
        InfrastructureStatusHistory(
            status=InfrastructureStatus.PROPOSED,
            effective_date="2022-01-15",
            evidence_source="REGULATORY_FILING",
        ),
        InfrastructureStatusHistory(
            status=InfrastructureStatus.UNDER_CONSTRUCTION,
            effective_date="2023-01-10",
            evidence_source="EPC_CONSTRUCTION_COMMENCEMENT",
        ),
        InfrastructureStatusHistory(
            status=InfrastructureStatus.OPERATIONAL,
            effective_date="2025-02-01",
            evidence_source="GRID_COMMERCIAL_OPERATION_DATE",
        ),
    ]
    asset_registry.register_asset(historical_asset)

    # =========================================================================
    # FIXTURE K: UNKNOWN CAPACITY (Airport without passenger/cargo measurement)
    # =========================================================================
    unknown_cap_airport = create_airport_facility(
        asset_id="INF-AIR-UNKNOWN-CAP",
        name="Red Rock Regional Airstrip",
        country="US",
        latitude=35.5000,
        longitude=-111.6000,
        icao_code="KRRR",
        iata_code=None,  # Proves non-equivalence of ICAO and IATA
        passengers_per_year=None,  # Not available
        cargo_tonnes_year=None,
        runway_count=None,
    )
    asset_registry.register_asset(unknown_cap_airport)

    # Transmission Substation (Electricity Networks Sector)
    chino_substation = create_transmission_substation(
        asset_id="INF-GRID-SUB-CHINO",
        name="Chino 500kV Bulk Transmission Substation",
        country="US",
        latitude=34.0150,
        longitude=-117.6800,
        voltage_kv=500.0,
        capacity_mva=2200.0,
    )
    asset_registry.register_asset(chino_substation)

    # =========================================================================
    # FIXTURE L: PRIVATE NETWORK & TENANT ISOLATION
    # =========================================================================
    private_network = InfrastructureNetwork(
        network_id="NET-PRIVATE-SECURE-001",
        name="Classified Defense Energy Microgrid",
        sector=InfrastructureSector.ELECTRICITY_NETWORKS,
        country="US",
        nodes=[
            NetworkNode("NODE-SEC-1", "NET-PRIVATE-SECURE-001", "Substation Alpha", "substation", 38.89, -77.03),
            NetworkNode("NODE-SEC-2", "NET-PRIVATE-SECURE-001", "Command Compound", "facility", 38.90, -77.04),
        ],
        edges=[
            NetworkEdge(
                edge_id="EDGE-SEC-FEEDER",
                network_id="NET-PRIVATE-SECURE-001",
                from_node_id="NODE-SEC-1",
                to_node_id="NODE-SEC-2",
                edge_type="underground_cable",
                coordinates=[[-77.03, 38.89], [-77.04, 38.90]],
                length_km=1.8,
            )
        ],
        is_private=True,
        tenant_id="TENANT-DEFENSE-CORP",
    )
    network_registry.register_network(private_network)

    private_asset = create_power_plant(
        asset_id="INF-PWR-PRIVATE-001",
        name="Classified Backup Generation Facility",
        country="US",
        latitude=38.8900,
        longitude=-77.0300,
        primary_fuel="diesel_backup",
        capacity_mw=25.0,
    )
    private_asset.is_private = True
    private_asset.tenant_id = "TENANT-DEFENSE-CORP"
    asset_registry.register_asset(private_asset)

    # =========================================================================
    # FIXTURE M: SOURCE LICENSE (Non-Commercial Dataset)
    # =========================================================================
    non_commercial_asset = create_mining_asset(
        asset_id="INF-MIN-NONCOMM-001",
        name="Academia Research Survey Deposit",
        country="CA",
        commodity="lithium",
        latitude=52.5000,
        longitude=-115.3000,
        rom_tonnes_year=120000.0,
        source_id="ACADEMIC_RESEARCH_SURVEY",
        source_license=LicensingClass.NON_COMMERCIAL_ONLY,
    )
    asset_registry.register_asset(non_commercial_asset)

    # =========================================================================
    # FIXTURE N: SOURCE REVOCATION TESTBED ASSET
    # =========================================================================
    revocable_asset = create_data_center_asset(
        asset_id="INF-DC-REVOCABLE-001",
        name="Metro Data Exchange Vault",
        country="US",
        latitude=39.0438,
        longitude=-77.4874,
        it_load_mw=45.0,
        total_power_mw=55.0,
        source_id="REVOCABLE_PROPRIETARY_FEED",
        source_license=LicensingClass.COMMERCIAL_ALLOWED,
    )
    asset_registry.register_asset(revocable_asset)

    # =========================================================================
    # GLOBAL INSTITUTIONAL ASSETS ACROSS REMAINING SECTORS
    # =========================================================================
    # World Ports
    rotterdam = create_port_facility(
        asset_id="INF-PRT-ROTTERDAM",
        name="Port of Rotterdam Maasvlakte II",
        country="NL",
        latitude=51.9540,
        longitude=4.0150,
        un_locode="NLRTM",
        teu_capacity=14500000.0,
        max_draft_meters=24.0,
        berth_count=22,
    )
    singapore_tuas = create_port_facility(
        asset_id="INF-PRT-TUAS-SG",
        name="Tuas Mega Port Singapore",
        country="SG",
        latitude=1.2650,
        longitude=103.6280,
        un_locode="SGSIN",
        teu_capacity=20000000.0,
        max_draft_meters=23.0,
        berth_count=18,
    )
    asset_registry.register_asset(rotterdam)
    asset_registry.register_asset(singapore_tuas)

    # World Airports
    jfk_airport = create_airport_facility(
        asset_id="INF-AIR-KJFK",
        name="John F. Kennedy International Airport",
        country="US",
        latitude=40.6413,
        longitude=-73.7781,
        icao_code="KJFK",
        iata_code="JFK",
        passengers_per_year=62000000.0,
        cargo_tonnes_year=1400000.0,
        runway_count=4,
    )
    london_heathrow = create_airport_facility(
        asset_id="INF-AIR-EGLL",
        name="London Heathrow Airport",
        country="GB",
        latitude=51.4700,
        longitude=-0.4543,
        icao_code="EGLL",
        iata_code="LHR",
        passengers_per_year=79200000.0,
        cargo_tonnes_year=1430000.0,
        runway_count=2,
    )
    asset_registry.register_asset(jfk_airport)
    asset_registry.register_asset(london_heathrow)

    # Hyperscale Data Centers
    ashburn_campus = create_data_center_asset(
        asset_id="INF-DC-ASHBURN-CAMPUS",
        name="Ashburn Quantum Park Hyperscale Campus",
        country="US",
        latitude=39.0150,
        longitude=-77.4650,
        it_load_mw=240.0,
        total_power_mw=300.0,
        gross_sqft=1200000.0,
        white_space_sqft=800000.0,
        asset_type=InfrastructureAssetType.DATA_CENTER_CAMPUS,
    )
    dublin_datacenter = create_data_center_asset(
        asset_id="INF-DC-DUBLIN-EAST",
        name="Grange Castle Cloud Data Center",
        country="IE",
        latitude=53.3150,
        longitude=-6.4400,
        it_load_mw=90.0,
        total_power_mw=110.0,
        gross_sqft=450000.0,
        white_space_sqft=280000.0,
    )
    asset_registry.register_asset(ashburn_campus)
    asset_registry.register_asset(dublin_datacenter)

    # World-Scale Mines
    escondida_copper = create_mining_asset(
        asset_id="INF-MIN-ESCONDIDA",
        name="Minera Escondida Copper Complex",
        country="CL",
        commodity="copper",
        latitude=-24.2670,
        longitude=-69.0700,
        asset_type=InfrastructureAssetType.OPEN_PIT_MINE,
        rom_tonnes_year=130000000.0,
        refined_tonnes_year=1100000.0,
        proved_reserves_tonnes=25000000.0,
    )
    greenbushes_lithium = create_mining_asset(
        asset_id="INF-MIN-GREENBUSHES",
        name="Greenbushes Lithium Mine",
        country="AU",
        commodity="lithium",
        latitude=-33.8600,
        longitude=116.0100,
        asset_type=InfrastructureAssetType.OPEN_PIT_MINE,
        rom_tonnes_year=4500000.0,
        refined_tonnes_year=380000.0,
    )
    asset_registry.register_asset(escondida_copper)
    asset_registry.register_asset(greenbushes_lithium)

    # Major Rail Assets
    bnsf_corridor = create_rail_asset(
        asset_id="INF-RAIL-BNSF-CHICAGO",
        name="Corwith Intermodal Rail Terminal",
        country="US",
        latitude=41.8150,
        longitude=-87.7100,
        track_length_km=48.5,
        annual_freight_tonnes=18500000.0,
    )
    asset_registry.register_asset(bnsf_corridor)

    # Major Logistics Hubs
    dallas_air_hub = create_logistics_asset(
        asset_id="INF-LOG-DFW-AIR-HUB",
        name="DFW Regional Logistics Gateway",
        country="US",
        latitude=32.9000,
        longitude=-97.0400,
        gross_sqft=2500000.0,
        warehouse_volume_m3=3000000.0,
    )
    asset_registry.register_asset(dallas_air_hub)


# Automatically seed on import
seed_infrastructure_system()
