"use client";

import React from "react";
import { ChevronRight } from "lucide-react";
import {
  BondDirectoryItem,
  formatBondCoupon,
  formatBondMaturity,
  formatBondPrice,
  formatBondType,
  formatBondYield,
  formatPriceBasis,
  formatTimeToMaturity,
  formatYieldChangeBps,
  formatYieldTypeLabel,
  getDirectionColorClass,
  getFreshnessBadgeClass,
} from "@/lib/markets/bonds";

export interface BondDirectoryRowProps {
  item: BondDirectoryItem;
  isSelected: boolean;
  onSelect: (item: BondDirectoryItem) => void;
}

export function BondDirectoryRow({
  item,
  isSelected,
  onSelect,
}: BondDirectoryRowProps) {
  const isSovereign =
    item.bond_type === "sovereign" || item.bond_type === "treasury_bill";

  return (
    <tr
      onClick={() => onSelect(item)}
      className={`border-b border-[var(--atlas-border-subtle)] text-xs cursor-pointer transition-colors ${
        isSelected
          ? "bg-emerald-500/10 hover:bg-emerald-500/15"
          : "hover:bg-[var(--atlas-surface-hover)]"
      }`}
    >
      {/* Security Symbol & ISIN */}
      <td className="py-2.5 px-3">
        <div className="flex flex-col">
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {item.symbol}
          </span>
          <span className="text-[11px] text-[var(--atlas-text-tertiary)] font-mono">
            {item.isin || item.cusip || "—"}
          </span>
        </div>
      </td>

      {/* Security Name & Issuer */}
      <td className="py-2.5 px-3 max-w-[220px]">
        <div className="flex flex-col">
          <span className="font-medium text-[var(--atlas-text-primary)] truncate" title={item.name}>
            {item.name}
          </span>
          <span className="text-[11px] text-[var(--atlas-text-secondary)] truncate" title={item.issuer.name}>
            {item.issuer.name}
          </span>
        </div>
      </td>

      {/* Bond Type Badge */}
      <td className="py-2.5 px-3 whitespace-nowrap">
        <span
          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${
            isSovereign
              ? "bg-blue-500/10 text-blue-400 border-blue-500/30"
              : item.bond_type === "corporate"
              ? "bg-purple-500/10 text-purple-400 border-purple-500/30"
              : "bg-teal-500/10 text-teal-400 border-teal-500/30"
          }`}
        >
          {formatBondType(item.bond_type)}
        </span>
      </td>

      {/* Currency */}
      <td className="py-2.5 px-3 font-mono font-medium text-[var(--atlas-text-secondary)]">
        {item.currency}
      </td>

      {/* Coupon Rate */}
      <td className="py-2.5 px-3 whitespace-nowrap">
        <div className="flex flex-col">
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatBondCoupon(item.terms.coupon_rate, item.terms.coupon_type)}
          </span>
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] capitalize">
            {item.terms.coupon_frequency.toLowerCase()}
          </span>
        </div>
      </td>

      {/* Maturity */}
      <td className="py-2.5 px-3 whitespace-nowrap">
        <div className="flex flex-col">
          <span className="font-mono text-[var(--atlas-text-primary)]">
            {formatBondMaturity(item.terms.maturity_date, item.terms.is_perpetual)}
          </span>
          {!item.terms.is_perpetual && item.terms.time_to_maturity_years && (
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] font-mono">
              {formatTimeToMaturity(item.terms.time_to_maturity_years)}
            </span>
          )}
        </div>
      </td>

      {/* Clean / Dirty Price */}
      <td className="py-2.5 px-3 text-right whitespace-nowrap">
        <div className="flex flex-col items-end">
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {formatBondPrice(item.price.clean_price, item.price.quote_unit)}
          </span>
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] font-mono">
            {formatPriceBasis(item.price.price_basis)}
          </span>
        </div>
      </td>

      {/* Yield & Basis Points Change */}
      <td className="py-2.5 px-3 text-right whitespace-nowrap">
        <div className="flex flex-col items-end">
          <span className="font-mono font-medium text-cyan-400">
            {formatBondYield(item.yield_obs.yield_value, item.yield_obs.yield_type)}
          </span>
          <div className="flex items-center gap-1 text-[10px] font-mono">
            <span className="text-[var(--atlas-text-tertiary)]">
              {formatYieldTypeLabel(item.yield_obs.yield_type)}:
            </span>
            <span className={getDirectionColorClass(item.yield_obs.yield_change_bps_24h)}>
              {formatYieldChangeBps(item.yield_obs.yield_change_bps_24h)}
            </span>
          </div>
        </div>
      </td>

      {/* Freshness Badge */}
      <td className="py-2.5 px-3 text-center whitespace-nowrap">
        <span
          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono border ${getFreshnessBadgeClass(
            item.freshness_status
          )}`}
        >
          {item.freshness_status}
        </span>
      </td>

      {/* Action / Inspect icon */}
      <td className="py-2.5 px-2 text-right">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(item);
          }}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-emerald-400 hover:bg-[var(--atlas-surface-subtle)] transition-colors"
          title="Inspect security"
        >
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </button>
      </td>
    </tr>
  );
}
