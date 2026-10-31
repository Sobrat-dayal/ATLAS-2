/**
 * Category styling and taxonomy metadata for Universal Events (Stage 135)
 */

import { EventCategory, EventVerificationStatus, EventLifecycleStatus } from './types';

export interface CategoryMeta {
  label: string;
  badgeClass: string;
  borderClass: string;
  iconName: string;
}

export const CATEGORY_METADATA: Record<EventCategory, CategoryMeta> = {
  FINANCIAL: {
    label: 'Financial & Earnings',
    badgeClass: 'bg-emerald-950/80 text-emerald-400 border-emerald-800',
    borderClass: 'border-l-emerald-500',
    iconName: 'DollarSign',
  },
  CORPORATE: {
    label: 'Corporate Action',
    badgeClass: 'bg-blue-950/80 text-blue-400 border-blue-800',
    borderClass: 'border-l-blue-500',
    iconName: 'Building',
  },
  ECONOMIC: {
    label: 'Macroeconomic Release',
    badgeClass: 'bg-amber-950/80 text-amber-400 border-amber-800',
    borderClass: 'border-l-amber-500',
    iconName: 'TrendingUp',
  },
  MONETARY_POLICY: {
    label: 'Monetary Policy',
    badgeClass: 'bg-indigo-950/80 text-indigo-400 border-indigo-800',
    borderClass: 'border-l-indigo-500',
    iconName: 'Landmark',
  },
  REGULATORY: {
    label: 'Regulatory Order',
    badgeClass: 'bg-purple-950/80 text-purple-400 border-purple-800',
    borderClass: 'border-l-purple-500',
    iconName: 'Scale',
  },
  SANCTIONS: {
    label: 'Sanctions & Measures',
    badgeClass: 'bg-rose-950/80 text-rose-400 border-rose-800',
    borderClass: 'border-l-rose-500',
    iconName: 'ShieldAlert',
  },
  GEOPOLITICAL: {
    label: 'Geopolitical Action',
    badgeClass: 'bg-orange-950/80 text-orange-400 border-orange-800',
    borderClass: 'border-l-orange-500',
    iconName: 'Globe',
  },
  NEWS_REPORTED: {
    label: 'Media Reported',
    badgeClass: 'bg-zinc-800 text-zinc-300 border-zinc-700',
    borderClass: 'border-l-zinc-500',
    iconName: 'Newspaper',
  },
  NATURAL_DISASTER: {
    label: 'Natural Disaster',
    badgeClass: 'bg-red-950/80 text-red-400 border-red-800',
    borderClass: 'border-l-red-500',
    iconName: 'Activity',
  },
  PHYSICAL_WORLD: {
    label: 'Physical Observation',
    badgeClass: 'bg-cyan-950/80 text-cyan-400 border-cyan-800',
    borderClass: 'border-l-cyan-500',
    iconName: 'Eye',
  },
  INFRASTRUCTURE: {
    label: 'Infrastructure Event',
    badgeClass: 'bg-yellow-950/80 text-yellow-400 border-yellow-800',
    borderClass: 'border-l-yellow-500',
    iconName: 'Cpu',
  },
  OTHER_VERIFIED_EVENT: {
    label: 'Verified Event',
    badgeClass: 'bg-slate-800 text-slate-300 border-slate-700',
    borderClass: 'border-l-slate-500',
    iconName: 'CheckCircle',
  },
};

export const VERIFICATION_BADGES: Record<EventVerificationStatus, { label: string; className: string }> = {
  OFFICIALLY_CONFIRMED: {
    label: 'OFFICIALLY CONFIRMED',
    className: 'bg-emerald-950 text-emerald-400 border border-emerald-800',
  },
  INDEPENDENTLY_CORROBORATED: {
    label: 'CORROBORATED',
    className: 'bg-cyan-950 text-cyan-400 border border-cyan-800',
  },
  SOURCE_REPORTED: {
    label: 'SOURCE REPORTED',
    className: 'bg-blue-950 text-blue-400 border border-blue-800',
  },
  UNVERIFIED: {
    label: 'UNVERIFIED',
    className: 'bg-amber-950 text-amber-400 border border-amber-800',
  },
  CONFLICTED: {
    label: 'CONFLICTED',
    className: 'bg-rose-950 text-rose-400 border border-rose-800 animate-pulse',
  },
  REJECTED: {
    label: 'REJECTED / FRAUD',
    className: 'bg-red-950 text-red-400 border border-red-800 line-through',
  },
};

export const LIFECYCLE_BADGES: Record<EventLifecycleStatus, { label: string; className: string }> = {
  SCHEDULED: { label: 'SCHEDULED', className: 'text-amber-400 border-amber-800' },
  PROPOSED: { label: 'PROPOSED', className: 'text-purple-400 border-purple-800' },
  ANNOUNCED: { label: 'ANNOUNCED', className: 'text-blue-400 border-blue-800' },
  REPORTED: { label: 'REPORTED', className: 'text-cyan-400 border-cyan-800' },
  OCCURRED: { label: 'OCCURRED', className: 'text-emerald-400 border-emerald-800' },
  CONFIRMED: { label: 'CONFIRMED', className: 'text-emerald-400 border-emerald-800' },
  POSTPONED: { label: 'POSTPONED', className: 'text-yellow-400 border-yellow-800' },
  CANCELLED: { label: 'CANCELLED', className: 'text-zinc-500 border-zinc-700' },
  SUPERSEDED: { label: 'SUPERSEDED', className: 'text-zinc-400 border-zinc-700' },
  RETRACTED: { label: 'RETRACTED', className: 'text-red-400 border-red-800' },
  DISPUTED: { label: 'DISPUTED', className: 'text-rose-400 border-rose-800' },
  STATUS_UNKNOWN: { label: 'UNKNOWN', className: 'text-zinc-500 border-zinc-800' },
};
