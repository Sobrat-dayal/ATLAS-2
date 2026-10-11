/**
 * Determines whether raw palette input represents an ATLAS structured command
 * or deterministic shorthand, as opposed to normal text search.
 *
 * Section 153-157: Lightweight detector to guard when the backend structured parser
 * should be invoked.
 */

const SHORTHAND_SUFFIXES = [
  " CHART",
  " NEWS",
  " RESEARCH",
  " FA",
];

const SHORTHAND_PREFIXES = [
  "MAP ",
  "OPTIONS ",
  "BUY ",
  "SELL ",
];

const EXACT_SHORTHANDS = [
  "PORT RISK",
];

export function looksLikeAtlasStructuredCommand(rawInput: string): boolean {
  const trimmed = rawInput.trim();
  if (!trimmed) return false;

  // 1. Explicit slash command mode
  if (trimmed.startsWith("/")) {
    return true;
  }

  const upper = trimmed.toUpperCase();

  // 2. Exact shorthand matches (e.g. "PORT RISK")
  if (EXACT_SHORTHANDS.includes(upper)) {
    return true;
  }

  // Check if string contains quotes for multi-word targets
  const hasQuotes = trimmed.includes('"') || trimmed.includes("'");
  const words = trimmed.split(/\s+/);

  // 3. Recognized shorthand suffixes (e.g. NVDA CHART, "NVIDIA Corporation" NEWS)
  for (const suffix of SHORTHAND_SUFFIXES) {
    if (upper.endsWith(suffix) && upper.length > suffix.length) {
      // Must be either single-word target (exactly 2 words) or explicitly quoted
      if (words.length === 2 || hasQuotes) {
        return true;
      }
    }
  }

  // 4. Recognized shorthand prefixes (e.g. MAP TSMC, OPTIONS NVDA)
  for (const prefix of SHORTHAND_PREFIXES) {
    if (upper.startsWith(prefix) && upper.length > prefix.length) {
      // Must be either single-word target (exactly 2 words) or explicitly quoted
      if (words.length === 2 || hasQuotes) {
        return true;
      }
    }
  }

  return false;
}
