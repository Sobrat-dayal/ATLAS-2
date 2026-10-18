/**
 * Multi-Market Calendar Alignment & Temporal Mapping Engine for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Strict UTC Unix timestamp resolution (never candle index or raw screen X pixels)
 * - Cross-interval session mapping (e.g. 5-minute intraday tick -> 1-day containing bar)
 * - Market calendar awareness (crypto 24/7 continuous vs equity market sessions & weekends)
 * - Safe nearest-bar determination with bounded tolerance
 * - Absolute visible time range clamping without feedback bouncing
 * - Strict financial data integrity: NO fabricated candles, NO synthetic quotes
 */

import { ChartBarDTO } from "../types";
import { TemporalAlignmentMatchType, TemporalMappingResult } from "./types";

/**
 * Check if an asset class trades continuously 24/7 (Crypto) or follows regular market sessions (Equities, FX, Bonds).
 */
export function isContinuousMarket(assetClass: string): boolean {
  const ac = assetClass.toLowerCase();
  return ac === "crypto" || ac === "cryptocurrency";
}

/**
 * Find bar matching a canonical timestamp or nearest bounded bar within existing historical bars.
 * Does NOT create or fabricate bars if none exists.
 */
export function mapTimestampToTargetBars(
  targetBars: ChartBarDTO[],
  timestampSeconds: number,
  targetInterval: string,
  toleranceSeconds: number = 86400 * 3
): TemporalMappingResult {
  if (!targetBars || targetBars.length === 0) {
    return {
      matchType: "NO_MATCH",
      targetTimestamp: null,
      hasBarAtTimestamp: false,
      notes: "Target panel has no loaded historical bars",
    };
  }

  // 1. Binary search for exact timestamp
  let low = 0;
  let high = targetBars.length - 1;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    const barTime = targetBars[mid].time_unix;

    if (barTime === timestampSeconds) {
      return {
        matchType: "EXACT_INSTANT",
        targetTimestamp: barTime,
        hasBarAtTimestamp: true,
      };
    } else if (barTime < timestampSeconds) {
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }

  // 2. Check if timestamp falls within a lower-frequency bar's interval duration (e.g., daily bar)
  const isDaily = targetInterval.toLowerCase() === "1d" || targetInterval.toLowerCase() === "d";
  if (isDaily) {
    // Check if timestamp is within same UTC calendar day or session day
    const targetDate = new Date(timestampSeconds * 1000).toISOString().slice(0, 10);
    const matchingBar = targetBars.find((b) => b.timestamp.slice(0, 10) === targetDate);
    if (matchingBar) {
      return {
        matchType: "SAME_TRADING_SESSION",
        targetTimestamp: matchingBar.time_unix,
        hasBarAtTimestamp: true,
        notes: `Matched containing daily session bar ${targetDate}`,
      };
    }
  }

  // 3. Find closest available bar within bounded tolerance
  let closestBar: ChartBarDTO | null = null;
  let minDiff = Infinity;

  for (const bar of targetBars) {
    const diff = Math.abs(bar.time_unix - timestampSeconds);
    if (diff < minDiff) {
      minDiff = diff;
      closestBar = bar;
    }
  }

  if (closestBar && minDiff <= toleranceSeconds) {
    return {
      matchType: "NEAREST_AVAILABLE_BAR",
      targetTimestamp: closestBar.time_unix,
      hasBarAtTimestamp: false, // Mark false so UI does not fabricate OHLC tooltip!
      notes: `Nearest bar at ${closestBar.timestamp} (offset: ${Math.round(minDiff / 60)}m)`,
    };
  }

  return {
    matchType: "OUT_OF_BOUNDS",
    targetTimestamp: null,
    hasBarAtTimestamp: false,
    notes: "Timestamp is outside target coverage bounds without fabrication",
  };
}

/**
 * Clamp a requested visible time range to target panel's available historical bounds.
 * Prevents requesting empty/invalid ranges while preserving valid user intent.
 */
export function clampVisibleTimeRange(
  requestedFrom: number,
  requestedTo: number,
  targetMinTime: number | null,
  targetMaxTime: number | null
): { from: number; to: number; isClamped: boolean } {
  // Validate basic range parameters
  if (requestedFrom >= requestedTo || !Number.isFinite(requestedFrom) || !Number.isFinite(requestedTo)) {
    return {
      from: requestedFrom,
      to: requestedTo,
      isClamped: false,
    };
  }

  if (targetMinTime === null || targetMaxTime === null || targetMinTime >= targetMaxTime) {
    return {
      from: requestedFrom,
      to: requestedTo,
      isClamped: false,
    };
  }

  let from = requestedFrom;
  let to = requestedTo;
  let isClamped = false;

  // If requested window is entirely older than target history
  if (to < targetMinTime) {
    from = targetMinTime;
    to = Math.min(targetMaxTime, targetMinTime + (requestedTo - requestedFrom));
    isClamped = true;
  }
  // If requested window is entirely in future of target history
  else if (from > targetMaxTime) {
    to = targetMaxTime;
    from = Math.max(targetMinTime, targetMaxTime - (requestedTo - requestedFrom));
    isClamped = true;
  } else {
    // Normal overlap: clamp boundaries if needed
    if (from < targetMinTime) {
      from = targetMinTime;
      isClamped = true;
    }
    if (to > targetMaxTime + 86400 * 7) {
      // allow small right margin for live updates
      to = targetMaxTime + 86400 * 7;
      isClamped = true;
    }
  }

  return { from, to, isClamped };
}
