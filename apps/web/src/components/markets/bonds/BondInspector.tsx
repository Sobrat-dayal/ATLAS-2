"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  BarChart2,
  BookOpen,
  Building2,
  Calendar,
  Coins,
  Info,
  Percent,
  ShieldAlert,
  X,
} from "lucide-react";
import {
  BondOverviewResponse,
  formatBondCoupon,
  formatBondMaturity,
  formatBondPrice,
  formatBondSpread,
  formatBondType,
  formatBondYield,
  formatObservationTime,
  formatPriceBasis,
  formatPriceKind,
  formatYieldChangeBps,
  formatYieldTypeLabel,
  getDirectionColorClass,
  getFreshnessBadgeClass,
} from "@/lib/markets/bonds";

export interface BondInspectorProps {
  overview: BondOverviewResponse | null;
  isLoading: boolean;
  onClose: () => void;
}

export function BondInspector({
  overview,
  isLoading,
  onClose,
}: BondInspectorProps) {
  if (isLoading && !overview) {
    return (
      <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-4 h-full animate-pulse">
        <div className="h-6 w-3/4 bg-zinc-800 rounded mb-4" />
        <div className="space-y-3">
          <div className="h-20 bg-zinc-800 rounded" />
          <div className="h-28 bg-zinc-800 rounded" />
          <div className="h-28 bg-zinc-800 rounded" />
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-6 text-center text-[var(--atlas-text-tertiary)] flex flex-col items-center justify-center min-h-[300px]">
        <Info className="h-8 w-8 text-zinc-600 mb-2" aria-hidden="true" />
        <p className="text-xs">Select a bond security to inspect contractual terms, clean/dirty prices, and yield observations.</p>
      </div>
    );
  }

  const { terms, price, yield_obs, issuer } = overview;

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-4 flex flex-col gap-4 text-xs">
      {/* Top Header */}
      <div className="flex items-start justify-between gap-3 border-b border-[var(--atlas-border-subtle)] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-[var(--atlas-text-primary)] font-mono">
              {overview.symbol}
            </h2>
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono border ${getFreshnessBadgeClass(
                price.freshness_status
              )}`}
            >
              {price.freshness_status}
            </span>
          </div>
          <p className="text-xs text-[var(--atlas-text-secondary)] mt-0.5 line-clamp-1 font-medium">
            {overview.name}
          </p>
          <div className="flex items-center gap-2 mt-1 text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
            <span>ISIN: {overview.isin || "—"}</span>
            {overview.cusip && <span>• CUSIP: {overview.cusip}</span>}
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-subtle)] transition-colors"
          title="Close Inspector"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      {/* Navigation Quick Actions */}
      <div className="grid grid-cols-3 gap-2">
        <Link
          href={`/companies?query=${encodeURIComponent(issuer.name)}`}
          className="inline-flex items-center justify-center gap-1.5 py-1.5 px-2 bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] transition-colors"
        >
          <Building2 className="h-3.5 w-3.5 text-blue-400" aria-hidden="true" />
          <span>Issuer</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>

        <Link
          href={`/charts?instrument=${encodeURIComponent(overview.instrument_entity_id)}`}
          className="inline-flex items-center justify-center gap-1.5 py-1.5 px-2 bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] transition-colors"
        >
          <BarChart2 className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
          <span>Charts</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>

        <Link
          href={`/research?query=${encodeURIComponent(overview.isin || overview.symbol)}`}
          className="inline-flex items-center justify-center gap-1.5 py-1.5 px-2 bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] transition-colors"
        >
          <BookOpen className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
          <span>Research</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>
      </div>

      {/* Card 1: Legal Issuer Details */}
      <div className="bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--atlas-text-tertiary)] uppercase tracking-wider">
          <span>Legal Debt Issuer</span>
          <span className="capitalize">{issuer.issuer_category}</span>
        </div>
        <div>
          <div className="font-medium text-[var(--atlas-text-primary)] text-sm">
            {issuer.name}
          </div>
          <div className="flex items-center gap-2 mt-1 text-[11px] text-[var(--atlas-text-secondary)]">
            <span>Jurisdiction: {issuer.jurisdiction}</span>
            <span>• Country: {issuer.country_code}</span>
          </div>
        </div>
      </div>

      {/* Card 2: Price Observations (Clean vs Dirty vs Accrued) */}
      <div className="bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2.5">
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--atlas-text-tertiary)] uppercase tracking-wider">
          <div className="flex items-center gap-1">
            <Coins className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
            <span>Price Observations</span>
          </div>
          <span>{formatPriceKind(price.price_kind)}</span>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-[var(--atlas-border-subtle)]/50">
          <div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)] uppercase font-mono">
              Clean Price
            </div>
            <div className="text-base font-bold font-mono text-[var(--atlas-text-primary)]">
              {formatBondPrice(price.clean_price, price.quote_unit)}
            </div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
              Excludes accrued interest
            </div>
          </div>

          <div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)] uppercase font-mono">
              Dirty Price
            </div>
            <div className="text-base font-bold font-mono text-[var(--atlas-text-primary)]">
              {formatBondPrice(price.dirty_price, price.quote_unit)}
            </div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
              Settlement invoice price
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[var(--atlas-border-subtle)]/50 text-[11px]">
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Accrued Interest: </span>
            <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {price.accrued_interest ? formatBondPrice(price.accrued_interest, price.quote_unit) : "—"}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Quotation Basis: </span>
            <span className="font-mono font-medium text-[var(--atlas-text-primary)] capitalize">
              {formatPriceBasis(price.price_basis)}
            </span>
          </div>
        </div>

        {price.bid && price.ask && (
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--atlas-border-subtle)]/50 text-[11px]">
            <div>
              <span className="text-[var(--atlas-text-tertiary)]">Bid: </span>
              <span className="font-mono text-[var(--atlas-text-primary)]">{formatBondPrice(price.bid, price.quote_unit)}</span>
            </div>
            <div>
              <span className="text-[var(--atlas-text-tertiary)]">Ask: </span>
              <span className="font-mono text-[var(--atlas-text-primary)]">{formatBondPrice(price.ask, price.quote_unit)}</span>
            </div>
            <div>
              <span className="text-[var(--atlas-text-tertiary)]">Spread: </span>
              <span className="font-mono text-[var(--atlas-text-primary)]">{formatBondSpread(price.spread)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Card 3: Yield Observations */}
      <div className="bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2.5">
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--atlas-text-tertiary)] uppercase tracking-wider">
          <div className="flex items-center gap-1">
            <Percent className="h-3.5 w-3.5 text-cyan-400" aria-hidden="true" />
            <span>Yield Observations</span>
          </div>
          <span>{formatYieldTypeLabel(yield_obs.yield_type)}</span>
        </div>

        <div className="flex items-baseline justify-between pt-1 border-t border-[var(--atlas-border-subtle)]/50">
          <div>
            <div className="text-xl font-bold font-mono text-cyan-400">
              {formatBondYield(yield_obs.yield_value, yield_obs.yield_type)}
            </div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
              Annualized Yield ({yield_obs.yield_unit})
            </div>
          </div>

          <div className="text-right">
            <div className={`text-sm font-bold font-mono ${getDirectionColorClass(yield_obs.yield_change_bps_24h)}`}>
              {formatYieldChangeBps(yield_obs.yield_change_bps_24h)}
            </div>
            <div className="text-[10px] text-[var(--atlas-text-tertiary)]">
              24h Yield Movement
            </div>
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-[10px] text-[var(--atlas-text-tertiary)]">
          <Info className="h-3 w-3 inline mr-1 text-cyan-400" aria-hidden="true" />
          Yield is derived from market price and cash-flow timing; distinct from contractual coupon rate.
        </div>
      </div>

      {/* Card 4: Contractual Terms & Schedule */}
      <div className="bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--atlas-text-tertiary)] uppercase tracking-wider">
          <div className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5 text-teal-400" aria-hidden="true" />
            <span>Contractual Terms</span>
          </div>
          <span>{formatBondType(overview.bond_type)}</span>
        </div>

        <div className="grid grid-cols-2 gap-y-1.5 gap-x-2 pt-1 border-t border-[var(--atlas-border-subtle)]/50 text-[11px]">
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Coupon Rate: </span>
            <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {formatBondCoupon(terms.coupon_rate, terms.coupon_type)}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Frequency: </span>
            <span className="font-mono capitalize text-[var(--atlas-text-primary)]">
              {terms.coupon_frequency.toLowerCase()}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Issue Date: </span>
            <span className="font-mono text-[var(--atlas-text-primary)]">{terms.issue_date}</span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Maturity Date: </span>
            <span className="font-mono text-[var(--atlas-text-primary)]">
              {formatBondMaturity(terms.maturity_date, terms.is_perpetual)}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Day Count: </span>
            <span className="font-mono text-[var(--atlas-text-primary)]">{terms.day_count_convention}</span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Seniority: </span>
            <span className="font-mono capitalize text-[var(--atlas-text-primary)]">
              {terms.seniority.replace("_", " ").toLowerCase()}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Callable: </span>
            <span className="font-mono text-[var(--atlas-text-primary)]">
              {terms.is_callable ? "Yes" : "No"}
            </span>
          </div>
          <div>
            <span className="text-[var(--atlas-text-tertiary)]">Face Value: </span>
            <span className="font-mono text-[var(--atlas-text-primary)]">
              {terms.face_value} {overview.currency}
            </span>
          </div>
        </div>
      </div>

      {/* Card 5: Provenance & Non-Executable Disclaimer */}
      <div className="bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
          <span>Source: {price.provider}</span>
          <span>Updated: {formatObservationTime(price.source_timestamp)}</span>
        </div>

        <div className="flex items-start gap-1.5 p-2 rounded bg-amber-500/5 border border-amber-500/20 text-[10px] text-amber-400/90 leading-relaxed">
          <ShieldAlert className="h-3.5 w-3.5 shrink-0 mt-0.5" aria-hidden="true" />
          <span>{overview.non_executable_disclaimer}</span>
        </div>
      </div>
    </div>
  );
}
