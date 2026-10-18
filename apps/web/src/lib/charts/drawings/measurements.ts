/**
 * Financial Price and Time Measurement Utilities for ATLAS Charts (Stage 71).
 *
 * Implements:
 * - Absolute price change calculation Delta P = P2 - P1.
 * - Percentage price change Delta P% = (P2 - P1) / P1 * 100 with zero/negative denominator guards.
 * - Elapsed calendar time formatting (days, hours, minutes).
 * - Qualified trading bar count from canonical chart bars.
 */

import { ChartBarDTO } from "../types";

export interface PriceMeasurementResult {
  startPrice: number;
  endPrice: number;
  deltaPrice: number;
  deltaPriceFormatted: string;
  deltaPercent: number | null;
  deltaPercentFormatted: string;
  isPositive: boolean;
  isZero: boolean;
}

export interface TimeMeasurementResult {
  startTime: number;
  endTime: number;
  elapsedSeconds: number;
  elapsedFormatted: string;
  barCount: number;
  barCountFormatted: string;
}

export interface CombinedMeasurementResult {
  price: PriceMeasurementResult;
  time: TimeMeasurementResult;
}

/**
 * Calculates price change and percentage change between two financial prices.
 */
export function calculatePriceMeasurement(
  startPrice: number,
  endPrice: number,
  quotationUnit?: string
): PriceMeasurementResult {
  const deltaPrice = endPrice - startPrice;
  const isPositive = deltaPrice > 0;
  const isZero = deltaPrice === 0;

  // Format absolute change with sign
  const sign = isPositive ? "+" : "";
  const unit = quotationUnit ? ` ${quotationUnit}` : "";
  const deltaPriceFormatted = `${sign}${deltaPrice.toFixed(2)}${unit}`;

  // Percentage difference: strictly valid only when startPrice > 0
  let deltaPercent: number | null = null;
  let deltaPercentFormatted = "N/A";

  if (startPrice > 0) {
    deltaPercent = (deltaPrice / startPrice) * 100;
    deltaPercentFormatted = `${deltaPercent > 0 ? "+" : ""}${deltaPercent.toFixed(2)}%`;
  } else if (startPrice === 0) {
    deltaPercentFormatted = "N/A (base 0)";
  } else {
    // Negative start price (e.g. negative oil futures)
    deltaPercentFormatted = "N/A (negative base)";
  }

  return {
    startPrice,
    endPrice,
    deltaPrice,
    deltaPriceFormatted,
    deltaPercent,
    deltaPercentFormatted,
    isPositive,
    isZero,
  };
}

/**
 * Formats elapsed seconds into an institutional calendar duration.
 */
export function formatElapsedSeconds(seconds: number): string {
  const absSec = Math.abs(seconds);
  const days = Math.floor(absSec / 86400);
  const hours = Math.floor((absSec % 86400) / 3600);
  const minutes = Math.floor((absSec % 3600) / 60);

  if (days > 0) {
    return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
  }
  if (hours > 0) {
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }
  return `${minutes}m`;
}

/**
 * Calculates time elapsed and the actual count of qualified canonical bars between two timestamps.
 */
export function calculateTimeMeasurement(
  startTime: number,
  endTime: number,
  bars: ChartBarDTO[] = []
): TimeMeasurementResult {
  const minTime = Math.min(startTime, endTime);
  const maxTime = Math.max(startTime, endTime);
  const elapsedSeconds = maxTime - minTime;
  const elapsedFormatted = formatElapsedSeconds(elapsedSeconds);

  // Count canonical loaded bars in range [minTime, maxTime]
  let barCount = 0;
  if (bars && bars.length > 0) {
    for (let i = 0; i < bars.length; i++) {
      const t = bars[i].time_unix;
      if (t >= minTime && t <= maxTime) {
        barCount++;
      }
    }
  }

  const barCountFormatted = `${barCount} bar${barCount === 1 ? "" : "s"}`;

  return {
    startTime,
    endTime,
    elapsedSeconds,
    elapsedFormatted,
    barCount,
    barCountFormatted,
  };
}

/**
 * Calculates combined price and time measurements.
 */
export function calculateCombinedMeasurement(
  startPrice: number,
  endPrice: number,
  startTime: number,
  endTime: number,
  bars: ChartBarDTO[] = [],
  quotationUnit?: string
): CombinedMeasurementResult {
  return {
    price: calculatePriceMeasurement(startPrice, endPrice, quotationUnit),
    time: calculateTimeMeasurement(startTime, endTime, bars),
  };
}
