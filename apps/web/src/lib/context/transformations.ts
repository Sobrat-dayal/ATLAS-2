/**
 * Client-Side Canonical Entity Transformations for ATLAS Stage 121.
 */

import { ResolvedEntity, TransformationType } from "./types";

export const LOCAL_CANONICAL_ENTITIES: Record<string, ResolvedEntity> = {
  AAPL: {
    entity_id: "inst_aapl_us",
    entity_type: "INSTRUMENT",
    canonical_name: "Apple Inc. Common Stock",
    display_name: "Apple Inc.",
    symbol: "AAPL",
    exchange: "NASDAQ",
    currency: "USD",
    country: "USA",
  },
  MSFT: {
    entity_id: "inst_msft_us",
    entity_type: "INSTRUMENT",
    canonical_name: "Microsoft Corporation Common Stock",
    display_name: "Microsoft Corp.",
    symbol: "MSFT",
    exchange: "NASDAQ",
    currency: "USD",
    country: "USA",
  },
  NVDA: {
    entity_id: "inst_nvda_us",
    entity_type: "INSTRUMENT",
    canonical_name: "NVIDIA Corporation Common Stock",
    display_name: "NVIDIA Corp.",
    symbol: "NVDA",
    exchange: "NASDAQ",
    currency: "USD",
    country: "USA",
  },
  AMZN: {
    entity_id: "inst_amzn_us",
    entity_type: "INSTRUMENT",
    canonical_name: "Amazon.com Inc. Common Stock",
    display_name: "Amazon.com Inc.",
    symbol: "AMZN",
    exchange: "NASDAQ",
    currency: "USD",
    country: "USA",
  },
  GOOGL: {
    entity_id: "inst_googl_us",
    entity_type: "INSTRUMENT",
    canonical_name: "Alphabet Inc. Class A Common Stock",
    display_name: "Alphabet Inc.",
    symbol: "GOOGL",
    exchange: "NASDAQ",
    currency: "USD",
    country: "USA",
  },
};

export const LOCAL_COMPANY_ENTITIES: Record<string, ResolvedEntity> = {
  comp_apple_us: {
    entity_id: "comp_apple_us",
    entity_type: "COMPANY",
    canonical_name: "Apple Inc.",
    display_name: "Apple Inc.",
    symbol: "AAPL",
    currency: "USD",
    country: "USA",
  },
  comp_microsoft_us: {
    entity_id: "comp_microsoft_us",
    entity_type: "COMPANY",
    canonical_name: "Microsoft Corporation",
    display_name: "Microsoft Corp.",
    symbol: "MSFT",
    currency: "USD",
    country: "USA",
  },
  comp_nvidia_us: {
    entity_id: "comp_nvidia_us",
    entity_type: "COMPANY",
    canonical_name: "NVIDIA Corporation",
    display_name: "NVIDIA Corp.",
    symbol: "NVDA",
    currency: "USD",
    country: "USA",
  },
};

const INSTRUMENT_TO_COMPANY_LOCAL: Record<string, string> = {
  AAPL: "comp_apple_us",
  inst_aapl_us: "comp_apple_us",
  MSFT: "comp_microsoft_us",
  inst_msft_us: "comp_microsoft_us",
  NVDA: "comp_nvidia_us",
  inst_nvda_us: "comp_nvidia_us",
};

const COMPANY_TO_SYMBOL_LOCAL: Record<string, string> = {
  comp_apple_us: "AAPL",
  comp_microsoft_us: "MSFT",
  comp_nvidia_us: "NVDA",
};

export function transformEntityLocal(
  sourceId: string,
  transformation: TransformationType
): ResolvedEntity | null {
  const clean = sourceId.trim();

  if (transformation === "INSTRUMENT_TO_COMPANY") {
    const compId = INSTRUMENT_TO_COMPANY_LOCAL[clean.toUpperCase()] || INSTRUMENT_TO_COMPANY_LOCAL[clean];
    if (compId && LOCAL_COMPANY_ENTITIES[compId]) {
      return LOCAL_COMPANY_ENTITIES[compId];
    }
    // Fallback derived company
    const sym = clean.toUpperCase();
    return {
      entity_id: `comp_${sym.toLowerCase()}_us`,
      entity_type: "COMPANY",
      canonical_name: `${sym} Corporate Issuer`,
      display_name: `${sym} Corp.`,
      symbol: sym,
      currency: "USD",
      country: "USA",
    };
  }

  if (transformation === "COMPANY_TO_PRIMARY_LISTING") {
    const sym = COMPANY_TO_SYMBOL_LOCAL[clean];
    if (sym && LOCAL_CANONICAL_ENTITIES[sym]) {
      return LOCAL_CANONICAL_ENTITIES[sym];
    }
    if (clean.length <= 6 && clean.match(/^[A-Za-z]+$/)) {
      const s = clean.toUpperCase();
      return (
        LOCAL_CANONICAL_ENTITIES[s] || {
          entity_id: `inst_${s.toLowerCase()}_us`,
          entity_type: "INSTRUMENT",
          canonical_name: `${s} Common Stock`,
          display_name: `${s} Inc.`,
          symbol: s,
          currency: "USD",
        }
      );
    }
    return null;
  }

  if (transformation === "OPTION_TO_UNDERLYING") {
    // Standard OCC option format: Root ticker is the first letters before digits
    const match = clean.match(/^([A-Za-z]+)/);
    if (match) {
      const root = match[1].toUpperCase();
      return (
        LOCAL_CANONICAL_ENTITIES[root] || {
          entity_id: `inst_${root.toLowerCase()}_us`,
          entity_type: "INSTRUMENT",
          canonical_name: `${root} Common Stock`,
          display_name: `${root} Inc.`,
          symbol: root,
          currency: "USD",
        }
      );
    }
  }

  if (transformation === "PORTFOLIO_TO_BENCHMARK") {
    return {
      entity_id: "SPX",
      entity_type: "BENCHMARK",
      canonical_name: "S&P 500 Index",
      display_name: "S&P 500",
      symbol: "SPX",
      currency: "USD",
    };
  }

  return null;
}

