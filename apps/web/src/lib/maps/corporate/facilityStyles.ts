/**
 * Accessible color taxonomy and visual styling for Corporate Facilities (Stage 132).
 */

import { CorporateFacilityStatus, CorporateFacilityType, GeographicPrecisionClass } from "./types";

export interface FacilityStyleDefinition {
  label: string;
  color: string;
  textColor: string;
  borderColor: string;
  iconName: string;
}

export const FACILITY_TYPE_STYLES: Record<CorporateFacilityType, FacilityStyleDefinition> = {
  CORPORATE_HEADQUARTERS: {
    label: "Corporate HQ",
    color: "#38bdf8",
    textColor: "text-sky-400",
    borderColor: "border-sky-500/40",
    iconName: "Building2",
  },
  REGISTERED_OFFICE: {
    label: "Registered Office",
    color: "#94a3b8",
    textColor: "text-slate-400",
    borderColor: "border-slate-500/40",
    iconName: "FileText",
  },
  REGIONAL_HEADQUARTERS: {
    label: "Regional HQ",
    color: "#818cf8",
    textColor: "text-indigo-400",
    borderColor: "border-indigo-500/40",
    iconName: "Building",
  },
  CORPORATE_OFFICE: {
    label: "Corporate Office",
    color: "#60a5fa",
    textColor: "text-blue-400",
    borderColor: "border-blue-500/40",
    iconName: "Briefcase",
  },
  MANUFACTURING_FACILITY: {
    label: "Manufacturing Plant",
    color: "#f59e0b",
    textColor: "text-amber-400",
    borderColor: "border-amber-500/40",
    iconName: "Factory",
  },
  ASSEMBLY_FACILITY: {
    label: "Assembly Plant",
    color: "#f97316",
    textColor: "text-orange-400",
    borderColor: "border-orange-500/40",
    iconName: "Cpu",
  },
  RESEARCH_AND_DEVELOPMENT: {
    label: "R&D Facility",
    color: "#10b981",
    textColor: "text-emerald-400",
    borderColor: "border-emerald-500/40",
    iconName: "FlaskConical",
  },
  DISTRIBUTION_CENTER: {
    label: "Distribution Center",
    color: "#a855f7",
    textColor: "text-purple-400",
    borderColor: "border-purple-500/40",
    iconName: "Truck",
  },
  WAREHOUSE: {
    label: "Warehouse",
    color: "#a1a1aa",
    textColor: "text-zinc-400",
    borderColor: "border-zinc-500/40",
    iconName: "Package",
  },
  CORPORATE_CAMPUS: {
    label: "Corporate Campus",
    color: "#14b8a6",
    textColor: "text-teal-400",
    borderColor: "border-teal-500/40",
    iconName: "Landmark",
  },
  CUSTOMER_SUPPORT_CENTER: {
    label: "Customer Support",
    color: "#f43f5e",
    textColor: "text-rose-400",
    borderColor: "border-rose-500/40",
    iconName: "Headphones",
  },
  SERVICE_CENTER: {
    label: "Service Center",
    color: "#eab308",
    textColor: "text-yellow-400",
    borderColor: "border-yellow-500/40",
    iconName: "Wrench",
  },
  OTHER_VERIFIED_FACILITY: {
    label: "Other Verified Facility",
    color: "#71717a",
    textColor: "text-zinc-400",
    borderColor: "border-zinc-600/40",
    iconName: "MapPin",
  },
};

export const FACILITY_STATUS_STYLES: Record<
  CorporateFacilityStatus,
  { label: string; bg: string; text: string; border: string }
> = {
  OPERATIONAL: {
    label: "Operational",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
  },
  ANNOUNCED: {
    label: "Announced",
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/30",
  },
  PLANNED: {
    label: "Planned",
    bg: "bg-purple-500/10",
    text: "text-purple-400",
    border: "border-purple-500/30",
  },
  UNDER_CONSTRUCTION: {
    label: "Under Construction",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/30",
  },
  TEMPORARILY_CLOSED: {
    label: "Temporarily Closed",
    bg: "bg-yellow-500/10",
    text: "text-yellow-400",
    border: "border-yellow-500/30",
  },
  PERMANENTLY_CLOSED: {
    label: "Permanently Closed",
    bg: "bg-rose-500/10",
    text: "text-rose-400",
    border: "border-rose-500/30",
  },
  SOLD: {
    label: "Sold / Divested",
    bg: "bg-zinc-800",
    text: "text-zinc-400",
    border: "border-zinc-700",
  },
  RELOCATED: {
    label: "Relocated",
    bg: "bg-zinc-800",
    text: "text-zinc-400",
    border: "border-zinc-700",
  },
  HISTORICAL: {
    label: "Historical Record",
    bg: "bg-slate-800",
    text: "text-slate-400",
    border: "border-slate-700",
  },
  STATUS_UNKNOWN: {
    label: "Status Unknown",
    bg: "bg-zinc-900",
    text: "text-zinc-500",
    border: "border-zinc-800",
  },
};

export const PRECISION_CLASS_INFO: Record<
  GeographicPrecisionClass,
  { label: string; badge: string; isApproximate: boolean; description: string }
> = {
  VERIFIED_SITE_POINT: {
    label: "Exact Site Point",
    badge: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
    isApproximate: false,
    description: "Verified physical entrance or building center point.",
  },
  VERIFIED_SITE_POLYGON: {
    label: "Verified Site Boundary",
    badge: "text-teal-400 border-teal-500/30 bg-teal-500/10",
    isApproximate: false,
    description: "Documented cadastral or campus boundary polygon.",
  },
  VERIFIED_STREET_ADDRESS: {
    label: "Verified Street Address",
    badge: "text-sky-400 border-sky-500/30 bg-sky-500/10",
    isApproximate: false,
    description: "Geocoded to verified street address with building number.",
  },
  GEOCODED_ADDRESS_APPROXIMATE: {
    label: "Approximate Street",
    badge: "text-yellow-400 border-yellow-500/30 bg-yellow-500/10",
    isApproximate: true,
    description: "Approximated to street or road segment.",
  },
  LOCALITY_CENTROID: {
    label: "City Centroid",
    badge: "text-amber-400 border-amber-500/30 bg-amber-500/10",
    isApproximate: true,
    description: "City or locality center point; exact facility coordinates unknown.",
  },
  ADMINISTRATIVE_REGION_ONLY: {
    label: "State / Region Only",
    badge: "text-orange-400 border-orange-500/30 bg-orange-500/10",
    isApproximate: true,
    description: "State or province level only.",
  },
  COUNTRY_ONLY: {
    label: "Country Only",
    badge: "text-rose-400 border-rose-500/30 bg-rose-500/10",
    isApproximate: true,
    description: "Country level only.",
  },
  LOCATION_UNRESOLVED: {
    label: "Unresolved Location",
    badge: "text-zinc-500 border-zinc-700 bg-zinc-800",
    isApproximate: true,
    description: "No geographic coordinates available in records.",
  },
};

