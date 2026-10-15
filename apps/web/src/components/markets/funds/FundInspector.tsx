"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useSelectedEntity } from "@/hooks/entity";
import { useFundOverview } from "@/hooks/markets/useFundOverview";
import {
  formatAUM,
  formatExpenseRatio,
  formatFundChange,
  formatFundNAV,
  formatFundPrice,
  formatValuationDate,
} from "@/lib/markets/funds";
import {
  Activity,
  ArrowDown,
  ArrowUp,
  BarChart2,
  BookOpen,
  Briefcase,
  Check,
  Compass,
  Copy,
  Database,
  DollarSign,
  Landmark,
  Minus,
  ShieldCheck,
  X,
} from "lucide-react";

export interface FundInspectorProps {
  instrumentEntityId: string | null;
  onClose: () => void;
}

export function FundInspector({
  instrumentEntityId,
  onClose,
}: FundInspectorProps) {
  const { selectEntity } = useSelectedEntity();
  const { data, isLoading, isError, error } = useFundOverview(instrumentEntityId);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!instrumentEntityId) return null;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const item = data?.item;
  const identifiers = data?.identifiers || [];
  const venue = data?.venue_details;
  const benchmark = data?.benchmark_details;
  const management = data?.management_details;
  const limitations = data?.coverage_limitations || [];

  const isExchangeTraded = item?.is_exchange_traded;
  const quote = item?.market_quote;
  const nav = item?.official_nav;
  const fees = item?.fees;
  const aum = item?.aum;

  const priceChange = quote?.percentage_change
    ? formatFundChange(quote.percentage_change)
    : null;

  return (
    <aside
      aria-label="Fund inspector"
      className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md flex flex-col h-full max-h-[85vh] overflow-hidden shadow-lg animate-in fade-in slide-in-from-right-2 duration-150"
    >
      {/* Top Title & Close Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/80">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
            Fund Inspector
          </span>
          {item?.fund_type_label && (
            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {item.fund_type_label}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close fund inspector"
          className="p-1 rounded text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-hover)] transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div className="p-4 overflow-y-auto space-y-4 flex-1">
        {/* Loading state */}
        {isLoading && (
          <div className="space-y-3 animate-pulse">
            <div className="h-6 bg-zinc-800 rounded w-3/4"></div>
            <div className="h-4 bg-zinc-800 rounded w-1/2"></div>
            <div className="h-20 bg-zinc-800 rounded"></div>
            <div className="h-20 bg-zinc-800 rounded"></div>
          </div>
        )}

        {/* Error state */}
        {!isLoading && isError && (
          <div className="p-3 rounded bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
            {error?.message || "Failed to load fund details."}
          </div>
        )}

        {/* Loaded Content */}
        {!isLoading && item && (
          <>
            {/* Header: Name, Ticker, Category */}
            <div>
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="text-base font-bold text-[var(--atlas-text-primary)] truncate">
                  {item.display_name}
                </h2>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-[var(--atlas-surface-card)] text-emerald-400 border border-[var(--atlas-border-subtle)]">
                  {item.display_symbol}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-1.5 mt-1 text-xs text-[var(--atlas-text-tertiary)]">
                <span>{item.fund_category}</span>
                <span>•</span>
                <span>Domicile: {item.domicile}</span>
                <span>•</span>
                <span>CCY: {item.share_class_currency}</span>
                {item.distribution_policy && (
                  <>
                    <span>•</span>
                    <span>{item.distribution_policy}</span>
                  </>
                )}
              </div>
            </div>

            {/* Canonical Instrument UUID Block */}
            <div className="p-2.5 rounded bg-[var(--atlas-surface-card)]/50 border border-[var(--atlas-border-subtle)]">
              <div className="flex items-center justify-between text-[11px] text-[var(--atlas-text-secondary)] mb-1">
                <span>Financial Instrument UUID</span>
                <button
                  type="button"
                  onClick={() => handleCopy(item.instrument_entity_id, "inst_id")}
                  className="inline-flex items-center gap-1 text-[10px] text-emerald-400 hover:text-emerald-300"
                >
                  {copiedId === "inst_id" ? (
                    <>
                      <Check className="h-3 w-3" /> Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" /> Copy
                    </>
                  )}
                </button>
              </div>
              <div className="font-mono text-[11px] text-[var(--atlas-text-primary)] break-all select-all">
                {item.instrument_entity_id}
              </div>
            </div>

            {/* 1. Market Price (Exchange-Traded Products) */}
            {isExchangeTraded ? (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1.5">
                  <span className="flex items-center gap-1.5">
                    <Activity className="h-3.5 w-3.5 text-emerald-400" />
                    Exchange Market Quote (Trade)
                  </span>
                  {quote?.freshness_status && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
                      {quote.freshness_status}
                    </span>
                  )}
                </div>

                <div className="flex items-baseline justify-between mt-2">
                  <div className="text-2xl font-bold font-mono text-[var(--atlas-text-primary)]">
                    {formatFundPrice(quote?.last_price, item.trading_currency)}
                  </div>
                  {priceChange && (
                    <div className={`flex items-center gap-1 font-mono text-xs font-semibold ${priceChange.colorClass}`}>
                      {priceChange.isPositive && <ArrowUp className="h-3.5 w-3.5" />}
                      {priceChange.isNegative && <ArrowDown className="h-3.5 w-3.5" />}
                      {!priceChange.isPositive && !priceChange.isNegative && (
                        <Minus className="h-3.5 w-3.5 opacity-40" />
                      )}
                      <span>{priceChange.text}</span>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2 mt-3 pt-2.5 border-t border-[var(--atlas-border-subtle)] text-[11px]">
                  <div>
                    <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">Bid</span>
                    <span className="font-mono text-[var(--atlas-text-secondary)]">
                      {formatFundPrice(quote?.bid_price, item.trading_currency)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">Ask</span>
                    <span className="font-mono text-[var(--atlas-text-secondary)]">
                      {formatFundPrice(quote?.ask_price, item.trading_currency)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">Ref Close</span>
                    <span className="font-mono text-[var(--atlas-text-secondary)]">
                      {formatFundPrice(quote?.reference_close, item.trading_currency)}
                    </span>
                  </div>
                </div>

                <div className="mt-2.5 pt-2 border-t border-[var(--atlas-border-subtle)] text-[10px] text-[var(--atlas-text-tertiary)] flex justify-between">
                  <span>
                    Observed: {quote?.source_timestamp ? new Date(quote.source_timestamp).toLocaleTimeString() : "Recent"}
                  </span>
                  <span>Feed: {quote?.provider_display_name || "OpenBB / Polygon"}</span>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium mb-1.5">
                  <Landmark className="h-3.5 w-3.5 text-blue-400" />
                  <span>Trading Structure</span>
                </div>
                <div className="text-xs text-[var(--atlas-text-primary)] font-semibold">
                  Unlisted Open-End Mutual Fund
                </div>
                <p className="text-[11px] text-[var(--atlas-text-tertiary)] mt-1">
                  This instrument does not trade on an exchange secondary market with continuous bids and asks. Purchases and redemptions occur directly with the fund manager at official Net Asset Value (NAV).
                </p>
              </div>
            )}

            {/* Listing Venue Section */}
            {venue && (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium mb-2">
                  <Landmark className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Exchange Venue</span>
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-[var(--atlas-text-tertiary)]">Venue Name</span>
                    <span className="font-medium text-[var(--atlas-text-primary)]">
                      {venue.name}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--atlas-text-tertiary)]">Operating MIC</span>
                    <span className="font-mono text-[var(--atlas-text-primary)]">
                      {venue.mic}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--atlas-text-tertiary)]">Jurisdiction</span>
                    <span className="text-[var(--atlas-text-primary)]">{venue.country}</span>
                  </div>
                </div>
              </div>
            )}

            {/* 2. Official Net Asset Value (NAV) Section */}
            <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
              <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1.5">
                <span className="flex items-center gap-1.5">
                  <Database className="h-3.5 w-3.5 text-amber-400" />
                  Official Net Asset Value (NAV)
                </span>
                {nav?.is_available ? (
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono text-amber-400 bg-amber-950/40 border border-amber-800/40">
                    Valuation Point
                  </span>
                ) : (
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono text-zinc-500 bg-zinc-900 border border-zinc-800">
                    Unavailable
                  </span>
                )}
              </div>

              {nav?.is_available ? (
                <>
                  <div className="flex items-baseline justify-between mt-2">
                    <div className="text-2xl font-bold font-mono text-amber-400">
                      {formatFundNAV(nav.nav_per_unit, nav.nav_currency || item.share_class_currency)}
                    </div>
                    <div className="text-xs text-[var(--atlas-text-tertiary)]">
                      Method: <span className="font-mono text-[var(--atlas-text-secondary)]">{nav.valuation_method}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-3 pt-2.5 border-t border-[var(--atlas-border-subtle)] text-[11px]">
                    <div>
                      <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">Valuation Date</span>
                      <span className="font-medium text-[var(--atlas-text-primary)]">
                        {formatValuationDate(nav.valuation_date)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">NAV Currency</span>
                      <span className="font-mono text-[var(--atlas-text-primary)]">
                        {nav.nav_currency || item.share_class_currency}
                      </span>
                    </div>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-[var(--atlas-border-subtle)] text-[10px] text-[var(--atlas-text-tertiary)] flex justify-between">
                    <span>Source: {nav.provenance || "authoritative_fund_catalog"}</span>
                    <span>Scope: Share Class</span>
                  </div>
                </>
              ) : (
                <div className="text-xs text-[var(--atlas-text-tertiary)] italic py-2">
                  Official NAV observation unavailable for this share class.
                </div>
              )}
            </div>

            {/* 3. Fees and Assets Under Management (AUM) */}
            <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
              <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium mb-2.5">
                <DollarSign className="h-3.5 w-3.5 text-emerald-400" />
                <span>Fees & Assets Under Management</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                {/* Net Expense Ratio */}
                <div className="p-2 rounded bg-zinc-900/50 border border-zinc-800">
                  <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
                    Net Expense Ratio
                  </span>
                  <div className="text-base font-bold font-mono text-[var(--atlas-text-primary)] mt-0.5">
                    {fees?.is_available ? formatExpenseRatio(fees.net_expense_ratio, fees.fee_scale) : "—"}
                  </div>
                  <span className="text-[9px] text-[var(--atlas-text-tertiary)] block mt-0.5">
                    Scale: {fees?.fee_scale || "percentage"}
                  </span>
                </div>

                {/* Total AUM */}
                <div className="p-2 rounded bg-zinc-900/50 border border-zinc-800">
                  <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
                    Reported AUM
                  </span>
                  <div className="text-base font-bold font-mono text-[var(--atlas-text-primary)] mt-0.5">
                    {aum?.is_available ? formatAUM(aum.amount, aum.currency) : "—"}
                  </div>
                  <span className="text-[9px] text-[var(--atlas-text-tertiary)] block mt-0.5 truncate">
                    Scope: {aum?.scope || "Fund Net Assets"}
                  </span>
                </div>
              </div>
            </div>

            {/* 4. Benchmark & Strategy */}
            {benchmark && (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
                    <Compass className="h-3.5 w-3.5 text-amber-400" />
                    <span>Tracked Benchmark</span>
                  </div>
                  {benchmark.is_verified && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
                      <ShieldCheck className="h-3 w-3" />
                      Verified Index
                    </span>
                  )}
                </div>
                <div className="text-xs font-semibold text-[var(--atlas-text-primary)]">
                  {benchmark.name}
                </div>
                {benchmark.description && (
                  <p className="text-[11px] text-[var(--atlas-text-tertiary)] mt-1">
                    {benchmark.description}
                  </p>
                )}
              </div>
            )}

            {/* 5. Sponsor & Management */}
            {management && (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
                    <Briefcase className="h-3.5 w-3.5 text-blue-400" />
                    <span>Manager & Sponsor</span>
                  </div>
                  {management.is_verified && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
                      <ShieldCheck className="h-3 w-3" />
                      Verified
                    </span>
                  )}
                </div>
                <div className="text-xs font-semibold text-[var(--atlas-text-primary)]">
                  {management.name}
                </div>
                <div className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5">
                  Role: {management.role}
                </div>
              </div>
            )}

            {/* 6. Canonical Identifiers */}
            {identifiers.length > 0 && (
              <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
                <div className="text-xs text-[var(--atlas-text-secondary)] font-medium mb-1.5">
                  Canonical Identifiers
                </div>
                <div className="space-y-1">
                  {identifiers.map((ident) => (
                    <div
                      key={`${ident.scheme}-${ident.value}`}
                      className="flex items-center justify-between text-xs font-mono"
                    >
                      <span className="text-[var(--atlas-text-tertiary)] uppercase text-[10px]">
                        {ident.scheme}
                      </span>
                      <span className="text-[var(--atlas-text-primary)]">
                        {ident.value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 7. Coverage Limitations Notice */}
            {limitations.length > 0 && (
              <div className="p-2.5 rounded bg-zinc-900/60 border border-zinc-800 text-[10px] text-zinc-400 space-y-1">
                <span className="font-semibold text-zinc-300 block">Data Limitations:</span>
                <ul className="list-disc list-inside space-y-0.5">
                  {limitations.map((lim, idx) => (
                    <li key={idx}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions: Open Charts / Open Research */}
            <div className="pt-2 flex items-center gap-2">
              {isExchangeTraded && (
                <Link
                  href="/charts"
                  onClick={() => selectEntity(item.instrument_entity_id)}
                  className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
                >
                  <BarChart2 className="h-3.5 w-3.5" />
                  <span>Open Charts</span>
                </Link>
              )}
              <Link
                href="/research"
                onClick={() => selectEntity(item.instrument_entity_id)}
                className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-amber-500/50"
              >
                <BookOpen className="h-3.5 w-3.5" />
                <span>Open Research</span>
              </Link>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
