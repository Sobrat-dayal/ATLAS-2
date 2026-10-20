/**
 * Viewport-Aware Subscription Planning for Live Watchlists (Stage 78).
 *
 * Implements:
 * - Visible-row subscription prioritization with bounded overscan (+/- 10 rows)
 * - Subscription capacity budget enforcement (max 100 series per view)
 * - Background tab suspension (reducing/suspending view subscriptions when hidden)
 * - Stable canonical series identity generation
 * - Fast-scroll debouncing support
 */

import { QuoteSubscriptionKeyDTO } from "@/lib/realtime/types";
import { WatchlistItem } from "../types";
import { VisibleRowRange } from "./types";

export interface SubscriptionPlanOptions {
  overscan?: number;
  maxBudget?: number;
  isTabVisible?: boolean;
}

export const DEFAULT_OVERSCAN = 10;
export const DEFAULT_SUBSCRIPTION_BUDGET = 50;

/**
 * Computes the desired canonical subscription series set based on visible rows and overscan.
 */
export function calculateDesiredSubscriptionPlan(
  items: WatchlistItem[],
  visibleRange: VisibleRowRange | null,
  options: SubscriptionPlanOptions = {}
): QuoteSubscriptionKeyDTO[] {
  const isTabVisible = options.isTabVisible ?? true;

  // 1. If tab is in background, suspend view-specific live subscriptions
  if (!isTabVisible || items.length === 0) {
    return [];
  }

  const overscan = options.overscan ?? DEFAULT_OVERSCAN;
  const maxBudget = options.maxBudget ?? DEFAULT_SUBSCRIPTION_BUDGET;

  let startIndex = 0;
  let endIndex = items.length;

  // If a viewport visible range is specified, apply bounded overscan
  if (visibleRange) {
    startIndex = Math.max(0, visibleRange.startIndex - overscan);
    endIndex = Math.min(items.length, visibleRange.endIndex + overscan);
  }

  // Ensure bounded slice within budget
  const sliceCount = endIndex - startIndex;
  if (sliceCount > maxBudget) {
    endIndex = startIndex + maxBudget;
  }

  const slice = items.slice(startIndex, endIndex);

  // Map to canonical QuoteSubscriptionKeyDTO
  const seen = new Set<string>();
  const plan: QuoteSubscriptionKeyDTO[] = [];

  for (const item of slice) {
    if (!item.instrument_entity_id) continue;
    const key = item.instrument_entity_id.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      plan.push({
        instrument_entity_id: item.instrument_entity_id,
        variant: item.delivery_delay_status === "delayed" ? "delayed" : null,
        symbol: item.symbol,
      });
    }

    if (plan.length >= maxBudget) {
      break;
    }
  }

  return plan;
}
