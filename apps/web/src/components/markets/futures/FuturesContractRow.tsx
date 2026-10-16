"use client";

import React from "react";
import {
  FuturesContractDirectoryItem,
  formatContractMonth,
  formatDate,
  formatFuturesPrice,
  formatOpenInterest,
  formatPriceChange,
  formatPriceChangeClass,
  formatSettlementType,
  formatVolume,
  getFreshnessBadgeClass,
} from "@/lib/markets/futures";

export interface FuturesContractRowProps {
  contract: FuturesContractDirectoryItem;
  isSelected: boolean;
  onSelect: (instrumentEntityId: string) => void;
}

export function FuturesContractRow({
  contract,
  isSelected,
  onSelect,
}: FuturesContractRowProps) {
  const settlementBadge = formatSettlementType(contract.settlement_type);

  const priceFormatted = formatFuturesPrice(
    contract.price_observation.last,
    contract.quote_unit,
    contract.quote_currency
  );

  const settleFormatted = formatFuturesPrice(
    contract.settlement_observation.settlement_price,
    contract.quote_unit,
    contract.quote_currency
  );

  const changeFormatted = formatPriceChange(
    contract.price_change.change_absolute,
    contract.price_change.change_percent,
    contract.quote_unit
  );

  const changeClass = formatPriceChangeClass(
    contract.price_change.change_absolute
  );

  const isExpired = contract.lifecycle_status === "expired";

  return (
    <tr
      onClick={() => onSelect(contract.instrument_entity_id)}
      className={`cursor-pointer transition-colors border-b border-[var(--atlas-border-subtle)] text-xs select-none ${
        isSelected
          ? "bg-emerald-950/20 hover:bg-emerald-950/30"
          : isExpired
          ? "opacity-75 hover:bg-[var(--atlas-surface-hover)]/40"
          : "hover:bg-[var(--atlas-surface-hover)]"
      }`}
    >
      {/* Symbol & Product */}
      <td className="px-3 py-2.5 font-mono">
        <div className="flex items-center gap-1.5">
          <span className="font-bold text-[var(--atlas-text-primary)]">
            {contract.symbol}
          </span>
          {isExpired && (
            <span className="px-1 py-0.2 rounded text-[9px] font-sans font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">
              EXP
            </span>
          )}
        </div>
        <div className="text-[10px] text-[var(--atlas-text-tertiary)] truncate max-w-[140px]">
          {contract.name}
        </div>
      </td>

      {/* Underlying Commodity */}
      <td className="px-3 py-2.5">
        <div className="text-[var(--atlas-text-primary)] font-medium truncate max-w-[150px]">
          {contract.underlying_name}
        </div>
        <div className="text-[10px] text-[var(--atlas-text-secondary)] font-mono">
          {contract.quote_unit}
        </div>
      </td>

      {/* Exchange Venue */}
      <td className="px-3 py-2.5 font-mono text-[var(--atlas-text-secondary)] whitespace-nowrap">
        <span className="px-1.5 py-0.5 rounded bg-[var(--atlas-surface-subtle)] border border-[var(--atlas-border-subtle)] text-[10px] text-[var(--atlas-text-primary)]">
          {contract.exchange}
        </span>
      </td>

      {/* Contract Month */}
      <td className="px-3 py-2.5 font-mono text-[var(--atlas-text-primary)] whitespace-nowrap">
        {formatContractMonth(contract.contract_month)}
      </td>

      {/* Expiration Date */}
      <td className="px-3 py-2.5 text-[var(--atlas-text-secondary)] font-mono whitespace-nowrap">
        {formatDate(contract.expiration_date)}
      </td>

      {/* Last Executed Trade Price */}
      <td className="px-3 py-2.5 font-mono font-semibold text-right whitespace-nowrap">
        <span className={contract.price_observation.last ? "text-[var(--atlas-text-primary)]" : "text-[var(--atlas-text-tertiary)]"}>
          {priceFormatted}
        </span>
      </td>

      {/* Official Settlement Price */}
      <td className="px-3 py-2.5 font-mono text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
        {settleFormatted}
      </td>

      {/* Qualified Price Change */}
      <td className={`px-3 py-2.5 font-mono text-right whitespace-nowrap font-medium ${changeClass}`}>
        {changeFormatted}
      </td>

      {/* Session Volume */}
      <td className="px-3 py-2.5 font-mono text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
        {formatVolume(contract.volume_open_interest.volume)}
      </td>

      {/* Open Interest */}
      <td className="px-3 py-2.5 font-mono text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
        {formatOpenInterest(contract.volume_open_interest.open_interest)}
      </td>

      {/* Settlement Method */}
      <td className="px-3 py-2.5 text-center whitespace-nowrap">
        <span
          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium border ${settlementBadge.badgeClass}`}
        >
          {settlementBadge.label}
        </span>
      </td>

      {/* Freshness Status */}
      <td className="px-3 py-2.5 text-center whitespace-nowrap">
        <span
          className={`inline-block px-1.5 py-0.5 rounded text-[9px] font-mono uppercase tracking-wider border ${getFreshnessBadgeClass(
            contract.price_observation.freshness_status
          )}`}
        >
          {contract.price_observation.freshness_status}
        </span>
      </td>
    </tr>
  );
}
