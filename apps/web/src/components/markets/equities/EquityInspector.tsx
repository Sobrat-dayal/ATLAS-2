"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSelectedEntity } from "@/hooks/entity";
import { useEquityOverview } from "@/hooks/markets/useEquityOverview";
import {
  formatEquityPrice,
  formatAbsoluteChange,
  formatPercentageChange,
  formatEquitySubtype,
  getFreshnessBadge,
  getDirectionColorClass,
  formatObservationTime,
} from "@/lib/markets/equities";
import {
  Activity,
  ArrowDown,
  ArrowUp,
  ArrowUpRight,
  BarChart2,
  Building2,
  Check,
  Copy,
  Landmark,
  Minus,
  ShieldCheck,
  X,
} from "lucide-react";

export interface EquityInspectorProps {
  instrumentEntityId: string | null;
  onClose: () => void;
}

export function EquityInspector({
  instrumentEntityId,
  onClose,
}: EquityInspectorProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();
  const { data, isLoading, isError, error } = useEquityOverview(instrumentEntityId);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!instrumentEntityId) return null;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleOpenCompany = (companyId: string) => {
    // Explicitly transition selected entity context to Company UUID per Stage 23/25
    selectEntity(companyId);
    router.push("/companies");
  };

  const item = data?.item;
  const issuer = data?.issuer_company;
  const venue = data?.venue_details;
  const identifiers = data?.identifiers || [];
  const limitations = data?.coverage_limitations || [];

  const freshness = getFreshnessBadge(item?.freshness_status);
  const colorClass = getDirectionColorClass(
    item?.change_direction || "unknown"
  );

  return (
    <aside
      aria-label="Equity security inspector"
      className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md flex flex-col h-full max-h-[85vh] overflow-hidden shadow-lg animate-in fade-in slide-in-from-right-2 duration-150"
    >
      {/* Top Title & Close Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/80">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
            Security Inspector
          </span>
          {item?.listing_status && (
            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {item.listing_status}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close equity inspector"
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
            <div className="h-16 bg-zinc-800 rounded"></div>
            <div className="h-24 bg-zinc-800 rounded"></div>
          </div>
        )}

        {/* Error state */}
        {!isLoading && isError && (
          <div className="p-3 rounded bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
            {error?.message || "Failed to load security overview."}
          </div>
        )}

        {/* Loaded Content */}
        {!isLoading && item && (
          <>
            {/* Header: Name, Symbol, Subtype */}
            <div>
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="text-base font-bold text-[var(--atlas-text-primary)] truncate">
                  {item.display_name}
                </h2>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-[var(--atlas-surface-card)] text-emerald-400 border border-[var(--atlas-border-subtle)]">
                  {item.display_symbol}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-1 text-xs text-[var(--atlas-text-tertiary)]">
                <span>{formatEquitySubtype(item.equity_subtype)}</span>
                <span>•</span>
                <span>{item.listing_market_country}</span>
                <span>•</span>
                <span className="font-mono">{item.trading_currency}</span>
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

            {/* Latest Price & Price Change Card */}
            <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
              <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1.5">
                <span className="flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-sky-400" />
                  Latest Quote Observation
                </span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-medium border ${freshness.className}`}
                >
                  {freshness.label}
                </span>
              </div>

              <div className="flex items-baseline justify-between mt-2">
                <div className="text-2xl font-bold font-mono text-[var(--atlas-text-primary)]">
                  {formatEquityPrice(item.last_price, item.trading_currency)}
                </div>
                <div className={`flex items-center gap-1 font-mono text-xs font-semibold ${colorClass}`}>
                  {item.change_direction === "up" && (
                    <ArrowUp className="h-3.5 w-3.5" />
                  )}
                  {item.change_direction === "down" && (
                    <ArrowDown className="h-3.5 w-3.5" />
                  )}
                  {item.change_direction === "flat" && (
                    <Minus className="h-3.5 w-3.5 opacity-40" />
                  )}
                  <span>{formatAbsoluteChange(item.absolute_change, item.trading_currency)}</span>
                  <span>({formatPercentageChange(item.percentage_change)})</span>
                </div>
              </div>

              {/* Bid / Ask and Reference Close grid */}
              <div className="grid grid-cols-3 gap-2 mt-3 pt-2.5 border-t border-[var(--atlas-border-subtle)] text-[11px]">
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Bid
                  </span>
                  <span className="font-mono text-[var(--atlas-text-secondary)]">
                    {formatEquityPrice(item.bid_price, item.trading_currency)}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Ask
                  </span>
                  <span className="font-mono text-[var(--atlas-text-secondary)]">
                    {formatEquityPrice(item.ask_price, item.trading_currency)}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Prior Close
                  </span>
                  <span className="font-mono text-[var(--atlas-text-secondary)]">
                    {formatEquityPrice(item.reference_close, item.trading_currency)}
                  </span>
                </div>
              </div>

              {/* Source Timestamp & Provider Provenance */}
              <div className="mt-2.5 pt-2 border-t border-[var(--atlas-border-subtle)] text-[10px] text-[var(--atlas-text-tertiary)] flex justify-between">
                <span>
                  Observed: {formatObservationTime(item.source_timestamp || item.received_at)}
                </span>
                <span>Source: {item.provider_display_name || "Canonical Feed"}</span>
              </div>
            </div>

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

            {/* Verified Issuer Company Section */}
            <div className="p-3 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
                  <Building2 className="h-3.5 w-3.5 text-blue-400" />
                  <span>Issuer Company</span>
                </div>
                {issuer?.verified && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
                    <ShieldCheck className="h-3 w-3" />
                    Verified Link
                  </span>
                )}
              </div>

              {issuer ? (
                <div className="space-y-2">
                  <div className="text-xs">
                    <div className="font-semibold text-[var(--atlas-text-primary)]">
                      {issuer.canonical_name}
                    </div>
                    {issuer.country_of_incorporation && (
                      <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
                        Incorporated in {issuer.country_of_incorporation}
                      </div>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleOpenCompany(issuer.company_entity_id)}
                    className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500/50"
                  >
                    <span>Open Company</span>
                    <ArrowUpRight className="h-3 w-3" />
                  </button>
                </div>
              ) : (
                <div className="text-[11px] text-[var(--atlas-text-tertiary)] italic">
                  Issuer relationship unavailable in canonical catalog.
                </div>
              )}
            </div>

            {/* Identifiers List */}
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

            {/* Coverage Limitations Transparency */}
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

            {/* Primary Action Buttons */}
            <div className="pt-2 flex items-center gap-2">
              <Link
                href="/charts"
                className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
              >
                <BarChart2 className="h-3.5 w-3.5" />
                <span>Open Charts</span>
              </Link>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
