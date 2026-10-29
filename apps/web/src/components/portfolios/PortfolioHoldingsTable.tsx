"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  formatCurrency,
  formatPnL,
  formatPrice,
  formatQuantity,
  getQuoteFreshnessBadge,
  getValuationStatusBadge,
} from "@/lib/portfolios/formatting";
import {
  AccountDTO,
  PortfolioDTO,
  PositionDTO,
  ValuationDTO,
} from "@/lib/portfolios/types";
import { Search } from "lucide-react";

interface PortfolioHoldingsTableProps {
  portfolio: PortfolioDTO;
  positions: PositionDTO[];
  accounts: AccountDTO[];
  valuation: ValuationDTO | null;
  onSelectPosition: (pos: PositionDTO) => void;
}

export function PortfolioHoldingsTable({
  portfolio,
  positions,
  accounts,
  valuation,
  onSelectPosition,
}: PortfolioHoldingsTableProps) {
  const [search, setSearch] = useState("");
  const baseCur = portfolio.base_currency;

  const filtered = positions.filter((p) => {
    const q = search.toLowerCase().trim();
    if (!q) return true;
    return (
      p.symbol.toLowerCase().includes(q) ||
      p.exchange.toLowerCase().includes(q) ||
      (p.company_name && p.company_name.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-3 p-4">
      {/* Top Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default pb-3">
        <div className="flex items-center gap-2">
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search symbol, exchange..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 pl-8 pr-2.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-none"
            />
          </div>
          <span className="text-xs text-atlas-text-muted">
            Showing {filtered.length} of {positions.length} holdings
          </span>
        </div>
      </div>

      {/* Dense Bloomberg-Style Holdings Table */}
      <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-0">
        {filtered.length === 0 ? (
          <div className="py-12 text-center text-xs text-atlas-text-muted">
            {search ? "No holdings matching search criteria." : "No holdings in this portfolio yet."}
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default bg-atlas-surface-1/70 text-[11px] font-semibold text-atlas-text-muted">
                <th className="py-2.5 px-3">Security</th>
                <th className="py-2.5 px-3">Exchange</th>
                <th className="py-2.5 px-3 text-right">Shares</th>
                <th className="py-2.5 px-3 text-right">Avg Unit Basis</th>
                <th className="py-2.5 px-3 text-right">Total Cost Basis</th>
                <th className="py-2.5 px-3 text-right">Mark Price</th>
                <th className="py-2.5 px-3 text-center">Freshness</th>
                <th className="py-2.5 px-3 text-right">Market Value ({baseCur})</th>
                <th className="py-2.5 px-3 text-right">Unrealized P&L</th>
                <th className="py-2.5 px-3 text-center">Valuation Status</th>
                <th className="py-2.5 pr-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40 font-mono">
              {filtered.map((pos) => {
                const posVal = valuation?.position_valuations.find(
                  (v) => v.instrument_id === pos.instrument_id
                );
                const pnlObj = posVal?.unrealized_pnl
                  ? formatPnL(posVal.unrealized_pnl, baseCur)
                  : { text: "—", isPositive: false, isNegative: false };

                const freshnessBadge = posVal?.quote_freshness
                  ? getQuoteFreshnessBadge(posVal.quote_freshness)
                  : null;

                const valStatusBadge = posVal?.valuation_status
                  ? getValuationStatusBadge(posVal.valuation_status)
                  : null;

                const acc = accounts.find((a) => a.id === pos.account_id);

                return (
                  <tr
                    key={pos.instrument_id + (pos.account_id || "")}
                    className="hover:bg-atlas-surface-1 transition-colors"
                  >
                    {/* Security */}
                    <td className="py-2.5 px-3 font-sans">
                      <div className="font-bold text-atlas-text-primary">
                        {pos.symbol}
                      </div>
                      <div className="text-[10px] text-atlas-text-muted">
                        {pos.company_name || pos.instrument_id}
                        {acc ? ` · ${acc.account_name}` : ""}
                      </div>
                    </td>

                    {/* Exchange */}
                    <td className="py-2.5 px-3 text-[11px] text-atlas-text-secondary font-sans">
                      {pos.exchange}
                    </td>

                    {/* Quantity */}
                    <td className="py-2.5 px-3 text-right font-medium text-atlas-text-primary">
                      {formatQuantity(pos.quantity)}
                    </td>

                    {/* Avg Cost */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                      {pos.average_unit_cost
                        ? formatPrice(pos.average_unit_cost, pos.cost_basis_currency)
                        : "—"}
                    </td>

                    {/* Total Basis */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                      {formatCurrency(pos.remaining_cost_basis, pos.cost_basis_currency)}
                    </td>

                    {/* Mark Price */}
                    <td className="py-2.5 px-3 text-right">
                      {posVal?.mark_price ? (
                        <div className="text-atlas-text-primary font-bold">
                          {formatPrice(posVal.mark_price, posVal.price_currency || baseCur)}
                        </div>
                      ) : (
                        <span className="italic text-atlas-text-muted">Unpriced</span>
                      )}
                    </td>

                    {/* Freshness */}
                    <td className="py-2.5 px-3 text-center font-sans">
                      {freshnessBadge && (
                        <Badge variant={freshnessBadge.variant} className="text-[9px] px-1 py-0">
                          {freshnessBadge.label}
                        </Badge>
                      )}
                    </td>

                    {/* Base Market Value */}
                    <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                      {posVal?.base_market_value
                        ? formatCurrency(posVal.base_market_value, baseCur)
                        : "—"}
                    </td>

                    {/* Unrealized P&L */}
                    <td
                      className={`py-2.5 px-3 text-right font-semibold ${
                        pnlObj.isPositive
                          ? "text-emerald-400"
                          : pnlObj.isNegative
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {pnlObj.text}
                    </td>

                    {/* Valuation Status */}
                    <td className="py-2.5 px-3 text-center font-sans">
                      {valStatusBadge && (
                        <Badge variant={valStatusBadge.variant} className="text-[9px] px-1 py-0">
                          {valStatusBadge.label}
                        </Badge>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-2.5 pr-3 text-right font-sans">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => onSelectPosition(pos)}
                        className="h-6 text-[10px]"
                      >
                        Inspect Lots
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

