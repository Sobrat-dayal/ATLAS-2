"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  BarChart2,
  BookOpen,
  Check,
  Coins,
  Copy,
  Info,
  Layers,
  X,
} from "lucide-react";
import {
  formatCryptoChange,
  formatCryptoFreshnessBadge,
  formatCryptoPrice,
  formatCryptoRateKind,
  formatCryptoSpread,
  formatCryptoSpreadBps,
  formatCryptoVolume,
  formatObservedTimestamp,
} from "@/lib/markets/crypto";
import { useCryptoMarketDetail } from "@/hooks/markets/useCryptoMarketDetail";

export interface CryptoMarketInspectorProps {
  selectedPairId: string | null;
  onClose: () => void;
}

export function CryptoMarketInspector({
  selectedPairId,
  onClose,
}: CryptoMarketInspectorProps) {
  const { data: detail, isLoading, isError, error } =
    useCryptoMarketDetail(selectedPairId);
  const [copiedId, setCopiedId] = useState(false);
  const [copiedContract, setCopiedContract] = useState(false);

  if (!selectedPairId) {
    return (
      <aside
        aria-label="Cryptocurrency market inspector placeholder"
        className="h-full flex flex-col items-center justify-center p-6 text-center border border-[var(--atlas-border-subtle)] rounded-lg bg-[var(--atlas-surface-card)]"
      >
        <Layers className="h-8 w-8 text-[var(--atlas-text-tertiary)] mb-2.5 opacity-50" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)]">
          Select a Crypto Spot Market
        </h3>
        <p className="text-xs text-[var(--atlas-text-tertiary)] mt-1 max-w-[240px]">
          Click any spot trading pair in the table to inspect exchange venue data, base asset details, and top-of-book metrics.
        </p>
      </aside>
    );
  }

  const handleCopyUuid = () => {
    if (detail?.instrument_entity_id) {
      navigator.clipboard.writeText(detail.instrument_entity_id);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const handleCopyContract = () => {
    if (detail?.base_asset.contract_address) {
      navigator.clipboard.writeText(detail.base_asset.contract_address);
      setCopiedContract(true);
      setTimeout(() => setCopiedContract(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <aside
        aria-label="Loading cryptocurrency market details"
        className="h-full p-4 border border-[var(--atlas-border-subtle)] rounded-lg bg-[var(--atlas-surface-card)] flex flex-col justify-center items-center text-xs text-[var(--atlas-text-tertiary)] gap-2"
      >
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
        <span>Loading market overview...</span>
      </aside>
    );
  }

  if (isError || !detail) {
    return (
      <aside
        aria-label="Error loading cryptocurrency market details"
        className="h-full p-4 border border-rose-900/30 rounded-lg bg-[var(--atlas-surface-card)] flex flex-col justify-center items-center text-xs text-rose-400 gap-2 text-center"
      >
        <p>{error?.message || "Failed to load market inspection details."}</p>
        <button
          type="button"
          onClick={onClose}
          className="px-2.5 py-1 text-xs bg-zinc-800 text-zinc-300 rounded hover:bg-zinc-700"
        >
          Dismiss
        </button>
      </aside>
    );
  }

  const quote = detail.quote;
  const change = formatCryptoChange(quote.change_24h_percent);
  const freshness = formatCryptoFreshnessBadge(quote.freshness_status);
  const rateKind = formatCryptoRateKind(quote.rate_kind);

  return (
    <aside
      aria-label={`Inspection details for ${detail.market_symbol} on ${detail.venue.name}`}
      className="flex flex-col gap-3.5 p-4 rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] text-xs"
    >
      {/* Top Header */}
      <div className="flex items-start justify-between gap-2 border-b border-[var(--atlas-border-subtle)] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold font-mono text-[var(--atlas-text-primary)]">
              {detail.market_symbol}
            </h2>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700/50">
              {detail.venue.name}
            </span>
          </div>
          <div className="text-[11px] text-[var(--atlas-text-secondary)] mt-0.5">
            {detail.base_asset.name} &middot; Quoted in {detail.quote_asset_symbol} ({detail.quote_asset_type})
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-hover)] transition-colors"
          title="Close Inspector"
          aria-label="Close Inspector"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      {/* Quotation Orientation Card */}
      <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/60 border border-[var(--atlas-border-subtle)]">
        <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] tracking-wider">
          Market Orientation
        </div>
        <div className="font-mono text-xs font-medium text-[var(--atlas-text-primary)] mt-1">
          1 {detail.base_asset.symbol} ={" "}
          <span className="text-emerald-400 font-bold">
            {formatCryptoPrice(quote.last_price, detail.price_precision, detail.quote_asset_symbol)}
          </span>
        </div>
        <div className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5">
          Symbol on {detail.venue.name}: <span className="font-mono text-zinc-300">{detail.venue_market_symbol}</span>
        </div>
      </div>

      {/* Spot Price & Spread Breakdown */}
      <div className="grid grid-cols-2 gap-2">
        <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/40 border border-[var(--atlas-border-subtle)]">
          <div className="text-[10px] text-[var(--atlas-text-tertiary)]">Last Price</div>
          <div className="text-sm font-bold font-mono text-[var(--atlas-text-primary)] mt-0.5">
            {formatCryptoPrice(quote.last_price, detail.price_precision)}
          </div>
          <div className="text-[10px] font-sans mt-0.5">
            <span className={`inline-block px-1 rounded text-[9px] border ${rateKind.badgeClass}`}>
              {rateKind.label}
            </span>
          </div>
        </div>

        <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/40 border border-[var(--atlas-border-subtle)]">
          <div className="text-[10px] text-[var(--atlas-text-tertiary)]">24h Change</div>
          <div className={`text-sm font-bold font-mono mt-0.5 ${change.colorClass}`}>
            {change.text}
          </div>
          {quote.change_24h && (
            <div className="text-[10px] font-mono text-[var(--atlas-text-tertiary)] mt-0.5">
              {formatCryptoPrice(quote.change_24h, detail.price_precision, detail.quote_asset_symbol)}
            </div>
          )}
        </div>
      </div>

      {/* Top-of-Book Bid / Ask / Spread */}
      <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/40 border border-[var(--atlas-border-subtle)] space-y-1.5">
        <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] tracking-wider">
          Top of Book (Level 1)
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Bid:</span>
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatCryptoPrice(quote.bid, detail.price_precision)}
          </span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Ask:</span>
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatCryptoPrice(quote.ask, detail.price_precision)}
          </span>
        </div>
        <div className="flex justify-between items-center text-xs pt-1 border-t border-[var(--atlas-border-subtle)]">
          <span className="text-[var(--atlas-text-tertiary)]">Spread:</span>
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatCryptoSpread(quote.spread_absolute, detail.price_precision)}
            {quote.spread_bps !== null && quote.spread_bps !== undefined && (
              <span className="text-[10px] text-[var(--atlas-text-tertiary)] ml-1">
                ({formatCryptoSpreadBps(quote.spread_bps)})
              </span>
            )}
          </span>
        </div>
        {quote.midpoint && (
          <div className="flex justify-between items-center text-xs">
            <span className="text-[var(--atlas-text-tertiary)]">Midpoint:</span>
            <span className="font-mono text-[var(--atlas-text-secondary)]">
              {formatCryptoPrice(quote.midpoint, detail.price_precision)}
            </span>
          </div>
        )}
      </div>

      {/* 24h Trading Volume */}
      <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/40 border border-[var(--atlas-border-subtle)] space-y-1">
        <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] tracking-wider">
          Reported 24h Volume
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Base Traded:</span>
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatCryptoVolume(quote.volume_24h_base, detail.base_asset.symbol)}
          </span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Quote Traded:</span>
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatCryptoVolume(quote.volume_24h_quote, detail.quote_asset_symbol)}
          </span>
        </div>
      </div>

      {/* Digital Asset Identity Details */}
      <div className="p-2.5 rounded bg-[var(--atlas-surface-secondary)]/40 border border-[var(--atlas-border-subtle)] space-y-1.5">
        <div className="flex items-center gap-1.5 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] tracking-wider">
          <Coins className="h-3 w-3 text-amber-400" aria-hidden="true" />
          <span>Base Asset Specification</span>
        </div>
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Asset Kind:</span>
          <span className="capitalize font-medium text-[var(--atlas-text-primary)]">
            {detail.base_asset.asset_kind}
          </span>
        </div>
        {detail.base_asset.network_id && (
          <div className="flex justify-between items-center text-xs">
            <span className="text-[var(--atlas-text-tertiary)]">Network:</span>
            <span className="capitalize font-mono text-[var(--atlas-text-primary)]">
              {detail.base_asset.network_id}
            </span>
          </div>
        )}
        {detail.base_asset.contract_address && (
          <div className="flex justify-between items-center text-xs">
            <span className="text-[var(--atlas-text-tertiary)]">Contract:</span>
            <div className="flex items-center gap-1">
              <span className="font-mono text-[10px] text-zinc-300 truncate max-w-[120px]">
                {detail.base_asset.contract_address.substring(0, 6)}...
                {detail.base_asset.contract_address.substring(detail.base_asset.contract_address.length - 4)}
              </span>
              <button
                type="button"
                onClick={handleCopyContract}
                className="p-0.5 rounded text-[var(--atlas-text-tertiary)] hover:text-white"
                title="Copy contract address"
              >
                {copiedContract ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
              </button>
            </div>
          </div>
        )}
        <div className="flex justify-between items-center text-xs">
          <span className="text-[var(--atlas-text-tertiary)]">Decimals:</span>
          <span className="font-mono text-[var(--atlas-text-primary)]">{detail.base_asset.decimals}</span>
        </div>
      </div>

      {/* Provenance & Observation Metadata */}
      <div className="space-y-1 text-[11px] text-[var(--atlas-text-tertiary)] pt-1 border-t border-[var(--atlas-border-subtle)]">
        <div className="flex justify-between items-center">
          <span>Freshness:</span>
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${freshness.badgeClass}`}>
            {freshness.label}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span>Provider:</span>
          <span className="font-medium text-[var(--atlas-text-secondary)]">{quote.provider}</span>
        </div>
        <div className="flex justify-between items-center">
          <span>Observed:</span>
          <span className="font-mono text-[10px]">{formatObservedTimestamp(quote.observed_at)}</span>
        </div>
        <div className="flex justify-between items-center">
          <span>Instrument UUID:</span>
          <div className="flex items-center gap-1 font-mono text-[10px] text-zinc-400">
            <span>{detail.instrument_entity_id.substring(0, 8)}...</span>
            <button
              type="button"
              onClick={handleCopyUuid}
              className="p-0.5 text-zinc-400 hover:text-white"
              title="Copy UUID"
            >
              {copiedId ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex items-center gap-2 pt-1">
        <Link
          href={`/charts?entityId=${detail.instrument_entity_id}`}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-emerald-950/30 hover:bg-emerald-950/50 text-emerald-400 border border-emerald-800/40 transition-colors"
        >
          <BarChart2 className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Open Charts</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>
        <Link
          href={`/research?entityId=${detail.base_asset.asset_entity_id}`}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700/60 transition-colors"
        >
          <BookOpen className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Research</span>
        </Link>
      </div>

      {/* Non-Executable Notice */}
      <div className="flex items-start gap-1.5 p-2 rounded bg-zinc-900/50 border border-zinc-800 text-[10px] text-[var(--atlas-text-tertiary)]">
        <Info className="h-3.5 w-3.5 text-zinc-400 shrink-0 mt-0.5" aria-hidden="true" />
        <span>{detail.disclaimer}</span>
      </div>
    </aside>
  );
}
