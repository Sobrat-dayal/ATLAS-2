/**
 * Smart Snapping Engine for Financial Chart Observations (Stage 71).
 *
 * Implements:
 * - OFF mode: exact pointer coordinates.
 * - NEAREST_BAR mode: snaps time to the nearest canonical bar within pixel tolerance.
 * - OHLC mode: snaps price to the nearest Open, High, Low, or Close of the nearest bar within pixel tolerance.
 * - Modifier override: temporarily bypasses snapping when Shift or Alt is pressed.
 * - Strict integrity: Snaps ONLY to qualified canonical chart observations, never synthetic or fabricated values.
 */

import { ChartBarDTO } from "../types";
import { DrawingAnchor, ScreenPoint, SnappingMode } from "./types";

export interface SnapTargetResult {
  anchor: DrawingAnchor;
  screenPoint: ScreenPoint;
  snapped: boolean;
  snapField?: "open" | "high" | "low" | "close" | "bar";
}

export interface SnappingOptions {
  mode: SnappingMode;
  pixelTolerance?: number; // default 15px
  isModifierActive?: boolean; // Shift or Alt
}

export interface CoordinateProjection {
  timeToScreen: (time: number) => number | null;
  priceToScreen: (price: number) => number | null;
  screenToTime: (x: number) => number | null;
  screenToPrice: (y: number) => number | null;
}

/**
 * Resolves a pointer screen coordinate to a financial anchor with optional smart snapping.
 */
export function resolveSnapping(
  pointerScreen: ScreenPoint,
  bars: ChartBarDTO[],
  projection: CoordinateProjection,
  options: SnappingOptions
): SnapTargetResult {
  const { mode, pixelTolerance = 15, isModifierActive = false } = options;

  // Initial direct unsnapped financial coordinates
  const rawTime = projection.screenToTime(pointerScreen.x);
  const rawPrice = projection.screenToPrice(pointerScreen.y);

  const fallbackResult: SnapTargetResult = {
    anchor: {
      time: rawTime ?? 0,
      price: rawPrice ?? 0,
    },
    screenPoint: pointerScreen,
    snapped: false,
  };

  // If snapping is OFF, or modifier key overrides it, return raw coordinates
  if (mode === "OFF" || isModifierActive || !bars || bars.length === 0) {
    return fallbackResult;
  }

  // Find the nearest bar by screen X distance
  let nearestBar: ChartBarDTO | null = null;
  let minScreenDistX = Infinity;
  let nearestBarScreenX = 0;

  for (let i = 0; i < bars.length; i++) {
    const bar = bars[i];
    const screenX = projection.timeToScreen(bar.time_unix);
    if (screenX === null) continue;

    const distX = Math.abs(pointerScreen.x - screenX);
    if (distX < minScreenDistX) {
      minScreenDistX = distX;
      nearestBar = bar;
      nearestBarScreenX = screenX;
    }
  }

  // If no bar is within horizontal pixel tolerance, no snap
  if (!nearestBar || minScreenDistX > pixelTolerance) {
    return fallbackResult;
  }

  // Mode: NEAREST_BAR (time snapped to bar, price remains raw pointer price)
  if (mode === "NEAREST_BAR") {
    return {
      anchor: {
        time: nearestBar.time_unix,
        price: rawPrice ?? 0,
      },
      screenPoint: {
        x: nearestBarScreenX,
        y: pointerScreen.y,
      },
      snapped: true,
      snapField: "bar",
    };
  }

  // Mode: OHLC (time snapped to bar, price snapped to nearest Open, High, Low, or Close)
  if (mode === "OHLC") {
    const ohlcCandidates: { field: "open" | "high" | "low" | "close"; price: number }[] = [
      { field: "open", price: Number(nearestBar.open) },
      { field: "high", price: Number(nearestBar.high) },
      { field: "low", price: Number(nearestBar.low) },
      { field: "close", price: Number(nearestBar.close) },
    ];

    let bestField: "open" | "high" | "low" | "close" = "close";
    let bestPrice = Number(nearestBar.close);
    let minScreenDistY = Infinity;
    let bestScreenY = pointerScreen.y;

    for (const cand of ohlcCandidates) {
      const screenY = projection.priceToScreen(cand.price);
      if (screenY === null) continue;

      const distY = Math.abs(pointerScreen.y - screenY);
      if (distY < minScreenDistY) {
        minScreenDistY = distY;
        bestField = cand.field;
        bestPrice = cand.price;
        bestScreenY = screenY;
      }
    }

    // Only snap price if within vertical pixel tolerance; otherwise snap time only
    if (minScreenDistY <= pixelTolerance) {
      return {
        anchor: {
          time: nearestBar.time_unix,
          price: bestPrice,
        },
        screenPoint: {
          x: nearestBarScreenX,
          y: bestScreenY,
        },
        snapped: true,
        snapField: bestField,
      };
    }

    // Fallback to snapping time only if price is outside tolerance
    return {
      anchor: {
        time: nearestBar.time_unix,
        price: rawPrice ?? 0,
      },
      screenPoint: {
        x: nearestBarScreenX,
        y: pointerScreen.y,
      },
      snapped: true,
      snapField: "bar",
    };
  }

  return fallbackResult;
}
