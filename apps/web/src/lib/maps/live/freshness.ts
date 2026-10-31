/**
 * ATLAS Maps Live Physical-World Freshness & Presentation Utilities (Stage 134).
 */

import { FreshnessState, LiveObservationCategory, ObservationDataClass, ProviderStatus } from "./types";

export function formatFreshnessAge(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s ago`;
  }
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) {
    return `${minutes}m ago`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours}h ${minutes % 60}m ago`;
  }
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function getFreshnessBadge(state: FreshnessState): {
  label: string;
  bg: string;
  text: string;
  border: string;
} {
  switch (state) {
    case "CURRENT":
      return {
        label: "CURRENT",
        bg: "bg-emerald-500/10",
        text: "text-emerald-400",
        border: "border-emerald-500/30",
      };
    case "DELAYED":
      return {
        label: "DELAYED",
        bg: "bg-amber-500/10",
        text: "text-amber-400",
        border: "border-amber-500/30",
      };
    case "STALE":
      return {
        label: "STALE",
        bg: "bg-orange-500/10",
        text: "text-orange-400",
        border: "border-orange-500/30",
      };
    case "EXPIRED":
      return {
        label: "EXPIRED",
        bg: "bg-zinc-500/10",
        text: "text-zinc-400",
        border: "border-zinc-500/30",
      };
    case "HISTORICAL":
      return {
        label: "HISTORICAL",
        bg: "bg-blue-500/10",
        text: "text-blue-400",
        border: "border-blue-500/30",
      };
    case "SOURCE_UNAVAILABLE":
    default:
      return {
        label: "UNAVAILABLE",
        bg: "bg-rose-500/10",
        text: "text-rose-400",
        border: "border-rose-500/30",
      };
  }
}

export function getProviderStatusBadge(status: ProviderStatus): {
  label: string;
  color: string;
  dotColor: string;
} {
  switch (status) {
    case "ONLINE":
      return { label: "ONLINE", color: "text-emerald-400", dotColor: "bg-emerald-400" };
    case "DEGRADED":
      return { label: "DEGRADED", color: "text-amber-400", dotColor: "bg-amber-400" };
    case "OFFLINE":
      return { label: "OFFLINE", color: "text-rose-400", dotColor: "bg-rose-400" };
    case "UNCONFIGURED":
      return { label: "UNCONFIGURED", color: "text-zinc-400", dotColor: "bg-zinc-500" };
    case "ACCESS_RESTRICTED":
      return { label: "RESTRICTED", color: "text-purple-400", dotColor: "bg-purple-400" };
    default:
      return { label: "UNKNOWN", color: "text-zinc-400", dotColor: "bg-zinc-400" };
  }
}

export function getDataClassBadge(dataClass: ObservationDataClass): {
  label: string;
  tag: string;
  color: string;
} {
  switch (dataClass) {
    case "OBSERVED":
      return {
        label: "PHYSICAL MEASUREMENT",
        tag: "OBSERVED",
        color: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
      };
    case "PROPAGATED":
      return {
        label: "ORBITAL PROPAGATION",
        tag: "PROPAGATED",
        color: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
      };
    case "FORECAST":
      return {
        label: "ATMOSPHERIC MODEL",
        tag: "FORECAST",
        color: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      };
    case "REFERENCE":
    default:
      return {
        label: "STATIC REFERENCE",
        tag: "REFERENCE",
        color: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
      };
  }
}

export function getCategoryLabel(category: LiveObservationCategory): string {
  switch (category) {
    case "AIRCRAFT":
      return "Flights (ADS-B)";
    case "VESSEL":
      return "Vessels (AIS)";
    case "SATELLITE":
      return "Satellites (SGP4)";
    case "WEATHER_ALERT":
      return "Weather Alerts (CAP)";
    case "WEATHER_OBSERVATION":
      return "Surface Weather";
    case "WEATHER_FORECAST":
      return "Weather Forecast";
    case "EARTHQUAKE":
      return "Earthquakes (USGS)";
    case "ACTIVE_FIRE":
      return "Thermal Hotspots (FIRMS)";
    case "NATURAL_EVENT":
      return "Natural Events (EONET)";
    default:
      return category;
  }
}
