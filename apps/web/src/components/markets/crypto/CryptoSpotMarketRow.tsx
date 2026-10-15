"use client";

import React from "react";
import {
  CryptoSpotMarketDirectoryItem,
  formatCryptoChange,
  formatCryptoFreshnessBadge,
  formatCryptoPrice,
  formatCryptoRateKind,
  formatCryptoSpread,
  formatCryptoSpreadBps,
  formatCryptoVolume,
  formatObservedTimestamp,
} from "@/lib/markets/crypto";

export interface CryptoSpotMarketRowProps {
  market: CryptoSpotMarketDirectoryItem;
  isSelected: boolean;
  onSelect: (market: CryptoSpotMarketDirectoryItem) => void;
}

export function CryptoSpotMarketRow({
  market,
  isSelected,
  onSelect,
}: CryptoSpotMarketRowProps) {
  const quote = market.quote;
  const change = formatCryptoChange(quote?.change_24h_percent);
  const freshness = formatCryptoFreshnessBadge(quote?.freshness_status);
  const rateKind = formatCryptoRateKind(quote?.rate_kind);

  const quoteTypeBadgeClass =
    market.quote_asset_type === "fiat"
      ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/40"
      : market.quote_asset_type === "stablecoin"
      ? "bg-cyan-950/40 text-cyan-300 border-cyan-800/40"
      : "bg-amber-950/40 text-amber-300 border-amber-800/40";

  return (
    <tr
      onClick={() => onSelect(market)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(market);
        }
      }}
      tabIndex={0}
      role="row"
      aria-selected={isSelected}
      className={`group cursor-pointer border-b border-[var(--atlas-border-subtle)] transition-colors text-xs focus:outline-none focus:bg-[var(--atlas-surface-hover)] ${
        isSelected
          ? "bg-[var(--atlas-surface-active)] text-[var(--atlas-text-primary)]"
          : "hover:bg-[var(--atlas-surface-hover)] text-[var(--atlas-text-secondary)]"
      }`}
    >
      {/* 1. Trading Pair */}
      <td className="px-3 py-2.5 font-medium whitespace-nowrap">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-sm font-semibold text-[var(--atlas-text-primary)]">
            {market.market_symbol}
          </span>
          <span
            className={`px-1.5 py-0.5 rounded text-[10px] font-mono border capitalize ${quoteTypeBadgeClass}`}
            title={`Quoted in ${market.quote_asset_type}`}
          >
            {market.quote_asset_type}
          </span>
        </div>
        <div className="text-[10px] text-[var(--atlas-text-tertiary)] truncate mt-0.5">
          {market.base_asset_name} &middot; {market.venue_market_symbol}
        </div>
      </td>

      {/* 2. Exchange / Venue */}
      <td className="px-3 py-2.5 whitespace-nowrap">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700/50">
          {market.venue_name}
        </span>
      </td>

      {/* 3. Last Price */}
      <td className="px-3 py-2.5 text-right font-mono font-medium whitespace-nowrap text-[var(--atlas-text-primary)]">
        <div>
          {formatCryptoPrice(quote?.last_price, market.price_precision, market.quote_asset_symbol)}
        </div>
        <div className="text-[10px] font-sans">
          <span className={`inline-block px-1 rounded text-[9px] border ${rateKind.badgeClass}`}>
            {rateKind.label}
          </span>
        </div>
      </td>

      {/* 4. Bid */}
      <td className="px-3 py-2.5 text-right font-mono whitespace-nowrap text-[var(--atlas-text-secondary)]">
        {formatCryptoPrice(quote?.bid, market.price_precision)}
      </td>

      {/* 5. Ask */}
      <td className="px-3 py-2.5 text-right font-mono whitespace-nowrap text-[var(--atlas-text-secondary)]">
        {formatCryptoPrice(quote?.ask, market.price_precision)}
      </td>

      {/* 6. Spread */}
      <td className="px-3 py-2.5 text-right font-mono whitespace-nowrap">
        <div className="text-[var(--atlas-text-primary)]">
          {formatCryptoSpread(quote?.spread_absolute, market.price_precision)}
        </div>
        {quote?.spread_bps !== null && quote?.spread_bps !== undefined && (
          <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
            {formatCryptoSpreadBps(quote.spread_bps)}
          </div>
        )}
      </td>

      {/* 7. 24h Change */}
      <td className={`px-3 py-2.5 text-right font-mono font-medium whitespace-nowrap ${change.colorClass}`}>
        {change.text}
      </td>

      {/* 8. 24h Volume */}
      <td className="px-3 py-2.5 text-right font-mono whitespace-nowrap">
        <div className="text-[var(--atlas-text-primary)]">
          {formatCryptoVolume(quote?.volume_24h_base, market.base_asset_symbol)}
        </div>
        {quote?.volume_24h_quote && (
          <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
            {formatCryptoVolume(quote.volume_24h_quote, market.quote_asset_symbol)}
          </div>
        )}
      </td>

      {/* 9. Data Status */}
      <td className="px-3 py-2.5 text-center whitespace-nowrap">
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border ${freshness.badgeClass}`}
        >
          {freshness.label}
        </span>
      </td>

      {/* 10. Source & Timestamp */}
      <td className="px-3 py-2.5 text-right text-[11px] text-[var(--atlas-text-tertiary)] whitespace-nowrap">
        <div className="font-medium text-zinc-400">{quote?.provider || "OPENBB"}</div>
        <div className="text-[10px]">{formatObservedTimestamp(quote?.observed_at)}</div>
      </td>
    </tr>
  );
}
