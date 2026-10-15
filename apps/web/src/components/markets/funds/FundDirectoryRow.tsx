"use client";

import React from "react";
import {
  FundDirectoryItem,
  formatAUM,
  formatExpenseRatio,
  formatFundChange,
  formatFundNAV,
  formatFundPrice,
  formatValuationDate,
} from "@/lib/markets/funds";

export interface FundDirectoryRowProps {
  item: FundDirectoryItem;
  isSelected: boolean;
  onSelect: (instrumentEntityId: string) => void;
}

export function FundDirectoryRow({
  item,
  isSelected,
  onSelect,
}: FundDirectoryRowProps) {
  const isExchangeTraded = item.is_exchange_traded;
  const quote = item.market_quote;
  const nav = item.official_nav;

  // Format Market Last Price
  const marketPriceDisplay = isExchangeTraded
    ? quote?.last_price
      ? formatFundPrice(quote.last_price, item.trading_currency)
      : "—"
    : "Not Listed";

  // Format Price Change
  const priceChange = isExchangeTraded
    ? formatFundChange(quote?.percentage_change)
    : { text: "—", colorClass: "text-[var(--atlas-text-secondary)] font-mono" };

  // Format Official NAV
  const navDisplay = nav?.is_available && nav.nav_per_unit
    ? formatFundNAV(nav.nav_per_unit, nav.nav_currency || item.share_class_currency)
    : "NAV unavailable";

  const navDateDisplay = nav?.is_available && nav.valuation_date
    ? formatValuationDate(nav.valuation_date)
    : "—";

  // Expense Ratio
  const expenseRatioDisplay = item.fees?.is_available && item.fees.net_expense_ratio
    ? formatExpenseRatio(item.fees.net_expense_ratio, item.fees.fee_scale)
    : "—";

  // AUM
  const aumDisplay = item.aum?.is_available && item.aum.amount
    ? formatAUM(item.aum.amount, item.aum.currency)
    : "—";

  // Fund Type Badge Styling
  const getTypeBadgeClass = (fundType: string) => {
    switch (fundType) {
      case "ETF":
        return "bg-emerald-950/40 text-emerald-400 border-emerald-800/40";
      case "OPEN_END_MUTUAL_FUND":
        return "bg-blue-950/40 text-blue-400 border-blue-800/40";
      case "CLOSED_END_FUND":
        return "bg-purple-950/40 text-purple-400 border-purple-800/40";
      default:
        return "bg-zinc-800/40 text-zinc-400 border-zinc-700/40";
    }
  };

  // Freshness & Delivery Status Badge
  const getStatusBadge = () => {
    if (!isExchangeTraded) {
      return (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">
          NAV Valued
        </span>
      );
    }

    if (!quote || quote.data_status !== "available") {
      return (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-medium bg-zinc-900 text-zinc-500 border border-zinc-800">
          No Quote
        </span>
      );
    }

    if (quote.delivery_delay_status === "delayed") {
      return (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-medium bg-amber-950/40 text-amber-400 border border-amber-800/40">
          Delayed
        </span>
      );
    }

    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-medium bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
        Live
      </span>
    );
  };

  return (
    <tr
      tabIndex={0}
      role="row"
      aria-selected={isSelected}
      onClick={() => onSelect(item.instrument_entity_id)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(item.instrument_entity_id);
        }
      }}
      className={`group cursor-pointer text-xs transition-colors focus:outline-none focus:bg-zinc-800/60 ${
        isSelected
          ? "bg-zinc-800/80 border-l-2 border-emerald-400"
          : "hover:bg-[var(--atlas-surface-hover)]/40"
      }`}
    >
      {/* Fund Name & Category */}
      <td className="py-2.5 px-3 max-w-[220px]">
        <div className="font-medium text-[var(--atlas-text-primary)] truncate group-hover:text-emerald-400 transition-colors">
          {item.display_name}
        </div>
        <div className="text-[10px] text-[var(--atlas-text-tertiary)] truncate">
          {item.fund_category} · {item.domicile}
        </div>
      </td>

      {/* Fund Type */}
      <td className="py-2.5 px-3 whitespace-nowrap">
        <span
          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border ${getTypeBadgeClass(
            item.fund_type
          )}`}
        >
          {item.fund_type_label}
        </span>
      </td>

      {/* Ticker / Identifier */}
      <td className="py-2.5 px-3 font-mono font-medium text-[var(--atlas-text-primary)] whitespace-nowrap">
        {item.display_symbol}
      </td>

      {/* Exchange / Venue */}
      <td className="py-2.5 px-3 text-[var(--atlas-text-secondary)] whitespace-nowrap">
        {item.exchange_mic || (
          <span className="text-zinc-500 italic">Unlisted</span>
        )}
      </td>

      {/* Currency */}
      <td className="py-2.5 px-3 font-mono text-[11px] text-[var(--atlas-text-secondary)] whitespace-nowrap">
        {item.trading_currency || item.share_class_currency}
      </td>

      {/* Market Price (Trade) */}
      <td className="py-2.5 px-3 text-right font-mono font-medium text-[var(--atlas-text-primary)] whitespace-nowrap">
        {isExchangeTraded ? (
          marketPriceDisplay
        ) : (
          <span className="text-zinc-500 font-sans italic text-[11px]">Unlisted</span>
        )}
      </td>

      {/* Price Change % */}
      <td className={`py-2.5 px-3 text-right whitespace-nowrap ${priceChange.colorClass}`}>
        {priceChange.text}
      </td>

      {/* Official NAV */}
      <td className="py-2.5 px-3 text-right font-mono font-medium text-amber-400 whitespace-nowrap">
        {navDisplay}
      </td>

      {/* NAV As Of */}
      <td className="py-2.5 px-3 text-right text-[11px] text-[var(--atlas-text-secondary)] whitespace-nowrap">
        {navDateDisplay}
      </td>

      {/* Expense Ratio */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-secondary)] whitespace-nowrap">
        {expenseRatioDisplay}
      </td>

      {/* AUM */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-secondary)] whitespace-nowrap hidden lg:table-cell">
        {aumDisplay}
      </td>

      {/* Status */}
      <td className="py-2.5 px-3 text-center whitespace-nowrap">
        {getStatusBadge()}
      </td>
    </tr>
  );
}
