"""Canonical Domain Models for ATLAS Physical Infrastructure Intelligence (Stage 133)."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class InfrastructureSector(str, Enum):
    """Institutional physical infrastructure sectors."""

    PORTS_MARITIME = "ports_maritime"
    AIRPORTS_AVIATION = "airports_aviation"
    POWER_GENERATION = "power_generation"
    ELECTRICITY_NETWORKS = "electricity_networks"
    OIL_GAS = "oil_gas"
    MINING = "mining"
    DATA_CENTERS = "data_centers"
    RAILWAYS = "railways"
    LOGISTICS_INDUSTRIAL = "logistics_industrial"


class InfrastructureAssetType(str, Enum):
    """Canonical physical infrastructure asset types."""

    # Ports & Maritime
    PORT_TERMINAL = "port_terminal"
    CONTAINER_TERMINAL = "container_terminal"
    BULK_TERMINAL = "bulk_terminal"
    CRUISE_TERMINAL = "cruise_terminal"
    BERTH = "berth"
    TRADE_LOCATION = "trade_location"

    # Airports & Aviation
    AIRPORT = "airport"
    AIRFIELD = "airfield"
    CARGO_TERMINAL = "cargo_terminal"
    RUNWAY = "runway"

    # Power Generation
    POWER_PLANT = "power_plant"
    GENERATING_UNIT = "generating_unit"
    BATTERY_STORAGE = "battery_storage"
    HYDRO_DAM = "hydro_dam"
    NUCLEAR_REACTOR = "nuclear_reactor"
    SOLAR_FARM = "solar_farm"
    WIND_FARM = "wind_farm"

    # Electricity Networks
    TRANSMISSION_LINE = "transmission_line"
    TRANSMISSION_SUBSTATION = "transmission_substation"
    GRID_INTERCONNECTION = "grid_interconnection"

    # Oil & Gas
    PIPELINE_ROUTE = "pipeline_route"
    PIPELINE_SEGMENT = "pipeline_segment"
    COMPRESSOR_STATION = "compressor_station"
    PUMPING_STATION = "pumping_station"
    LNG_TERMINAL = "lng_terminal"
    REFINERY = "refinery"
    OIL_STORAGE_DEPOT = "oil_storage_depot"

    # Mining
    OPEN_PIT_MINE = "open_pit_mine"
    UNDERGROUND_MINE = "underground_mine"
    PROCESSING_PLANT = "processing_plant"
    SMELTER_REFINERY = "smelter_refinery"
    TAILINGS_FACILITY = "tailings_facility"

    # Data Centers
    DATA_CENTER_CAMPUS = "data_center_campus"
    DATA_CENTER_FACILITY = "data_center_facility"

    # Railways
    RAIL_LINE = "rail_line"
    RAIL_STATION = "rail_station"
    INTERMODAL_RAIL_YARD = "intermodal_rail_yard"
    MARSHALLING_YARD = "marshalling_yard"

    # Logistics & Industrial
    DISTRIBUTION_CENTER = "distribution_center"
    BONDED_WAREHOUSE = "bonded_warehouse"
    FREIGHT_TERMINAL = "freight_terminal"
    LOGISTICS_PARK = "logistics_park"


class InfrastructureStatus(str, Enum):
    """Operational status of physical infrastructure assets."""

    OPERATIONAL = "operational"
    UNDER_CONSTRUCTION = "under_construction"
    PROPOSED = "proposed"
    DECOMMISSIONED = "decommissioned"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    UNKNOWN = "unknown"


class CapacityMetric(str, Enum):
    """Dimensional capacity and throughput metrics."""

    # Power (Rate of energy transfer)
    POWER_MW = "power_mw"
    POWER_GW = "power_gw"
    POWER_KW = "power_kw"

    # Energy (Stored work or production over time)
    ENERGY_MWH = "energy_mwh"
    ENERGY_GWH = "energy_gwh"
    ENERGY_KWH = "energy_kwh"

    # Ports & Maritime
    THROUGHPUT_TEU_YEAR = "throughput_teu_year"
    THROUGHPUT_TONNES_YEAR = "throughput_tonnes_year"
    BERTH_COUNT = "berth_count"
    MAX_DRAFT_METERS = "max_draft_meters"

    # Airports & Aviation
    PASSENGERS_YEAR = "passengers_year"
    CARGO_TONNES_YEAR = "cargo_tonnes_year"
    AIRCRAFT_MOVEMENTS_YEAR = "aircraft_movements_year"
    RUNWAY_COUNT = "runway_count"

    # Pipelines & Refineries
    THROUGHPUT_BPD = "throughput_bpd"
    THROUGHPUT_MMCFD = "throughput_mmcfd"
    STORAGE_BARRELS = "storage_barrels"
    STORAGE_M3 = "storage_m3"

    # Mining
    RUN_OF_MINE_TONNES_YEAR = "run_of_mine_tonnes_year"
    REFINED_OUTPUT_TONNES_YEAR = "refined_output_tonnes_year"
    PROVED_RESERVES_TONNES = "proved_reserves_tonnes"
    MEASURED_RESOURCES_TONNES = "measured_resources_tonnes"

    # Data Centers
    DATA_CENTER_IT_LOAD_MW = "data_center_it_load_mw"
    DATA_CENTER_TOTAL_POWER_MW = "data_center_total_power_mw"
    GROSS_FLOOR_AREA_SQFT = "gross_floor_area_sqft"
    WHITE_SPACE_SQFT = "white_space_sqft"

    # Rail & Logistics
    TRACK_LENGTH_KM = "track_length_km"
    ANNUAL_FREIGHT_TONNES = "annual_freight_tonnes"
    WAREHOUSE_VOLUME_M3 = "warehouse_volume_m3"


class CapacityBasis(str, Enum):
    """Institutional basis/condition of reported capacity."""

    NAMEPLATE = "nameplate"
    NET_SUMMER = "net_summer"
    NET_WINTER = "net_winter"
    GROSS = "gross"
    DESIGN = "design"
    OPERATIONAL_PEAK = "operational_peak"
    PERMITTED = "permitted"
    ESTIMATED = "estimated"


class GeographicPrecisionClass(str, Enum):
    """Spatial resolution and fidelity classification."""

    EXACT_SITE = "exact_site"
    LOCALITY_CENTROID = "locality_centroid"
    APPROXIMATE = "approximate"
    ROUTE_CORRIDOR = "route_corridor"


class EntityRole(str, Enum):
    """Relationship between an institutional company and an infrastructure asset."""

    OWNER = "owner"
    OPERATOR = "operator"
    DEVELOPER = "developer"
    CONCESSION_HOLDER = "concession_holder"
    OFF_TAKER = "off_taker"
    EQUITY_PARTNER = "equity_partner"


class ConnectivityClass(str, Enum):
    """Evidence grade for network edge connectivity."""

    VERIFIED = "verified"
    CANDIDATE = "candidate"
    INFERRED = "inferred"
    DISCONNECTED = "disconnected"


class LicensingClass(str, Enum):
    """Source licensing and entitlement constraints."""

    COMMERCIAL_ALLOWED = "commercial_allowed"
    NON_COMMERCIAL_ONLY = "non_commercial_only"
    RESTRICTED = "restricted"


@dataclass
class InfrastructureCapacityRecord:
    """Individual typed capacity or throughput record with strict basis tracking."""

    metric: CapacityMetric
    value: float
    basis: CapacityBasis
    unit_str: str
    reporting_year: Optional[int] = None
    evidence_source: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric.value,
            "value": self.value,
            "basis": self.basis.value,
            "unit_str": self.unit_str,
            "reporting_year": self.reporting_year,
            "evidence_source": self.evidence_source,
            "notes": self.notes,
        }


@dataclass
class InfrastructureStatusHistory:
    """Auditable historical status transition for point-in-time state evaluation."""

    status: InfrastructureStatus
    effective_date: str  # YYYY-MM-DD
    evidence_source: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "effective_date": self.effective_date,
            "evidence_source": self.evidence_source,
            "notes": self.notes,
        }


@dataclass
class InfrastructureEntityLink:
    """Explicit, source-backed linkage between a company/financial entity and an asset."""

    entity_id: str
    entity_name: str
    role: EntityRole
    ownership_pct: Optional[float] = None
    effective_from: Optional[str] = None  # YYYY-MM-DD
    effective_to: Optional[str] = None  # YYYY-MM-DD
    evidence_source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "role": self.role.value,
            "ownership_pct": self.ownership_pct,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "evidence_source": self.evidence_source,
        }


@dataclass
class NetworkNode:
    """Point entity in an infrastructure topology network."""

    node_id: str
    network_id: str
    name: str
    node_type: str
    latitude: float
    longitude: float
    asset_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "network_id": self.network_id,
            "name": self.name,
            "node_type": self.node_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "asset_id": self.asset_id,
            "properties": self.properties,
        }


@dataclass
class NetworkEdge:
    """Directed or bidirectional edge representing an actual physical conduit or line."""

    edge_id: str
    network_id: str
    from_node_id: str
    to_node_id: str
    edge_type: str
    coordinates: List[List[float]] = field(default_factory=list)  # [[lng, lat], ...]
    length_km: Optional[float] = None
    capacity_value: Optional[float] = None
    capacity_unit: Optional[str] = None
    voltage_kv: Optional[float] = None
    diameter_inches: Optional[float] = None
    bidirectional: bool = True
    connectivity_evidence: ConnectivityClass = ConnectivityClass.VERIFIED
    source_id: str = "OFFICIAL"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "network_id": self.network_id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "edge_type": self.edge_type,
            "coordinates": self.coordinates,
            "length_km": self.length_km,
            "capacity_value": self.capacity_value,
            "capacity_unit": self.capacity_unit,
            "voltage_kv": self.voltage_kv,
            "diameter_inches": self.diameter_inches,
            "bidirectional": self.bidirectional,
            "connectivity_evidence": self.connectivity_evidence.value,
            "source_id": self.source_id,
            "properties": self.properties,
        }


@dataclass
class InfrastructureNetwork:
    """Canonical network container grouping nodes, edges and topology rules."""

    network_id: str
    name: str
    sector: InfrastructureSector
    country: str
    nodes: List[NetworkNode] = field(default_factory=list)
    edges: List[NetworkEdge] = field(default_factory=list)
    is_private: bool = False
    tenant_id: Optional[str] = None
    license_class: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "network_id": self.network_id,
            "name": self.name,
            "sector": self.sector.value,
            "country": self.country,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "is_private": self.is_private,
            "tenant_id": self.tenant_id,
            "license_class": self.license_class.value,
            "properties": self.properties,
        }


@dataclass
class InfrastructureAsset:
    """Authoritative physical infrastructure asset record."""

    asset_id: str
    name: str
    sector: InfrastructureSector
    asset_type: InfrastructureAssetType
    country: str  # ISO 3166-1 alpha-2 / alpha-3
    latitude: float
    longitude: float
    region: Optional[str] = None
    geometry: Dict[str, Any] = field(default_factory=dict)
    precision: GeographicPrecisionClass = GeographicPrecisionClass.EXACT_SITE
    is_approximate_route: bool = False
    status: InfrastructureStatus = InfrastructureStatus.OPERATIONAL
    status_history: List[InfrastructureStatusHistory] = field(default_factory=list)
    parent_asset_id: Optional[str] = None
    child_asset_ids: List[str] = field(default_factory=list)
    capacity_records: List[InfrastructureCapacityRecord] = field(default_factory=list)
    entity_links: List[InfrastructureEntityLink] = field(default_factory=list)
    identifiers: Dict[str, str] = field(default_factory=dict)
    source_id: str = "OFFICIAL"
    source_license: LicensingClass = LicensingClass.COMMERCIAL_ALLOWED
    is_private: bool = False
    tenant_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def get_status_as_of(self, as_of_date: str) -> InfrastructureStatus:
        """Evaluate factual operational status as of a specific calendar date (YYYY-MM-DD)."""
        if not self.status_history:
            return self.status

        # Sort history chronologically
        sorted_history = sorted(self.status_history, key=lambda h: h.effective_date)
        applicable_status = InfrastructureStatus.UNKNOWN

        for entry in sorted_history:
            if entry.effective_date <= as_of_date:
                applicable_status = entry.status
            else:
                break

        return applicable_status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "name": self.name,
            "sector": self.sector.value,
            "asset_type": self.asset_type.value,
            "country": self.country,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "geometry": self.geometry,
            "precision": self.precision.value,
            "is_approximate_route": self.is_approximate_route,
            "status": self.status.value,
            "status_history": [h.to_dict() for h in self.status_history],
            "parent_asset_id": self.parent_asset_id,
            "child_asset_ids": self.child_asset_ids,
            "capacity_records": [c.to_dict() for c in self.capacity_records],
            "entity_links": [l.to_dict() for l in self.entity_links],
            "identifiers": self.identifiers,
            "source_id": self.source_id,
            "source_license": self.source_license.value,
            "is_private": self.is_private,
            "tenant_id": self.tenant_id,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

