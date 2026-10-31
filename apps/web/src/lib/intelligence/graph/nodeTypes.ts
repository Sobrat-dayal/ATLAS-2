/**
 * Node type configurations, icons, and display helpers (Stage 136).
 */

import { GraphNodeType } from './types';

export interface NodeTypeConfig {
  type: GraphNodeType;
  label: string;
  color: string;
  borderColor: string;
  bgColor: string;
  iconName: string;
}

export const NODE_TYPE_CONFIGS: Record<GraphNodeType, NodeTypeConfig> = {
  EVENT: {
    type: 'EVENT',
    label: 'Event',
    color: '#38bdf8', // sky-400
    borderColor: '#0284c7',
    bgColor: 'rgba(56, 189, 248, 0.15)',
    iconName: 'calendar',
  },
  COMPANY: {
    type: 'COMPANY',
    label: 'Company',
    color: '#34d399', // emerald-400
    borderColor: '#059669',
    bgColor: 'rgba(52, 211, 153, 0.15)',
    iconName: 'building',
  },
  ISSUER: {
    type: 'ISSUER',
    label: 'Issuer',
    color: '#10b981', // emerald-500
    borderColor: '#047857',
    bgColor: 'rgba(16, 185, 129, 0.15)',
    iconName: 'briefcase',
  },
  LEGAL_ENTITY: {
    type: 'LEGAL_ENTITY',
    label: 'Legal Entity',
    color: '#a78bfa', // purple-400
    borderColor: '#7c3aed',
    bgColor: 'rgba(167, 139, 250, 0.15)',
    iconName: 'shield',
  },
  FINANCIAL_INSTRUMENT: {
    type: 'FINANCIAL_INSTRUMENT',
    label: 'Instrument',
    color: '#60a5fa', // blue-400
    borderColor: '#2563eb',
    bgColor: 'rgba(96, 165, 250, 0.15)',
    iconName: 'trending-up',
  },
  SECTOR: {
    type: 'SECTOR',
    label: 'Sector',
    color: '#818cf8', // indigo-400
    borderColor: '#4f46e5',
    bgColor: 'rgba(129, 140, 248, 0.15)',
    iconName: 'pie-chart',
  },
  INDUSTRY: {
    type: 'INDUSTRY',
    label: 'Industry',
    color: '#c084fc', // purple-400
    borderColor: '#9333ea',
    bgColor: 'rgba(192, 132, 252, 0.15)',
    iconName: 'layers',
  },
  COUNTRY: {
    type: 'COUNTRY',
    label: 'Country',
    color: '#fbbf24', // amber-400
    borderColor: '#d97706',
    bgColor: 'rgba(251, 191, 36, 0.15)',
    iconName: 'globe',
  },
  ADMINISTRATIVE_REGION: {
    type: 'ADMINISTRATIVE_REGION',
    label: 'Region',
    color: '#f59e0b', // amber-500
    borderColor: '#b45309',
    bgColor: 'rgba(245, 158, 11, 0.15)',
    iconName: 'map-pin',
  },
  COMMODITY: {
    type: 'COMMODITY',
    label: 'Commodity',
    color: '#eab308', // yellow-500
    borderColor: '#a16207',
    bgColor: 'rgba(234, 179, 8, 0.15)',
    iconName: 'droplet',
  },
  ECONOMIC_INDICATOR: {
    type: 'ECONOMIC_INDICATOR',
    label: 'Indicator',
    color: '#2dd4bf', // teal-400
    borderColor: '#0d9488',
    bgColor: 'rgba(45, 212, 191, 0.15)',
    iconName: 'activity',
  },
  CENTRAL_BANK: {
    type: 'CENTRAL_BANK',
    label: 'Central Bank',
    color: '#f43f5e', // rose-500
    borderColor: '#be123c',
    bgColor: 'rgba(244, 63, 94, 0.15)',
    iconName: 'landmark',
  },
  REGULATORY_AUTHORITY: {
    type: 'REGULATORY_AUTHORITY',
    label: 'Regulator',
    color: '#f97316', // orange-500
    borderColor: '#c2410c',
    bgColor: 'rgba(249, 115, 22, 0.15)',
    iconName: 'scale',
  },
  CORPORATE_FACILITY: {
    type: 'CORPORATE_FACILITY',
    label: 'Facility',
    color: '#fb923c', // orange-400
    borderColor: '#ea580c',
    bgColor: 'rgba(251, 146, 60, 0.15)',
    iconName: 'home',
  },
  INFRASTRUCTURE_ASSET: {
    type: 'INFRASTRUCTURE_ASSET',
    label: 'Infrastructure',
    color: '#fdba74', // orange-300
    borderColor: '#f97316',
    bgColor: 'rgba(253, 186, 116, 0.15)',
    iconName: 'zap',
  },
  OTHER_SUPPORTED_CANONICAL_ENTITY: {
    type: 'OTHER_SUPPORTED_CANONICAL_ENTITY',
    label: 'Other Entity',
    color: '#94a3b8', // slate-400
    borderColor: '#475569',
    bgColor: 'rgba(148, 163, 184, 0.15)',
    iconName: 'circle',
  },
};
