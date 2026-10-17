"use client";

/**
 * Institutional Instrument Header for ATLAS Charts V1 (Stage 66).
 *
 * Displays authoritative instrument identity, quotation unit, trading venue,
 * provider provenance, adjustment policy, and asset-class classification.
 */

import React from "react";
import Link from "next/link";
import { ArrowUpRight, Clock, Database, ShieldCheck } from "lucide-react";
import {
  ChartInstrumentMetadata,
  getAssetClassBadgeLabel,
  getAssetClassColor,
} from "@/lib/charts";

export interface ChartInstrumentHeaderProps {
  instrument: ChartInstrumentMetadata | null;
}

export function ChartInstrumentHeader({ instrument }: ChartInstrumentHeaderProps) {
  if (!instrument) {
    return (
      <div className="flex items-center gap-3 p-4 bg-zinc-900/40 border border-zinc-800/80 rounded animate-pulse">
        <div className="w-20 h-6 bg-zinc-800 rounded" />
        <div className="w-48 h-6 bg-zinc-800 rounded" />
      </div>
    );
  }

  const assetClassBadgeClass = getAssetClassColor(instrument.asset_class);
  const assetClassLabel = getAssetClassBadgeLabel(instrument.asset_class);

  // Cross-module link destination
  const getMarketsLink = () => {
    switch (instrument.asset_class.toLowerCase()) {
      case "equities":
        return "/markets/equities";
      case "etfs":
        return "/markets/funds";
      case "fx":
        return "/markets/fx";
      case "crypto":
        return "/markets/crypto";
      case "bonds":
        return "/markets/bonds";
      case "futures":
        return "/markets/futures";
      default:
        return "/markets";
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 bg-zinc-950/80 border border-zinc-800/80 rounded">
      {/* Identity Group */}
      <div className="flex items-center gap-3">
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-bold font-mono text-zinc-100 tracking-tight">
            {instrument.display_symbol}
          </span>
          <span className="text-sm text-zinc-400 font-medium">
            {instrument.display_name}
          </span>
        </div>

        {/* Asset Class Badge */}
        <span
          className={`px-2 py-0.5 text-[11px] font-mono font-semibold rounded border ${assetClassBadgeClass}`}
        >
          {assetClassLabel}
        </span>

        {/* Venue Badge */}
        <span className="px-2 py-0.5 text-[11px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-300 rounded">
          {instrument.market_or_venue}
        </span>

        {/* Futures Contract Expiration */}
        {instrument.is_futures && instrument.contract_expiration && (
          <span className="px-2 py-0.5 text-[11px] font-mono bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded flex items-center gap-1">
            <Clock className="w-3 h-3 text-rose-400" />
            <span>Exp: {instrument.contract_expiration.slice(0, 10)}</span>
          </span>
        )}
      </div>

      {/* Financial Quotation & Provenance Metadata */}
      <div className="flex items-center gap-4 text-xs font-mono text-zinc-400">
        {/* Quotation Unit */}
        <div className="flex items-center gap-1.5 bg-zinc-900/60 px-2 py-1 rounded border border-zinc-800/60">
          <span className="text-zinc-500 text-[10px] uppercase">Unit:</span>
          <span className="text-zinc-200">{instrument.quotation_unit}</span>
        </div>

        {/* Adjustment Basis */}
        <div className="flex items-center gap-1.5 bg-zinc-900/60 px-2 py-1 rounded border border-zinc-800/60">
          <ShieldCheck className="w-3.5 h-3.5 text-zinc-500" />
          <span className="text-zinc-500 text-[10px] uppercase">Basis:</span>
          <span className="text-zinc-300">{instrument.adjustment_basis}</span>
        </div>

        {/* Provider Provenance */}
        <div className="flex items-center gap-1.5 bg-zinc-900/60 px-2 py-1 rounded border border-zinc-800/60">
          <Database className="w-3.5 h-3.5 text-cyan-500" />
          <span className="text-zinc-300">{instrument.provider_key}</span>
        </div>

        {/* Link to Markets Module */}
        <Link
          href={getMarketsLink()}
          className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 hover:underline transition-colors"
        >
          <span>Markets</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
