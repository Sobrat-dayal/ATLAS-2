"use client";

import React from "react";
import { RotateCcw, Search } from "lucide-react";
import { BondFilterOptionsResponse } from "@/lib/markets/bonds";

export interface BondDirectoryFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  issuerType: string;
  onIssuerTypeChange: (it: string) => void;
  bondType: string;
  onBondTypeChange: (bt: string) => void;
  currency: string;
  onCurrencyChange: (c: string) => void;
  couponType: string;
  onCouponTypeChange: (ct: string) => void;
  maturityBucket: string;
  onMaturityBucketChange: (mb: string) => void;
  onResetFilters: () => void;
  filterOptions?: BondFilterOptionsResponse | null;
  totalResults: number;
}

export function BondDirectoryFilters({
  query,
  onQueryChange,
  issuerType,
  onIssuerTypeChange,
  bondType,
  onBondTypeChange,
  currency,
  onCurrencyChange,
  couponType,
  onCouponTypeChange,
  maturityBucket,
  onMaturityBucketChange,
  onResetFilters,
  filterOptions,
  totalResults,
}: BondDirectoryFiltersProps) {
  const currencies = filterOptions?.currencies || ["USD", "EUR", "GBP", "JPY"];
  const issuerCategories = filterOptions?.issuer_categories || [
    "sovereign",
    "corporate",
    "supranational",
  ];
  const bondTypes = filterOptions?.bond_types || [
    "sovereign",
    "corporate",
    "treasury_bill",
    "supranational",
  ];
  const couponTypes = filterOptions?.coupon_types || [
    "fixed",
    "zero_coupon",
    "floating",
  ];
  const maturityBuckets = filterOptions?.maturity_buckets || [
    "under_1_year",
    "1_to_3_years",
    "3_to_5_years",
    "5_to_10_years",
    "over_10_years",
    "perpetual",
  ];

  const hasActiveFilters =
    query.trim().length > 0 ||
    issuerType !== "all" ||
    bondType !== "all" ||
    currency !== "all" ||
    couponType !== "all" ||
    maturityBucket !== "all";

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded p-3 mb-4 space-y-3">
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1">
          <Search
            className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)]"
            aria-hidden="true"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search by ISIN, CUSIP, security, or issuer..."
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] placeholder-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
        </div>

        {/* Filter Reset & Count */}
        <div className="flex items-center justify-between md:justify-end gap-2 text-xs">
          <span className="text-[var(--atlas-text-tertiary)] text-[11px] font-mono">
            {totalResults} {totalResults === 1 ? "security" : "securities"} matched
          </span>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={onResetFilters}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
              title="Reset all filters"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Dropdown Filters Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 pt-1 border-t border-[var(--atlas-border-subtle)]/50">
        {/* Issuer Category Filter */}
        <div>
          <label className="block text-[10px] uppercase font-mono tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Issuer Type
          </label>
          <select
            value={issuerType}
            onChange={(e) => onIssuerTypeChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Issuers</option>
            {issuerCategories.map((it) => (
              <option key={it} value={it}>
                {it.charAt(0).toUpperCase() + it.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Debt Type Filter */}
        <div>
          <label className="block text-[10px] uppercase font-mono tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Debt Type
          </label>
          <select
            value={bondType}
            onChange={(e) => onBondTypeChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Debt Types</option>
            {bondTypes.map((bt) => (
              <option key={bt} value={bt}>
                {bt === "treasury_bill"
                  ? "Treasury Bill"
                  : bt.charAt(0).toUpperCase() + bt.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Currency Filter */}
        <div>
          <label className="block text-[10px] uppercase font-mono tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Currency
          </label>
          <select
            value={currency}
            onChange={(e) => onCurrencyChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 font-mono"
          >
            <option value="all">All Currencies</option>
            {currencies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Coupon Type Filter */}
        <div>
          <label className="block text-[10px] uppercase font-mono tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Coupon Type
          </label>
          <select
            value={couponType}
            onChange={(e) => onCouponTypeChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Coupons</option>
            {couponTypes.map((ct) => (
              <option key={ct} value={ct}>
                {ct === "zero_coupon"
                  ? "Zero Coupon"
                  : ct.charAt(0).toUpperCase() + ct.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Maturity Range Filter */}
        <div>
          <label className="block text-[10px] uppercase font-mono tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Maturity
          </label>
          <select
            value={maturityBucket}
            onChange={(e) => onMaturityBucketChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Maturities</option>
            {maturityBuckets.map((mb) => {
              let label = mb;
              if (mb === "under_1_year") label = "< 1 Year";
              else if (mb === "1_to_3_years") label = "1–3 Years";
              else if (mb === "3_to_5_years") label = "3–5 Years";
              else if (mb === "5_to_10_years") label = "5–10 Years";
              else if (mb === "over_10_years") label = "> 10 Years";
              else if (mb === "perpetual") label = "Perpetual";
              return (
                <option key={mb} value={mb}>
                  {label}
                </option>
              );
            })}
          </select>
        </div>
      </div>
    </div>
  );
}
