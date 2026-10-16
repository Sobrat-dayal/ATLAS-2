"use client";

import React from "react";
import Link from "next/link";
import {
  AlertCircle,
  BarChart2,
  BookOpen,
  Calendar,
  ExternalLink,
  Layers,
  Scale,
  Shield,
  TrendingUp,
  X,
} from "lucide-react";
import {
  FuturesContractOverviewResponse,
  formatContractMonth,
  formatContractSize,
  formatDate,
  formatFuturesPrice,
  formatObservationTime,
  formatOpenInterest,
  formatPriceChange,
  formatPriceChangeClass,
  formatSettlementType,
  formatTickSpecs,
  formatTicksChange,
  formatVolume,
  getFreshnessBadgeClass,
} from "@/lib/markets/futures";

export interface FuturesContractInspectorProps {
  overview: FuturesContractOverviewResponse | null;
  isLoading: boolean;
  onClose: () => void;
}

export function FuturesContractInspector({
  overview,
  isLoading,
  onClose,
}: FuturesContractInspectorProps) {
  if (isLoading) {
    return (
      <aside
        aria-label="Contract Inspector Loading"
        className="h-full flex flex-col p-4 bg-[var(--atlas-surface-card)] border-l border-[var(--atlas-border-subtle)] overflow-y-auto animate-pulse space-y-4"
      >
        <div className="h-6 bg-[var(--atlas-surface-subtle)] rounded w-1/2" />
        <div className="h-24 bg-[var(--atlas-surface-subtle)] rounded w-full" />
        <div className="h-40 bg-[var(--atlas-surface-subtle)] rounded w-full" />
        <div className="h-40 bg-[var(--atlas-surface-subtle)] rounded w-full" />
      </aside>
    );
  }

  if (!overview) {
    return null;
  }

  const {
    symbol,
    name,
    exchange,
    exchange_mic,
    contract_month,
    lifecycle_status,
    underlying,
    product,
    specifications,
    price_observation,
    settlement_observation,
    price_change,
    volume_open_interest,
    provider,
    freshness_status,
    delay_status,
    source_timestamp,
    received_at,
    instrument_entity_id,
  } = overview;

  const settlementBadge = formatSettlementType(specifications.settlement_type);

  const priceFormatted = formatFuturesPrice(
    price_observation.last,
    specifications.quote_unit,
    specifications.quote_currency
  );

  const settleFormatted = formatFuturesPrice(
    settlement_observation.settlement_price,
    specifications.quote_unit,
    specifications.quote_currency
  );

  const changeFormatted = formatPriceChange(
    price_change.change_absolute,
    price_change.change_percent,
    specifications.quote_unit
  );

  const changeClass = formatPriceChangeClass(price_change.change_absolute);

  return (
    <aside
      aria-label={`Inspection Details for ${symbol}`}
      className="h-full flex flex-col bg-[var(--atlas-surface-card)] border-l border-[var(--atlas-border-subtle)] text-xs overflow-y-auto"
    >
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] sticky top-0 z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base font-bold font-mono text-[var(--atlas-text-primary)]">
              {symbol}
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)]">
              {exchange}
            </span>
            <span
              className={`px-1.5 py-0.2 rounded text-[9px] font-mono uppercase tracking-wider border ${
                lifecycle_status === "active"
                  ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40"
                  : "bg-zinc-800 text-zinc-400 border-zinc-700"
              }`}
            >
              {lifecycle_status}
            </span>
          </div>
          <div className="text-xs text-[var(--atlas-text-secondary)] mt-0.5">
            {name}
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-hover)] transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          title="Close Inspector"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div className="p-4 space-y-5 flex-1">
        {/* Quick Market Overview Banner */}
        <div className="p-3 rounded bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)]">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                Latest Trade
              </div>
              <div className="text-lg font-bold font-mono text-[var(--atlas-text-primary)]">
                {priceFormatted}
              </div>
              <div className={`text-xs font-mono font-medium ${changeClass}`}>
                {changeFormatted}
              </div>
            </div>

            <div>
              <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                Official Settlement
              </div>
              <div className="text-lg font-bold font-mono text-[var(--atlas-text-secondary)]">
                {settleFormatted}
              </div>
              <div className="text-[10px] text-[var(--atlas-text-tertiary)] font-mono">
                {settlement_observation.settlement_status} ({settlement_observation.trade_date || "—"})
              </div>
            </div>
          </div>

          {price_change.change_ticks !== null && price_change.change_ticks !== undefined && (
            <div className="mt-2 pt-2 border-t border-[var(--atlas-border-subtle)] text-[11px] text-[var(--atlas-text-secondary)] flex justify-between font-mono">
              <span>Ticks Movement:</span>
              <span className={changeClass}>
                {formatTicksChange(price_change.change_ticks)}
              </span>
            </div>
          )}
        </div>

        {/* Section 1: Canonical Identity */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--atlas-text-primary)] mb-2">
            <Layers className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Canonical Identity</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] bg-[var(--atlas-surface-subtle)] p-2.5 rounded border border-[var(--atlas-border-subtle)]">
            <dt className="text-[var(--atlas-text-tertiary)]">Instrument UUID:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)] truncate" title={instrument_entity_id}>
              {instrument_entity_id.substring(0, 8)}...
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Product Root:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {product.root_symbol} ({product.name})
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Underlying Asset:</dt>
            <dd className="text-[var(--atlas-text-primary)] font-medium truncate" title={underlying.name}>
              {underlying.name}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Listing Venue:</dt>
            <dd className="font-mono text-[var(--atlas-text-primary)]">
              {exchange} (MIC: {exchange_mic})
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Commodity Category:</dt>
            <dd className="capitalize text-[var(--atlas-text-primary)]">
              {product.category.replace(/_/g, " ")}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Delivery Region:</dt>
            <dd className="text-[var(--atlas-text-secondary)] truncate" title={underlying.reference_region || ""}>
              {underlying.reference_region || "—"}
            </dd>
          </dl>
        </div>

        {/* Section 2: Contract Specifications */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--atlas-text-primary)] mb-2">
            <Scale className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Contract Specifications</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] bg-[var(--atlas-surface-subtle)] p-2.5 rounded border border-[var(--atlas-border-subtle)]">
            <dt className="text-[var(--atlas-text-tertiary)]">Contract Size:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatContractSize(specifications.contract_size, specifications.size_unit)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Quotation Unit:</dt>
            <dd className="font-mono text-[var(--atlas-text-primary)]">
              {specifications.quote_unit}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Quote Currency:</dt>
            <dd className="font-mono text-[var(--atlas-text-primary)]">
              {specifications.quote_currency}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Tick Size &amp; Value:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatTickSpecs(specifications.tick_size, specifications.tick_value, specifications.quote_currency)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Settlement Method:</dt>
            <dd>
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-medium border ${settlementBadge.badgeClass}`}>
                {settlementBadge.label}
              </span>
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Trading Schedule:</dt>
            <dd className="text-[var(--atlas-text-secondary)] text-[10px] truncate" title={specifications.trading_hours}>
              {specifications.trading_hours}
            </dd>
          </dl>
        </div>

        {/* Section 3: Schedule & Expiration Dates */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--atlas-text-primary)] mb-2">
            <Calendar className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Schedule &amp; Expiration</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] bg-[var(--atlas-surface-subtle)] p-2.5 rounded border border-[var(--atlas-border-subtle)]">
            <dt className="text-[var(--atlas-text-tertiary)]">Contract Month:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatContractMonth(contract_month)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Expiration Date:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatDate(specifications.expiration_date)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Last Trading Day:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)]">
              {formatDate(specifications.last_trading_date)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Final Settlement:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)]">
              {formatDate(specifications.settlement_date)}
            </dd>

            {specifications.first_notice_date && (
              <>
                <dt className="text-[var(--atlas-text-tertiary)]">First Notice Day:</dt>
                <dd className="font-mono text-[var(--atlas-text-secondary)]">
                  {formatDate(specifications.first_notice_date)}
                </dd>
              </>
            )}

            {specifications.delivery_start_date && specifications.delivery_end_date && (
              <>
                <dt className="text-[var(--atlas-text-tertiary)]">Delivery Window:</dt>
                <dd className="font-mono text-[10px] text-[var(--atlas-text-secondary)] truncate">
                  {specifications.delivery_start_date} to {specifications.delivery_end_date}
                </dd>
              </>
            )}
          </dl>
        </div>

        {/* Section 4: Market Depth & Liquidity */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--atlas-text-primary)] mb-2">
            <TrendingUp className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Volume &amp; Open Interest</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] bg-[var(--atlas-surface-subtle)] p-2.5 rounded border border-[var(--atlas-border-subtle)]">
            <dt className="text-[var(--atlas-text-tertiary)]">Session Volume:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatVolume(volume_open_interest.volume)} contracts
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Open Interest:</dt>
            <dd className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatOpenInterest(volume_open_interest.open_interest)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">OI As-Of Date:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)]">
              {volume_open_interest.open_interest_as_of || "—"}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Bid / Ask Spread:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)]">
              {price_observation.bid && price_observation.ask
                ? `${price_observation.bid} / ${price_observation.ask}`
                : "—"}
            </dd>
          </dl>
        </div>

        {/* Section 5: Source Provenance & Freshness */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[var(--atlas-text-primary)] mb-2">
            <Shield className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Provenance &amp; Quality</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] bg-[var(--atlas-surface-subtle)] p-2.5 rounded border border-[var(--atlas-border-subtle)]">
            <dt className="text-[var(--atlas-text-tertiary)]">Data Provider:</dt>
            <dd className="font-mono text-[var(--atlas-text-primary)]">{provider}</dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Freshness Status:</dt>
            <dd>
              <span
                className={`inline-block px-1.5 py-0.2 rounded text-[9px] font-mono uppercase tracking-wider border ${getFreshnessBadgeClass(
                  freshness_status
                )}`}
              >
                {freshness_status}
              </span>
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Delay Status:</dt>
            <dd className="font-mono text-[var(--atlas-text-secondary)]">{delay_status}</dd>

            <dt className="text-[var(--atlas-text-tertiary)]">Observed Time:</dt>
            <dd className="font-mono text-[10px] text-[var(--atlas-text-secondary)] truncate">
              {formatObservationTime(source_timestamp)}
            </dd>

            <dt className="text-[var(--atlas-text-tertiary)]">ATLAS Ingested:</dt>
            <dd className="font-mono text-[10px] text-[var(--atlas-text-secondary)] truncate">
              {formatObservationTime(received_at)}
            </dd>
          </dl>
        </div>

        {/* Cross-Module Navigation Links */}
        <div className="space-y-1.5 pt-2">
          <Link
            href={`/charts?instrument=${encodeURIComponent(instrument_entity_id)}`}
            className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium rounded bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-primary)] transition-colors"
          >
            <BarChart2 className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>Open in Interactive Charts</span>
            <ExternalLink className="h-3 w-3 text-[var(--atlas-text-tertiary)]" />
          </Link>

          <Link
            href={`/research?instrument=${encodeURIComponent(instrument_entity_id)}`}
            className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium rounded bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-primary)] transition-colors"
          >
            <BookOpen className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
            <span>View Commodity Research</span>
            <ExternalLink className="h-3 w-3 text-[var(--atlas-text-tertiary)]" />
          </Link>
        </div>

        {/* Strict Non-Executable Institutional Disclaimer */}
        <div className="p-2.5 rounded bg-[var(--atlas-surface-subtle)]/60 border border-[var(--atlas-border-subtle)] text-[10px] text-[var(--atlas-text-tertiary)] leading-relaxed flex items-start gap-2">
          <AlertCircle className="h-3.5 w-3.5 shrink-0 text-amber-400 mt-0.5" aria-hidden="true" />
          <div>
            <span className="font-semibold text-[var(--atlas-text-secondary)]">
              Derivatives Terminal Notice:
            </span>{" "}
            Stage 62 provides canonical commodity and futures contract discovery. Futures trading, broker order execution, SPAN margin calculations, options pricing, and synthetic front-month continuous rolling are strictly deferred to subsequent roadmap stages.
          </div>
        </div>
      </div>
    </aside>
  );
}
