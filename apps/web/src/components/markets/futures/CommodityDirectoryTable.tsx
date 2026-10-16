"use client";

import React, { useState } from "react";
import { Layers, Search } from "lucide-react";
import { CommodityDirectoryItem, formatCommodityCategory } from "@/lib/markets/futures";

export interface CommodityDirectoryTableProps {
  commodities: CommodityDirectoryItem[];
  isLoading: boolean;
  category: string;
  onCategoryChange: (c: string) => void;
  query: string;
  onQueryChange: (q: string) => void;
}

export function CommodityDirectoryTable({
  commodities,
  isLoading,
  category,
  onCategoryChange,
  query,
  onQueryChange,
}: CommodityDirectoryTableProps) {
  const [selectedCommodity, setSelectedCommodity] =
    useState<CommodityDirectoryItem | null>(null);

  if (isLoading && commodities.length === 0) {
    return (
      <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] p-4 animate-pulse">
        <div className="h-6 bg-[var(--atlas-surface-subtle)] rounded w-1/4 mb-4" />
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-10 bg-[var(--atlas-surface-subtle)] rounded w-full" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search & Category Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)]">
        <div className="relative flex-1 max-w-md">
          <Search
            className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)]"
            aria-hidden="true"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search commodities by name or reference region..."
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded placeholder:text-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--atlas-text-secondary)]">Category:</span>
          <select
            value={category}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="px-2.5 py-1 text-xs bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Categories</option>
            <option value="energy">Energy</option>
            <option value="precious_metals">Precious Metals</option>
            <option value="industrial_metals">Industrial Metals</option>
            <option value="agriculture">Agriculture</option>
            <option value="livestock">Livestock</option>
            <option value="financial_index">Financial / Index</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] select-none">
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Commodity Name
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Category
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Physical Unit
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Reference Region / Pricing Hub
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
                  Grade Specification
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-center">
                  Products
                </th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-center">
                  Active Contracts
                </th>
              </tr>
            </thead>
            <tbody>
              {commodities.map((c) => (
                <tr
                  key={c.commodity_entity_id}
                  onClick={() => setSelectedCommodity(c)}
                  className={`cursor-pointer transition-colors border-b border-[var(--atlas-border-subtle)] ${
                    selectedCommodity?.commodity_entity_id === c.commodity_entity_id
                      ? "bg-emerald-950/20"
                      : "hover:bg-[var(--atlas-surface-hover)]"
                  }`}
                >
                  <td className="px-3 py-2.5 font-medium text-[var(--atlas-text-primary)]">
                    <div className="flex items-center gap-1.5">
                      <Layers className="h-3.5 w-3.5 text-emerald-400 shrink-0" aria-hidden="true" />
                      <span>{c.name}</span>
                    </div>
                    <div className="text-[10px] text-[var(--atlas-text-tertiary)] font-mono pl-5">
                      {c.slug}
                    </div>
                  </td>

                  <td className="px-3 py-2.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)]">
                      {formatCommodityCategory(c.category)}
                    </span>
                  </td>

                  <td className="px-3 py-2.5 font-mono text-[var(--atlas-text-primary)]">
                    {c.physical_unit}
                  </td>

                  <td className="px-3 py-2.5 text-[var(--atlas-text-secondary)] max-w-xs truncate" title={c.reference_region || ""}>
                    {c.reference_region || "—"}
                  </td>

                  <td className="px-3 py-2.5 text-[var(--atlas-text-tertiary)] max-w-xs truncate text-[11px]" title={c.grade_specification || ""}>
                    {c.grade_specification || "—"}
                  </td>

                  <td className="px-3 py-2.5 text-center font-mono">
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-[var(--atlas-surface-subtle)] text-[var(--atlas-text-primary)]">
                      {c.associated_products_count}
                    </span>
                  </td>

                  <td className="px-3 py-2.5 text-center font-mono">
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-950/40 text-emerald-300 border border-emerald-800/40">
                      {c.active_contracts_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-3 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] text-xs text-[var(--atlas-text-secondary)]">
          Total canonical underlyings: <span className="font-mono font-medium text-[var(--atlas-text-primary)]">{commodities.length}</span>
        </div>
      </div>
    </div>
  );
}
