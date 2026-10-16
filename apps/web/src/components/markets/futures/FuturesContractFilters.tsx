"use client";

import React from "react";
import { RotateCcw, Search } from "lucide-react";
import { FuturesFilterOptionsResponse } from "@/lib/markets/futures";

export interface FuturesContractFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  category: string;
  onCategoryChange: (c: string) => void;
  exchange: string;
  onExchangeChange: (e: string) => void;
  productEntityId: string;
  onProductEntityIdChange: (p: string) => void;
  contractMonth: string;
  onContractMonthChange: (cm: string) => void;
  settlementType: string;
  onSettlementTypeChange: (st: string) => void;
  lifecycleStatus: string;
  onLifecycleStatusChange: (ls: string) => void;
  onReset: () => void;
  filterOptions?: FuturesFilterOptionsResponse | null;
  totalMatches: number;
}

export function FuturesContractFilters({
  query,
  onQueryChange,
  category,
  onCategoryChange,
  exchange,
  onExchangeChange,
  productEntityId,
  onProductEntityIdChange,
  contractMonth,
  onContractMonthChange,
  settlementType,
  onSettlementTypeChange,
  lifecycleStatus,
  onLifecycleStatusChange,
  onReset,
  filterOptions,
  totalMatches,
}: FuturesContractFiltersProps) {
  const isFiltered =
    query.trim() !== "" ||
    category !== "all" ||
    exchange !== "all" ||
    productEntityId !== "all" ||
    contractMonth !== "all" ||
    settlementType !== "all" ||
    lifecycleStatus !== "all";

  const categories = filterOptions?.categories || [
    "energy",
    "precious_metals",
    "industrial_metals",
    "agriculture",
    "livestock",
    "financial_index",
  ];

  const exchanges = filterOptions?.exchanges || ["NYMEX", "COMEX", "CBOT", "CME", "ICE"];
  const products = filterOptions?.products || [];
  const months = filterOptions?.months || [];

  return (
    <div className="p-3 mb-4 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-3">
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search
            className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)]"
            aria-hidden="true"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search symbol, product (CL, GC, ES), commodity, or venue..."
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded placeholder:text-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            aria-label="Search futures contracts"
          />
        </div>

        {/* Matches counter and Reset */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-[var(--atlas-text-secondary)] font-mono">
            {totalMatches} {totalMatches === 1 ? "contract" : "contracts"}
          </span>
          {isFiltered && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-subtle)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Select Dropdowns */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {/* Category */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Exchange */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Exchange
          </label>
          <select
            value={exchange}
            onChange={(e) => onExchangeChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Venues</option>
            {exchanges.map((ex) => (
              <option key={ex} value={ex}>
                {ex}
              </option>
            ))}
          </select>
        </div>

        {/* Product */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Product Family
          </label>
          <select
            value={productEntityId}
            onChange={(e) => onProductEntityIdChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Products</option>
            {products.map((p) => (
              <option key={p.product_entity_id} value={p.product_entity_id}>
                {p.root_symbol} ({p.name})
              </option>
            ))}
          </select>
        </div>

        {/* Contract Month */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Contract Month
          </label>
          <select
            value={contractMonth}
            onChange={(e) => onContractMonthChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 font-mono"
          >
            <option value="all">All Months</option>
            {months.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>

        {/* Settlement Type */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Settlement Method
          </label>
          <select
            value={settlementType}
            onChange={(e) => onSettlementTypeChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Methods</option>
            <option value="physical">Physical Delivery</option>
            <option value="cash">Cash Settled</option>
          </select>
        </div>

        {/* Lifecycle Status */}
        <div>
          <label className="block text-[10px] font-medium uppercase tracking-wider text-[var(--atlas-text-tertiary)] mb-1">
            Listing Status
          </label>
          <select
            value={lifecycleStatus}
            onChange={(e) => onLifecycleStatusChange(e.target.value)}
            className="w-full px-2 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active Only</option>
            <option value="expired">Expired Only</option>
          </select>
        </div>
      </div>
    </div>
  );
}
