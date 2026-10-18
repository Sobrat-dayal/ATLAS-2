/**
 * Fibonacci Retracement Calculation Utilities for ATLAS Charts (Stage 71).
 *
 * Implements:
 * - Standard Fibonacci ratios: 0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.000.
 * - Direction-preserving formula L(r) = P0 + r * (P1 - P0).
 * - Exact financial level prices and formatted percentage labels.
 */

export interface FibonacciLevel {
  ratio: number;
  percentageLabel: string;
  price: number;
  priceFormatted: string;
  color: string;
}

export const FIBONACCI_DEFAULT_RATIOS: { ratio: number; label: string; color: string }[] = [
  { ratio: 0.0, label: "0.0% (0.0)", color: "#71717a" },
  { ratio: 0.236, label: "23.6% (0.236)", color: "#a855f7" },
  { ratio: 0.382, label: "38.2% (0.382)", color: "#06b6d4" },
  { ratio: 0.5, label: "50.0% (0.500)", color: "#10b981" },
  { ratio: 0.618, label: "61.8% (0.618)", color: "#f59e0b" },
  { ratio: 0.786, label: "78.6% (0.786)", color: "#ec4899" },
  { ratio: 1.0, label: "100.0% (1.0)", color: "#71717a" },
];

/**
 * Calculates standard Fibonacci retracement price levels given two anchor prices.
 * Preserves anchor direction: P0 is 0.0, P1 is 1.0.
 */
export function calculateFibonacciLevels(
  startPrice: number,
  endPrice: number,
  ratios = FIBONACCI_DEFAULT_RATIOS
): FibonacciLevel[] {
  const priceRange = endPrice - startPrice;

  return ratios.map((item) => {
    const rawLevelPrice = startPrice + item.ratio * priceRange;
    const levelPrice = Math.round(rawLevelPrice * 10000) / 10000;
    return {
      ratio: item.ratio,
      percentageLabel: item.label,
      price: levelPrice,
      priceFormatted: levelPrice.toFixed(2),
      color: item.color,
    };
  });
}
