"use client";

/**
 * Detailed Live Quote Metrics Strip for ATLAS Charts (Stage 67).
 *
 * Implements:
 * - Exact quotation precision formatting
 * - Tabular numerals for Last, Bid, Ask, Spread, and Sizes
 * - Truthful representation when Last price is unavailable (OTC FX / Bonds)
 * - Strict separation of executed trades from bid/ask quotes
 */

import React from "react";
import { ChartInstrumentMetadata, LiveQuoteDTO } from "@/lib/charts";
import { formatPrice } from "@/lib/charts/formatting";

export interface LatestQuoteDetailsProps {
  quote: LiveQuoteDTO | null;
  instrument: ChartInstrumentMetadata | null;
}

export function LatestQuoteDetails({ quote, instrument }: LatestQuoteDetailsProps) {
  // Determine quotation precision based on asset class
  const getPrecision = () => {
    if (!instrument) return 2;
    if (instrument.asset_class === "fx") return 4;
    if (instrument.asset_class === "bonds") return 3;
    return 2;
  };

  const precision = getPrecision();

  const lastPrice =
    quote?.has_genuine_last && quote?.last_price !== null && quote?.last_price !== undefined
      ? formatPrice(quote.last_price, precision)
      : null;

  const bidPrice =
    quote?.bid_price !== null && quote?.bid_price !== undefined
      ? formatPrice(quote.bid_price, precision)
      : "—";

  const askPrice =
    quote?.ask_price !== null && quote?.ask_price !== undefined
      ? formatPrice(quote.ask_price, precision)
      : "—";

  // Calculate spread if both bid and ask exist
  let spreadText = "—";
  let spreadBpsText = "";
  if (
    quote?.bid_price !== null &&
    quote?.bid_price !== undefined &&
    quote?.ask_price !== null &&
    quote?.ask_price !== undefined
  ) {
    const b = Number(quote.bid_price);
    const a = Number(quote.ask_price);
    if (!isNaN(b) && !isNaN(a) && a >= b) {
      const spread = a - b;
      spreadText = spread.toFixed(precision);
      const mid = (a + b) / 2;
      if (mid > 0) {
        const bps = (spread / mid) * 10000;
        spreadBpsText = `(${bps.toFixed(1)} bps)`;
      }
    }
  }

  const quoteUnit = instrument?.quotation_unit || "USD";

  return (
    <div
      role="region"
      aria-label="Latest Quote Metrics"
      className="flex flex-wrap items-center gap-4 px-4 py-2 bg-zinc-950/80 border-b border-zinc-800/80 text-xs font-mono"
    >
      {/* Last Price */}
      <div className="flex items-center gap-1.5">
        <span className="text-zinc-500 font-semibold">LAST:</span>
        {lastPrice !== null ? (
          <span className="text-sm font-bold text-emerald-400 tabular-nums">
            {lastPrice}
          </span>
        ) : (
          <span className="text-zinc-500 font-medium italic">
            — (LAST UNAVAILABLE)
          </span>
        )}
        {quote?.last_size && lastPrice !== null && (
          <span className="text-[10px] text-zinc-500 tabular-nums">
            x{quote.last_size}
          </span>
        )}
      </div>

      <div className="h-3 w-px bg-zinc-800" />

      {/* Bid / Ask */}
      <div className="flex items-center gap-1.5">
        <span className="text-zinc-500">BID:</span>
        <span className="text-zinc-200 tabular-nums font-semibold">{bidPrice}</span>
        {quote?.bid_size && (
          <span className="text-[10px] text-zinc-500 tabular-nums">
            ({quote.bid_size})
          </span>
        )}
      </div>

      <div className="flex items-center gap-1.5">
        <span className="text-zinc-500">ASK:</span>
        <span className="text-zinc-200 tabular-nums font-semibold">{askPrice}</span>
        {quote?.ask_size && (
          <span className="text-[10px] text-zinc-500 tabular-nums">
            ({quote.ask_size})
          </span>
        )}
      </div>

      <div className="h-3 w-px bg-zinc-800 hidden sm:block" />

      {/* Spread */}
      <div className="hidden sm:flex items-center gap-1.5">
        <span className="text-zinc-500">SPREAD:</span>
        <span className="text-zinc-300 tabular-nums">{spreadText}</span>
        {spreadBpsText && (
          <span className="text-[10px] text-zinc-500 tabular-nums">
            {spreadBpsText}
          </span>
        )}
      </div>

      <div className="h-3 w-px bg-zinc-800 hidden md:block" />

      {/* Quotation Unit */}
      <div className="hidden md:flex items-center gap-1.5 ml-auto text-zinc-400">
        <span className="text-zinc-500">UNIT:</span>
        <span className="text-zinc-300 font-medium">{quoteUnit}</span>
      </div>
    </div>
  );
}
