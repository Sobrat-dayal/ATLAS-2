/**
 * Unit Dimensional Integrity and Formatters for ATLAS Infrastructure (Stage 133).
 */

import { CapacityBasis, CapacityMetric } from './types';

export const METRIC_LABELS: Record<string, string> = {
  power_mw: 'Power (MW)',
  power_gw: 'Power (GW)',
  power_kw: 'Power (kW)',
  energy_mwh: 'Stored Energy (MWh)',
  energy_gwh: 'Stored Energy (GWh)',
  energy_kwh: 'Stored Energy (kWh)',
  throughput_teu_year: 'Container Throughput (TEU/yr)',
  throughput_tonnes_year: 'Bulk Throughput (t/yr)',
  berth_count: 'Berths',
  max_draft_meters: 'Max Draft (m)',
  passengers_year: 'Annual Passengers',
  cargo_tonnes_year: 'Air Cargo (t/yr)',
  aircraft_movements_year: 'Aircraft Movements/yr',
  runway_count: 'Runways',
  throughput_bpd: 'Liquid Throughput (bpd)',
  throughput_mmcfd: 'Gas Throughput (MMcf/d)',
  storage_barrels: 'Storage (bbl)',
  storage_m3: 'Storage (m³)',
  run_of_mine_tonnes_year: 'Run-of-Mine (t/yr)',
  refined_output_tonnes_year: 'Refined Metal (t/yr)',
  proved_reserves_tonnes: 'Proved Reserves (t)',
  measured_resources_tonnes: 'Measured Resources (t)',
  data_center_it_load_mw: 'IT Load (MW)',
  data_center_total_power_mw: 'Total Power (MW)',
  gross_floor_area_sqft: 'Gross Area (sqft)',
  white_space_sqft: 'White Space (sqft)',
  track_length_km: 'Track Length (km)',
  annual_freight_tonnes: 'Rail Freight (t/yr)',
  warehouse_volume_m3: 'Storage Volume (m³)',
};

export const BASIS_LABELS: Record<string, string> = {
  nameplate: 'Nameplate',
  net_summer: 'Net Summer',
  net_winter: 'Net Winter',
  gross: 'Gross',
  design: 'Design',
  operational_peak: 'Operational Peak',
  permitted: 'Permitted',
  estimated: 'Estimated',
};

/**
 * Format capacity record into institutional-grade display string.
 * Strictly displays "Not available" when value is null or undefined (Fixture K).
 */
export function formatCapacityDisplay(
  value: number | null | undefined,
  metric: string,
  basis?: string,
  customUnit?: string
): string {
  if (value === null || value === undefined) {
    return 'Not available';
  }

  const formattedNum = Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 1,
  });

  const unit = customUnit || METRIC_LABELS[metric] || metric;
  const basisStr = basis && BASIS_LABELS[basis] ? ` (${BASIS_LABELS[basis]})` : '';

  return `${formattedNum} ${unit}${basisStr}`;
}

/**
 * Validates that two capacity metrics share the exact same physical dimension before any combination.
 */
export function areMetricsDimensionallyCompatible(metricA: string, metricB: string): boolean {
  const isPowerA = ['power_mw', 'power_gw', 'power_kw'].includes(metricA);
  const isPowerB = ['power_mw', 'power_gw', 'power_kw'].includes(metricB);
  if (isPowerA && isPowerB) return true;

  const isEnergyA = ['energy_mwh', 'energy_gwh', 'energy_kwh'].includes(metricA);
  const isEnergyB = ['energy_mwh', 'energy_gwh', 'energy_kwh'].includes(metricB);
  if (isEnergyA && isEnergyB) return true;

  return metricA === metricB;
}
