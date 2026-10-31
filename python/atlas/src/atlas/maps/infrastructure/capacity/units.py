"""Unit Dimensional Integrity and Conversion for ATLAS Infrastructure (Stage 133)."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Tuple

from atlas.maps.infrastructure.domain import CapacityMetric
from atlas.maps.infrastructure.errors import IncompatibleCapacityUnitError


class UnitDimension(str, Enum):
    """Physical dimensions for capacity and throughput."""

    POWER = "power"  # Rate of energy transfer (MW, GW, kW)
    ENERGY = "energy"  # Stored energy / production over time (MWh, GWh, kWh)
    MARITIME_CONTAINER = "maritime_container"  # TEU/year
    MARITIME_BULK = "maritime_bulk"  # Tonnes/year
    AVIATION_PASSENGERS = "aviation_passengers"  # Passengers/year
    AVIATION_CARGO = "aviation_cargo"  # Tonnes/year
    FLIGHT_MOVEMENTS = "flight_movements"  # Aircraft movements/year
    PIPELINE_LIQUID = "pipeline_liquid"  # Barrels per day
    PIPELINE_GAS = "pipeline_gas"  # Million cubic feet per day
    LIQUID_VOLUME = "liquid_volume"  # Barrels or m3
    MINING_ROM = "mining_rom"  # Run-of-mine tonnes/year
    MINING_REFINED = "mining_refined"  # Refined output tonnes/year
    MINING_RESERVES = "mining_reserves"  # Proved reserves tonnes
    MINING_RESOURCES = "mining_resources"  # Measured resources tonnes
    DC_IT_LOAD = "dc_it_load"  # IT equipment load MW
    DC_TOTAL_POWER = "dc_total_power"  # Total building power MW
    AREA = "area"  # Square feet
    DISTANCE = "distance"  # km
    COUNT = "count"  # Integer count (berths, runways)


# Mapping of metrics to their fundamental physical dimensions
METRIC_DIMENSION_MAP: Dict[CapacityMetric, UnitDimension] = {
    CapacityMetric.POWER_MW: UnitDimension.POWER,
    CapacityMetric.POWER_GW: UnitDimension.POWER,
    CapacityMetric.POWER_KW: UnitDimension.POWER,
    CapacityMetric.ENERGY_MWH: UnitDimension.ENERGY,
    CapacityMetric.ENERGY_GWH: UnitDimension.ENERGY,
    CapacityMetric.ENERGY_KWH: UnitDimension.ENERGY,
    CapacityMetric.THROUGHPUT_TEU_YEAR: UnitDimension.MARITIME_CONTAINER,
    CapacityMetric.THROUGHPUT_TONNES_YEAR: UnitDimension.MARITIME_BULK,
    CapacityMetric.BERTH_COUNT: UnitDimension.COUNT,
    CapacityMetric.MAX_DRAFT_METERS: UnitDimension.DISTANCE,
    CapacityMetric.PASSENGERS_YEAR: UnitDimension.AVIATION_PASSENGERS,
    CapacityMetric.CARGO_TONNES_YEAR: UnitDimension.AVIATION_CARGO,
    CapacityMetric.AIRCRAFT_MOVEMENTS_YEAR: UnitDimension.FLIGHT_MOVEMENTS,
    CapacityMetric.RUNWAY_COUNT: UnitDimension.COUNT,
    CapacityMetric.THROUGHPUT_BPD: UnitDimension.PIPELINE_LIQUID,
    CapacityMetric.THROUGHPUT_MMCFD: UnitDimension.PIPELINE_GAS,
    CapacityMetric.STORAGE_BARRELS: UnitDimension.LIQUID_VOLUME,
    CapacityMetric.STORAGE_M3: UnitDimension.LIQUID_VOLUME,
    CapacityMetric.RUN_OF_MINE_TONNES_YEAR: UnitDimension.MINING_ROM,
    CapacityMetric.REFINED_OUTPUT_TONNES_YEAR: UnitDimension.MINING_REFINED,
    CapacityMetric.PROVED_RESERVES_TONNES: UnitDimension.MINING_RESERVES,
    CapacityMetric.MEASURED_RESOURCES_TONNES: UnitDimension.MINING_RESOURCES,
    CapacityMetric.DATA_CENTER_IT_LOAD_MW: UnitDimension.DC_IT_LOAD,
    CapacityMetric.DATA_CENTER_TOTAL_POWER_MW: UnitDimension.DC_TOTAL_POWER,
    CapacityMetric.GROSS_FLOOR_AREA_SQFT: UnitDimension.AREA,
    CapacityMetric.WHITE_SPACE_SQFT: UnitDimension.AREA,
    CapacityMetric.TRACK_LENGTH_KM: UnitDimension.DISTANCE,
    CapacityMetric.ANNUAL_FREIGHT_TONNES: UnitDimension.MARITIME_BULK,
    CapacityMetric.WAREHOUSE_VOLUME_M3: UnitDimension.LIQUID_VOLUME,
}

# Scaling factors to canonical unit within dimension (e.g. POWER -> MW, ENERGY -> MWh)
UNIT_SCALING_FACTORS: Dict[CapacityMetric, Tuple[float, CapacityMetric]] = {
    CapacityMetric.POWER_MW: (1.0, CapacityMetric.POWER_MW),
    CapacityMetric.POWER_GW: (1000.0, CapacityMetric.POWER_MW),
    CapacityMetric.POWER_KW: (0.001, CapacityMetric.POWER_MW),
    CapacityMetric.ENERGY_MWH: (1.0, CapacityMetric.ENERGY_MWH),
    CapacityMetric.ENERGY_GWH: (1000.0, CapacityMetric.ENERGY_MWH),
    CapacityMetric.ENERGY_KWH: (0.001, CapacityMetric.ENERGY_MWH),
}


def get_metric_dimension(metric: CapacityMetric) -> UnitDimension:
    """Return the physical dimension of a capacity metric."""
    dim = METRIC_DIMENSION_MAP.get(metric)
    if dim is None:
        raise IncompatibleCapacityUnitError(str(metric), "UNKNOWN", "Metric lacks dimensional definition")
    return dim


def assert_compatible_dimensions(metric_a: CapacityMetric, metric_b: CapacityMetric) -> None:
    """Ensure two metrics share the same fundamental dimension before any mathematical operation."""
    dim_a = get_metric_dimension(metric_a)
    dim_b = get_metric_dimension(metric_b)
    if dim_a != dim_b:
        raise IncompatibleCapacityUnitError(
            metric_a.value,
            metric_b.value,
            f"Dimension mismatch: {dim_a.value} vs {dim_b.value}. Never add rate (power) and work/storage (energy).",
        )


def convert_to_canonical_unit(metric: CapacityMetric, value: float) -> Tuple[CapacityMetric, float]:
    """Convert value to canonical unit within its dimension (e.g. GW -> MW)."""
    if metric in UNIT_SCALING_FACTORS:
        factor, canonical_metric = UNIT_SCALING_FACTORS[metric]
        return canonical_metric, value * factor
    return metric, value
