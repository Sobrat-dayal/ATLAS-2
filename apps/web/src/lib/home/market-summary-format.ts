/**
 * Deterministic Financial Formatting and Presentation Helpers for Home Market Summary.
 */

import {
  HomeMarketSummaryItem,
  MarketSummaryChangeDirection,
  MarketSummaryDeliveryDelay,
} from "./market-summary-types";

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$",
  EUR: "€",
  GBP: "£",
  JPY: "¥",
  INR: "₹",
  CHF: "CHF ",
};

/**
 * Formats canonical price value based on instrument category and units.
 * Never returns fabricated zero values when price is missing.
 */
export function formatMarketPrice(item: HomeMarketSummaryItem): {
  formattedValue: string;
  unitLabel: string;
} {
  const rawPrice = item.last_price || item.ask_price || item.bid_price;

  if (!rawPrice) {
    return {
      formattedValue: "Unavailable",
      unitLabel: item.quote_unit || item.quote_currency || "",
    };
  }

  const num = Number(rawPrice);
  if (isNaN(num)) {
    return {
      formattedValue: rawPrice,
      unitLabel: item.quote_unit || item.quote_currency || "",
    };
  }

  // 1. Currency Pair / FX (typically 4 decimal places)
  if (item.instrument_category === "currency") {
    return {
      formattedValue: num.toLocaleString(undefined, {
        minimumFractionDigits: 4,
        maximumFractionDigits: 4,
      }),
      unitLabel: item.quote_unit || item.quote_currency || "",
    };
  }

  // 2. Market Index (points, not currency)
  if (item.instrument_category === "market_index" || item.value_kind === "points") {
    return {
      formattedValue: num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }),
      unitLabel: item.quote_unit || "pts",
    };
  }

  // 3. Crypto Asset (high precision if small value, 2 decimals if >= 100)
  if (item.instrument_category === "crypto_asset") {
    const fractionDigits = num >= 100 ? 2 : num >= 1 ? 4 : 6;
    const prefix = item.quote_currency ? (CURRENCY_SYMBOLS[item.quote_currency] || "") : "";
    return {
      formattedValue: `${prefix}${num.toLocaleString(undefined, {
        minimumFractionDigits: fractionDigits,
        maximumFractionDigits: fractionDigits,
      })}`,
      unitLabel: item.quote_currency || "",
    };
  }

  // 4. Commodity
  if (item.instrument_category === "commodity") {
    const prefix = item.quote_currency ? (CURRENCY_SYMBOLS[item.quote_currency] || "") : "";
    return {
      formattedValue: `${prefix}${num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`,
      unitLabel: item.quote_unit || item.quote_currency || "",
    };
  }

  // 5. Standard Securities / Equities / ETFs
  const prefix = item.quote_currency ? (CURRENCY_SYMBOLS[item.quote_currency] || "") : "";
  return {
    formattedValue: `${prefix}${num.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`,
    unitLabel: item.quote_currency || "",
  };
}

/**
 * Formats absolute change with proper sign.
 */
export function formatAbsoluteChange(item: HomeMarketSummaryItem): string | null {
  if (!item.absolute_change) return null;
  const num = Number(item.absolute_change);
  if (isNaN(num)) return item.absolute_change;

  const decimals = item.instrument_category === "currency" ? 4 : 2;
  const formatted = Math.abs(num).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  if (num > 0) return `+${formatted}`;
  if (num < 0) return `-${formatted}`;
  return `0.${"0".repeat(decimals)}`;
}

/**
 * Formats percentage change with proper sign and % suffix.
 */
export function formatPercentageChange(item: HomeMarketSummaryItem): string | null {
  if (!item.percentage_change) return null;
  const num = Number(item.percentage_change);
  if (isNaN(num)) return `${item.percentage_change}%`;

  const formatted = Math.abs(num).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  if (num > 0) return `+${formatted}%`;
  if (num < 0) return `-${formatted}%`;
  return "0.00%";
}

/**
 * Presentation colors for price movement direction.
 */
export function getChangeDirectionStyles(direction: MarketSummaryChangeDirection): {
  textColor: string;
  badgeBg: string;
  badgeBorder: string;
} {
  switch (direction) {
    case "up":
      return {
        textColor: "text-emerald-400",
        badgeBg: "bg-emerald-500/10",
        badgeBorder: "border-emerald-500/20",
      };
    case "down":
      return {
        textColor: "text-rose-400",
        badgeBg: "bg-rose-500/10",
        badgeBorder: "border-rose-500/20",
      };
    case "flat":
      return {
        textColor: "text-zinc-400",
        badgeBg: "bg-zinc-500/10",
        badgeBorder: "border-zinc-500/20",
      };
    default:
      return {
        textColor: "text-zinc-500",
        badgeBg: "bg-zinc-800/20",
        badgeBorder: "border-zinc-700/20",
      };
  }
}

/**
 * Returns restrained label and badge styling for data freshness.
 */
export function getFreshnessBadge(status: string): {
  label: string;
  dotColor: string;
  textColor: string;
} {
  switch (status.toLowerCase()) {
    case "fresh":
      return { label: "Current", dotColor: "bg-emerald-400", textColor: "text-emerald-400" };
    case "aging":
      return { label: "Aging", dotColor: "bg-amber-400", textColor: "text-amber-400" };
    case "stale":
      return { label: "Stale", dotColor: "bg-orange-400", textColor: "text-orange-400" };
    case "unavailable":
    default:
      return { label: "No Feed", dotColor: "bg-zinc-500", textColor: "text-zinc-500" };
  }
}

/**
 * Returns delivery delay indicator label.
 */
export function getDelayBadge(delayStatus: MarketSummaryDeliveryDelay, delaySeconds?: number | null): {
  label: string;
  show: boolean;
} {
  if (delayStatus === "delayed") {
    const mins = delaySeconds ? Math.round(delaySeconds / 60) : 15;
    return { label: `${mins}m Delayed`, show: true };
  }
  return { label: "", show: false };
}
