/**
 * Compatibility Validation and Entitlement Verification Engine for ATLAS Chart Synchronization (Stage 73).
 *
 * Implements:
 * - Canonical instrument series compatibility checks
 * - Market data entitlement preflight (no privilege escalation across panels)
 * - Series-specific interval availability verification
 * - Chart-type data capability checks (OHLC requirements)
 * - Strict drawing synchronization compatibility gate (identical canonical series & quotation unit)
 * - Honest, informative error reporting without silent substitutions
 */

import {
  ChartInstrumentMetadata,
  ChartRenderMode,
} from "../types";
import {
  ChartSyncCapabilities,
  SyncApplyResult,
} from "./types";

export interface InstrumentValidationResult {
  isCompatible: boolean;
  reason?: string;
}

export interface IntervalValidationResult {
  isCompatible: boolean;
  reason?: string;
}

export interface ChartTypeValidationResult {
  isCompatible: boolean;
  reason?: string;
}

export interface DrawingCompatibilityResult {
  isCompatible: boolean;
  reason?: string;
}

/**
 * Validate if a target panel can adopt an incoming canonical instrument.
 */
export function validateInstrumentSync(
  sourceInstrument: ChartInstrumentMetadata,
  targetPanelId: string,
  userEntitlements?: Record<string, boolean>
): InstrumentValidationResult {
  if (!sourceInstrument || !sourceInstrument.entity_id) {
    return {
      isCompatible: false,
      reason: "Invalid source instrument metadata: missing canonical entity ID",
    };
  }

  // Verify entitlement permissions if entitlement mapping is provided
  if (userEntitlements) {
    const isEntitled =
      userEntitlements[sourceInstrument.entity_id] ??
      userEntitlements[sourceInstrument.display_symbol] ??
      true;
    if (!isEntitled) {
      return {
        isCompatible: false,
        reason: `Target panel ${targetPanelId} lacks required market data entitlement for ${sourceInstrument.display_symbol}`,
      };
    }
  }

  return { isCompatible: true };
}

/**
 * Validate if a target panel supports the requested interval.
 */
export function validateIntervalSync(
  targetSymbol: string,
  requestedInterval: string,
  targetSupportedIntervals: string[]
): IntervalValidationResult {
  // In financial charting, '1m' is 1-minute while '1M' is 1-Month.
  // Matching must preserve case for 'm' (minute) vs 'M' (month).
  const isSupported = targetSupportedIntervals.some((intv) => {
    if (intv === requestedInterval) return true;
    // For non-minute/month intervals (e.g. 1d vs 1D, 1w vs 1W), allow case-insensitivity
    if (
      !intv.includes("m") &&
      !intv.includes("M") &&
      !requestedInterval.includes("m") &&
      !requestedInterval.includes("M")
    ) {
      return intv.toLowerCase() === requestedInterval.toLowerCase();
    }
    return false;
  });

  if (!isSupported) {
    return {
      isCompatible: false,
      reason: `Interval '${requestedInterval}' is unavailable for ${targetSymbol}. Preserving existing interval.`,
    };
  }

  return { isCompatible: true };
}

/**
 * Validate if a target panel has necessary data structure (OHLC) for requested chart type.
 */
export function validateChartTypeSync(
  targetSymbol: string,
  requestedMode: ChartRenderMode,
  hasOHLC: boolean
): ChartTypeValidationResult {
  if ((requestedMode === "candlestick" || requestedMode === "bar") && !hasOHLC) {
    return {
      isCompatible: false,
      reason: `Chart type '${requestedMode}' requires full OHLC data, which is unavailable for ${targetSymbol}.`,
    };
  }

  return { isCompatible: true };
}

/**
 * Strict Compatibility Gate for Chart Drawing Synchronization.
 *
 * Drawings are anchored to financial coordinates (price/time).
 * Drawing synchronization must NEVER copy prices across different financial instruments
 * or incompatible quotation bases (e.g. copying an equity support line to crypto).
 */
export function validateDrawingSyncCompatibility(
  sourceInstrument: ChartInstrumentMetadata | null,
  targetInstrument: ChartInstrumentMetadata | null
): DrawingCompatibilityResult {
  if (!sourceInstrument || !targetInstrument) {
    return {
      isCompatible: false,
      reason: "Both source and destination instruments must be fully loaded to synchronize drawings.",
    };
  }

  // 1. Canonical Instrument Entity ID must match exactly
  if (sourceInstrument.entity_id !== targetInstrument.entity_id) {
    return {
      isCompatible: false,
      reason: `Cannot synchronize drawings between different instruments (${sourceInstrument.display_symbol} vs ${targetInstrument.display_symbol}). Price coordinates are instrument-specific.`,
    };
  }

  // 2. Quotation currency must match
  if (
    sourceInstrument.price_currency &&
    targetInstrument.price_currency &&
    sourceInstrument.price_currency.toUpperCase() !== targetInstrument.price_currency.toUpperCase()
  ) {
    return {
      isCompatible: false,
      reason: `Quotation currency mismatch (${sourceInstrument.price_currency} vs ${targetInstrument.price_currency}). Drawing price scales are incompatible.`,
    };
  }

  return { isCompatible: true };
}
