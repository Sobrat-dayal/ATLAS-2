/**
 * Formatting utilities for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).
 *
 * Implements strict, Decimal-safe display helpers for bond clean/dirty prices,
 * quotation units, contractual coupons, typed yields, and basis points.
 */

import { BondType, CouponType, PriceBasis, PriceKind, PriceQuoteUnit, YieldType } from "./types";

/**
 * Format observed bond price with quotation basis and unit.
 */
export function formatBondPrice(
  price: string | number | null | undefined,
  quoteUnit: PriceQuoteUnit = "percentage_of_par",
  precision = 3
): string {
  if (price === null || price === undefined || price === "") {
    return "—";
  }

  const num = typeof price === "number" ? price : parseFloat(price);
  if (isNaN(num)) {
    return "—";
  }

  const formatted = num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: precision,
  });

  if (quoteUnit === "percentage_of_par") {
    return `${formatted}%`;
  } else if (quoteUnit === "price_per_100_face") {
    return `${formatted} /100`;
  }
  return formatted;
}

/**
 * Format contractual coupon rate and type.
 */
export function formatBondCoupon(
  couponRate: string | number | null | undefined,
  couponType: CouponType = "fixed"
): string {
  if (couponType === "zero_coupon") {
    return "Zero (0.00%)";
  }

  if (couponRate === null || couponRate === undefined || couponRate === "") {
    return "Coupon unavailable";
  }

  const num = typeof couponRate === "number" ? couponRate : parseFloat(couponRate);
  if (isNaN(num)) {
    return "Coupon unavailable";
  }

  const rateStr = `${num.toFixed(3).replace(/\.?0+$/, "")}%`;
  if (couponType === "floating") {
    return `${rateStr} (Float)`;
  }
  return rateStr;
}

/**
 * Format typed yield observation.
 */
export function formatBondYield(
  yieldValue: string | number | null | undefined,
  _yieldType: YieldType = "ytm",
  precision = 3
): string {
  void _yieldType;
  if (yieldValue === null || yieldValue === undefined || yieldValue === "") {
    return "—";
  }

  const num = typeof yieldValue === "number" ? yieldValue : parseFloat(yieldValue);
  if (isNaN(num)) {
    return "—";
  }

  const formatted = num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: precision,
  });

  return `${formatted}%`;
}

/**
 * Format yield movement in basis points (1 bps = 0.01 percentage point).
 */
export function formatYieldChangeBps(bps: string | number | null | undefined): string {
  if (bps === null || bps === undefined || bps === "") {
    return "—";
  }

  const num = typeof bps === "number" ? bps : parseFloat(bps);
  if (isNaN(num)) {
    return "—";
  }

  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(1)} bps`;
}

/**
 * Format price spread between bid and ask.
 */
export function formatBondSpread(spread: string | number | null | undefined): string {
  if (spread === null || spread === undefined || spread === "") {
    return "—";
  }

  const num = typeof spread === "number" ? spread : parseFloat(spread);
  if (isNaN(num)) {
    return "—";
  }

  return num.toFixed(3);
}

/**
 * Format maturity date or display Perpetual.
 */
export function formatBondMaturity(
  maturityDateStr: string | null | undefined,
  isPerpetual = false
): string {
  if (isPerpetual) {
    return "Perpetual";
  }

  if (!maturityDateStr) {
    return "Maturity unavailable";
  }

  try {
    const d = new Date(maturityDateStr);
    if (isNaN(d.getTime())) {
      return maturityDateStr;
    }
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      timeZone: "UTC",
    });
  } catch {
    return maturityDateStr;
  }
}

/**
 * Format approximate calendar time to maturity.
 */
export function formatTimeToMaturity(years: string | number | null | undefined): string {
  if (years === null || years === undefined || years === "") {
    return "—";
  }

  const num = typeof years === "number" ? years : parseFloat(years);
  if (isNaN(num)) {
    return "—";
  }

  if (num < 1) {
    const months = Math.round(num * 12);
    return `${months} mo`;
  }
  return `${num.toFixed(1)} yr`;
}

/**
 * Human-readable bond debt type.
 */
export function formatBondType(type: BondType): string {
  switch (type) {
    case "sovereign":
      return "Sovereign";
    case "corporate":
      return "Corporate";
    case "municipal":
      return "Municipal";
    case "agency":
      return "Agency";
    case "supranational":
      return "Supranational";
    case "treasury_bill":
      return "Treasury Bill";
    default:
      return type;
  }
}

/**
 * Human-readable price kind.
 */
export function formatPriceKind(kind: PriceKind): string {
  switch (kind) {
    case "trade_price":
      return "Executed Trade";
    case "evaluated_price":
      return "Evaluated Model";
    case "indicative_quote":
      return "Indicative Quote";
    case "reference_price":
      return "Reference Fixing";
    default:
      return "Unknown";
  }
}

/**
 * Human-readable price basis.
 */
export function formatPriceBasis(basis: PriceBasis): string {
  switch (basis) {
    case "clean":
      return "Clean";
    case "dirty":
      return "Dirty";
    default:
      return "Unknown";
  }
}

/**
 * Human-readable yield type label.
 */
export function formatYieldTypeLabel(type: YieldType): string {
  switch (type) {
    case "ytm":
      return "YTM";
    case "ytc":
      return "YTC";
    case "ytw":
      return "YTW";
    case "current_yield":
      return "Current Yield";
    case "discount_yield":
      return "Discount";
    default:
      return "Yield";
  }
}

/**
 * Returns Tailwind color class for signed numeric movements.
 */
export function getDirectionColorClass(val: string | number | null | undefined): string {
  if (val === null || val === undefined || val === "") {
    return "text-zinc-400";
  }
  const num = typeof val === "number" ? val : parseFloat(val);
  if (isNaN(num) || num === 0) {
    return "text-zinc-400";
  }
  return num > 0 ? "text-emerald-400" : "text-rose-400";
}

/**
 * Returns Tailwind badge classes for data freshness status.
 */
export function getFreshnessBadgeClass(status: string | null | undefined): string {
  const s = (status || "").toUpperCase();
  switch (s) {
    case "REALTIME":
    case "LIVE":
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    case "DELAYED":
      return "bg-amber-500/10 text-amber-400 border-amber-500/30";
    case "STALE":
      return "bg-rose-500/10 text-rose-400 border-rose-500/30";
    default:
      return "bg-zinc-800 text-zinc-400 border-zinc-700/50";
  }
}

/**
 * Format observation timestamp.
 */
export function formatObservationTime(timestampStr: string | null | undefined): string {
  if (!timestampStr) return "—";
  try {
    const d = new Date(timestampStr);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
    }) + " UTC";
  } catch {
    return "—";
  }
}
