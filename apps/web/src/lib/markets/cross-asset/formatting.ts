/**
 * Formatting and display helpers for ATLAS Cross-Asset Markets V1.
 */

import {
  AssetClass,
  CrossAssetMode,
  CrossAssetWindow,
  NativeMetricKind,
} from "./types";

export function formatNumber(
  val: number | string | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";
  return num.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercentChange(
  pct: number | string | null | undefined,
  includePlus: boolean = true
): string {
  if (pct === null || pct === undefined || pct === "") return "—";
  const num = typeof pct === "string" ? parseFloat(pct) : pct;
  if (isNaN(num)) return "—";
  const prefix = num > 0 && includePlus ? "+" : "";
  return `${prefix}${num.toFixed(2)}%`;
}

export function formatNativeChange(
  changeValue: number | string | null | undefined,
  changePercent: number | string | null | undefined,
  metricKind: NativeMetricKind,
  unit: string
): string {
  if (metricKind === "BOND_YIELD_BPS_CHANGE") {
    if (changeValue === null || changeValue === undefined) return "—";
    const num = typeof changeValue === "string" ? parseFloat(changeValue) : changeValue;
    const prefix = num > 0 ? "+" : "";
    return `${prefix}${num.toFixed(1)} bps`;
  }

  if (changePercent !== null && changePercent !== undefined) {
    const pNum = typeof changePercent === "string" ? parseFloat(changePercent) : changePercent;
    if (!isNaN(pNum)) {
      const prefix = pNum > 0 ? "+" : "";
      return `${prefix}${pNum.toFixed(2)}%`;
    }
  }

  if (changeValue !== null && changeValue !== undefined) {
    const cNum = typeof changeValue === "string" ? parseFloat(changeValue) : changeValue;
    if (!isNaN(cNum)) {
      const prefix = cNum > 0 ? "+" : "";
      return `${prefix}${cNum.toFixed(2)} ${unit}`;
    }
  }

  return "—";
}

export function formatIndexedValue(val: number | string | null | undefined): string {
  if (val === null || val === undefined) return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";
  return num.toFixed(2);
}

export function formatIsoTime(isoStr: string | null | undefined): string {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr);
    return d.toISOString().replace("T", " ").substring(11, 19) + " UTC";
  } catch {
    return isoStr;
  }
}

export function getAssetClassColor(assetClass: AssetClass): {
  bg: string;
  text: string;
  border: string;
} {
  switch (assetClass) {
    case "equities":
      return {
        bg: "bg-blue-950/40",
        text: "text-blue-400",
        border: "border-blue-800/40",
      };
    case "etfs":
      return {
        bg: "bg-indigo-950/40",
        text: "text-indigo-400",
        border: "border-indigo-800/40",
      };
    case "fx":
      return {
        bg: "bg-teal-950/40",
        text: "text-teal-400",
        border: "border-teal-800/40",
      };
    case "crypto":
      return {
        bg: "bg-amber-950/40",
        text: "text-amber-400",
        border: "border-amber-800/40",
      };
    case "bonds":
      return {
        bg: "bg-purple-950/40",
        text: "text-purple-400",
        border: "border-purple-800/40",
      };
    case "futures":
      return {
        bg: "bg-emerald-950/40",
        text: "text-emerald-400",
        border: "border-emerald-800/40",
      };
    default:
      return {
        bg: "bg-zinc-800/40",
        text: "text-zinc-400",
        border: "border-zinc-700/40",
      };
  }
}

export function getModeLabel(mode: CrossAssetMode): string {
  switch (mode) {
    case "native_overview":
      return "Native Market Overview";
    case "aligned_performance":
      return "Aligned Price Performance";
    default:
      return mode;
  }
}

export function getWindowLabel(window: CrossAssetWindow): string {
  switch (window) {
    case "last_24h":
      return "Previous 24 Hours";
    case "last_7d":
      return "Previous 7 Days";
    case "last_30d":
      return "Previous 30 Days";
    default:
      return window;
  }
}
