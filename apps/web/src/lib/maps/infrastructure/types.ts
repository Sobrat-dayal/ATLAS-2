/**
 * Canonical TypeScript Types for ATLAS Physical Infrastructure Intelligence (Stage 133).
 */

export type InfrastructureSector =
  | 'ports_maritime'
  | 'airports_aviation'
  | 'power_generation'
  | 'electricity_networks'
  | 'oil_gas'
  | 'mining'
  | 'data_centers'
  | 'railways'
  | 'logistics_industrial';

export type InfrastructureAssetType =
  | 'port_terminal'
  | 'container_terminal'
  | 'bulk_terminal'
  | 'cruise_terminal'
  | 'berth'
  | 'trade_location'
  | 'airport'
  | 'airfield'
  | 'cargo_terminal'
  | 'runway'
  | 'power_plant'
  | 'generating_unit'
  | 'battery_storage'
  | 'hydro_dam'
  | 'nuclear_reactor'
  | 'solar_farm'
  | 'wind_farm'
  | 'transmission_line'
  | 'transmission_substation'
  | 'grid_interconnection'
  | 'pipeline_route'
  | 'pipeline_segment'
  | 'compressor_station'
  | 'pumping_station'
  | 'lng_terminal'
  | 'refinery'
  | 'oil_storage_depot'
  | 'open_pit_mine'
  | 'underground_mine'
  | 'processing_plant'
  | 'smelter_refinery'
  | 'tailings_facility'
  | 'data_center_campus'
  | 'data_center_facility'
  | 'rail_line'
  | 'rail_station'
  | 'intermodal_rail_yard'
  | 'marshalling_yard'
  | 'distribution_center'
  | 'bonded_warehouse'
  | 'freight_terminal'
  | 'logistics_park';

export type InfrastructureStatus =
  | 'operational'
  | 'under_construction'
  | 'proposed'
  | 'decommissioned'
  | 'suspended'
  | 'retired'
  | 'unknown';

export type CapacityMetric =
  | 'power_mw'
  | 'power_gw'
  | 'power_kw'
  | 'energy_mwh'
  | 'energy_gwh'
  | 'energy_kwh'
  | 'throughput_teu_year'
  | 'throughput_tonnes_year'
  | 'berth_count'
  | 'max_draft_meters'
  | 'passengers_year'
  | 'cargo_tonnes_year'
  | 'aircraft_movements_year'
  | 'runway_count'
  | 'throughput_bpd'
  | 'throughput_mmcfd'
  | 'storage_barrels'
  | 'storage_m3'
  | 'run_of_mine_tonnes_year'
  | 'refined_output_tonnes_year'
  | 'proved_reserves_tonnes'
  | 'measured_resources_tonnes'
  | 'data_center_it_load_mw'
  | 'data_center_total_power_mw'
  | 'gross_floor_area_sqft'
  | 'white_space_sqft'
  | 'track_length_km'
  | 'annual_freight_tonnes'
  | 'warehouse_volume_m3';

export type CapacityBasis =
  | 'nameplate'
  | 'net_summer'
  | 'net_winter'
  | 'gross'
  | 'design'
  | 'operational_peak'
  | 'permitted'
  | 'estimated';

export type GeographicPrecisionClass =
  | 'exact_site'
  | 'locality_centroid'
  | 'approximate'
  | 'route_corridor';

export type EntityRole =
  | 'owner'
  | 'operator'
  | 'developer'
  | 'concession_holder'
  | 'off_taker'
  | 'equity_partner';

export type ConnectivityClass =
  | 'verified'
  | 'candidate'
  | 'inferred'
  | 'disconnected';

export type LicensingClass =
  | 'commercial_allowed'
  | 'non_commercial_only'
  | 'restricted';

export interface InfrastructureCapacityRecord {
  metric: CapacityMetric | string;
  value: number | null;
  basis: CapacityBasis | string;
  unit_str: string;
  reporting_year?: number | null;
  evidence_source?: string | null;
  notes?: string | null;
}

export interface InfrastructureStatusHistory {
  status: InfrastructureStatus | string;
  effective_date: string;
  evidence_source?: string | null;
  notes?: string | null;
}

export interface InfrastructureEntityLink {
  entity_id: string;
  entity_name: string;
  role: EntityRole | string;
  ownership_pct?: number | null;
  effective_from?: string | null;
  effective_to?: string | null;
  evidence_source?: string | null;
}

export interface NetworkNode {
  node_id: string;
  network_id: string;
  name: string;
  node_type: string;
  latitude: number;
  longitude: number;
  asset_id?: string | null;
  properties?: Record<string, any>;
}

export interface NetworkEdge {
  edge_id: string;
  network_id: string;
  from_node_id: string;
  to_node_id: string;
  edge_type: string;
  coordinates?: number[][];
  length_km?: number | null;
  capacity_value?: number | null;
  capacity_unit?: string | null;
  voltage_kv?: number | null;
  diameter_inches?: number | null;
  bidirectional?: boolean;
  connectivity_evidence?: ConnectivityClass | string;
  source_id?: string;
  properties?: Record<string, any>;
}

export interface InfrastructureNetwork {
  network_id: string;
  name: string;
  sector: InfrastructureSector | string;
  country: string;
  node_count?: number;
  edge_count?: number;
  nodes?: NetworkNode[];
  edges?: NetworkEdge[];
  is_private?: boolean;
  tenant_id?: string | null;
  license_class?: LicensingClass | string;
  properties?: Record<string, any>;
}

export interface InfrastructureAsset {
  asset_id: string;
  name: string;
  sector: InfrastructureSector | string;
  asset_type: InfrastructureAssetType | string;
  country: string;
  region?: string | null;
  latitude: number;
  longitude: number;
  geometry?: Record<string, any>;
  precision: GeographicPrecisionClass | string;
  is_approximate_route: boolean;
  status: InfrastructureStatus | string;
  status_history?: InfrastructureStatusHistory[];
  parent_asset_id?: string | null;
  child_asset_ids?: string[];
  capacity_records: InfrastructureCapacityRecord[];
  entity_links: InfrastructureEntityLink[];
  identifiers?: Record<string, string>;
  source_id: string;
  source_license: LicensingClass | string;
  is_private?: boolean;
  tenant_id?: string | null;
  properties?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface H3InfrastructureCell {
  cell_id: string;
  resolution: number;
  facility_count: number;
  unit_count: number;
  total_records: number;
  density_per_km2: number;
  cell_area_km2: number;
  capacities: Record<string, number>;
  sectors: string[];
  asset_ids: string[];
}

export interface RegionalSummary {
  region_name: string;
  total_assets: number;
  facility_count: number;
  unit_count: number;
  sector_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
  capacity_by_sector: Record<string, Record<string, number>>;
  source_coverage: {
    distinct_sources: number;
    source_record_counts: Record<string, number>;
  };
}

export interface CompanyInfrastructureExposure {
  company_id: string;
  total_linked_assets: number;
  owned_asset_count: number;
  operated_asset_count: number;
  other_linked_count: number;
  sector_exposure: Record<string, number>;
  country_exposure: Record<string, number>;
  capacity_by_role: Record<string, Record<string, number>>;
  owned_assets: InfrastructureAsset[];
  operated_assets: InfrastructureAsset[];
}
