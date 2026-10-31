/**
 * Sector Visual Styles, Color Constants, and Badges for Physical Infrastructure (Stage 133).
 */

import { InfrastructureSector, InfrastructureStatus, GeographicPrecisionClass } from './types';

export interface SectorVisualMeta {
  sector: InfrastructureSector;
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  iconName: string;
}

export const SECTOR_VISUALS: Record<InfrastructureSector, SectorVisualMeta> = {
  ports_maritime: {
    sector: 'ports_maritime',
    label: 'Ports & Maritime',
    color: '#0284c7',
    bgColor: 'rgba(2, 132, 199, 0.12)',
    borderColor: 'rgba(2, 132, 199, 0.4)',
    iconName: 'Anchor',
  },
  airports_aviation: {
    sector: 'airports_aviation',
    label: 'Airports & Aviation',
    color: '#38bdf8',
    bgColor: 'rgba(56, 189, 248, 0.12)',
    borderColor: 'rgba(56, 189, 248, 0.4)',
    iconName: 'Plane',
  },
  power_generation: {
    sector: 'power_generation',
    label: 'Power Generation',
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.12)',
    borderColor: 'rgba(245, 158, 11, 0.4)',
    iconName: 'Zap',
  },
  electricity_networks: {
    sector: 'electricity_networks',
    label: 'Electricity Networks',
    color: '#a855f7',
    bgColor: 'rgba(168, 85, 247, 0.12)',
    borderColor: 'rgba(168, 85, 247, 0.4)',
    iconName: 'Activity',
  },
  oil_gas: {
    sector: 'oil_gas',
    label: 'Oil & Gas Pipelines',
    color: '#f97316',
    bgColor: 'rgba(249, 115, 22, 0.12)',
    borderColor: 'rgba(249, 115, 22, 0.4)',
    iconName: 'Flame',
  },
  mining: {
    sector: 'mining',
    label: 'Mining & Resources',
    color: '#d97706',
    bgColor: 'rgba(217, 119, 6, 0.12)',
    borderColor: 'rgba(217, 119, 6, 0.4)',
    iconName: 'Layers',
  },
  data_centers: {
    sector: 'data_centers',
    label: 'Data Centers',
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.12)',
    borderColor: 'rgba(16, 185, 129, 0.4)',
    iconName: 'Server',
  },
  railways: {
    sector: 'railways',
    label: 'Rail Infrastructure',
    color: '#6366f1',
    bgColor: 'rgba(99, 102, 241, 0.12)',
    borderColor: 'rgba(99, 102, 241, 0.4)',
    iconName: 'Navigation',
  },
  logistics_industrial: {
    sector: 'logistics_industrial',
    label: 'Industrial Logistics',
    color: '#8b5cf6',
    bgColor: 'rgba(139, 92, 246, 0.12)',
    borderColor: 'rgba(139, 92, 246, 0.4)',
    iconName: 'Box',
  },
};

export const STATUS_STYLES: Record<string, { label: string; badgeClass: string }> = {
  operational: {
    label: 'Operational',
    badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  },
  under_construction: {
    label: 'Under Construction',
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  },
  proposed: {
    label: 'Proposed',
    badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  },
  decommissioned: {
    label: 'Decommissioned',
    badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  },
  suspended: {
    label: 'Suspended',
    badgeClass: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  },
  retired: {
    label: 'Retired',
    badgeClass: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
  },
  unknown: {
    label: 'Unknown',
    badgeClass: 'bg-zinc-700/20 text-zinc-500 border-zinc-700/30',
  },
};

export const PRECISION_STYLES: Record<string, { label: string; badgeClass: string }> = {
  exact_site: {
    label: 'Exact Surveyed Site',
    badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  },
  locality_centroid: {
    label: 'Locality Centroid',
    badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  },
  approximate: {
    label: 'Approximate Location',
    badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  },
  route_corridor: {
    label: 'Generalized Route Corridor',
    badgeClass: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  },
};
