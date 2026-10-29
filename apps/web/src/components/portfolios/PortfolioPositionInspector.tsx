"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  formatCurrency,
  formatDate,
  formatPnL,
  formatPrice,
  formatQuantity,
} from "@/lib/portfolios/formatting";
import { LotDTO, PositionDTO, ValuationDTO } from "@/lib/portfolios/types";
import { Layers, X } from "lucide-react";

interface PortfolioPositionInspectorProps {
  position: PositionDTO | null;
  lots: LotDTO[];
  valuation: ValuationDTO | null;
  baseCurrency: string;
  onClose: () => void;
}

export function PortfolioPositionInspector({
  position,
  lots,
  valuation,
  baseCurrency,
  onClose,
}: PortfolioPositionInspectorProps) {
  if (!position) return null;

  const posVal = valuation?.position_valuations.find(
    (v) => v.instrument_id === position.instrument_id
  );
  const pnlObj = posVal?.unrealized_pnl
    ? formatPnL(posVal.unrealized_pnl, baseCurrency)
    : { text: "—", isPositive: false, isNegative: false };

  return (
    <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-atlas-accent" />
          <h2 className="text-sm font-bold text-atlas-text-primary">
            {position.symbol} — Holding Inspector & Tax Lots
          </h2>
          <Badge variant="outline" className="font-mono text-[10px]">
            {position.exchange}
          </Badge>
          <span className="text-xs text-atlas-text-muted font-mono">
            ID: {position.instrument_id}
          </span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-7 w-7 p-0 text-atlas-text-secondary hover:text-atlas-text-primary"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Metrics Row */}
      <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6 border-b border-atlas-border-default/50 pb-3">
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Total Shares</div>
          <div className="font-mono text-sm font-bold text-atlas-text-primary">
            {formatQuantity(position.quantity)}
          </div>
        </div>
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Average Unit Cost</div>
          <div className="font-mono text-sm font-bold text-atlas-text-primary">
            {position.average_unit_cost
              ? formatPrice(position.average_unit_cost, position.cost_basis_currency)
              : "—"}
          </div>
        </div>
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Remaining Cost Basis</div>
          <div className="font-mono text-sm font-bold text-atlas-text-primary">
            {formatCurrency(position.remaining_cost_basis, position.cost_basis_currency)}
          </div>
        </div>
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Market Price ({baseCurrency})</div>
          <div className="font-mono text-sm font-bold text-atlas-text-primary">
            {posVal?.mark_price ? formatPrice(posVal.mark_price, posVal.price_currency || baseCurrency) : "Unpriced"}
          </div>
        </div>
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Market Value</div>
          <div className="font-mono text-sm font-bold text-atlas-text-primary">
            {posVal?.base_market_value ? formatCurrency(posVal.base_market_value, baseCurrency) : "—"}
          </div>
        </div>
        <div className="rounded-xs bg-atlas-surface-1 p-2">
          <div className="text-[10px] text-atlas-text-muted">Unrealized P&L</div>
          <div
            className={`font-mono text-sm font-bold ${
              pnlObj.isPositive
                ? "text-emerald-400"
                : pnlObj.isNegative
                ? "text-rose-400"
                : "text-atlas-text-muted"
            }`}
          >
            {pnlObj.text}
          </div>
        </div>
      </div>

      {/* FIFO Tax Lots Table */}
      <div className="mt-3">
        <div className="flex items-center justify-between pb-2">
          <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
            Open FIFO Tax Lots ({lots.length})
          </h3>
          <span className="text-[11px] text-atlas-text-muted">
            Acquisitions ordered chronologically for FIFO consumption
          </span>
        </div>

        <div className="overflow-x-auto rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1">
          {lots.length === 0 ? (
            <div className="py-6 text-center text-xs text-atlas-text-muted">
              No open tax lots recorded for this position.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/40 text-[10px] font-semibold text-atlas-text-muted">
                  <th className="py-2 px-3">Lot ID</th>
                  <th className="py-2 px-3">Acquisition Date</th>
                  <th className="py-2 px-3 text-right">Original Qty</th>
                  <th className="py-2 px-3 text-right">Remaining Qty</th>
                  <th className="py-2 px-3 text-right">Unit Basis</th>
                  <th className="py-2 px-3 text-right">Total Basis</th>
                  <th className="py-2 px-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30">
                {lots.map((lot) => {
                  const isPartiallyConsumed =
                    parseFloat(lot.remaining_quantity) < parseFloat(lot.original_quantity);

                  return (
                    <tr key={lot.id} className="hover:bg-atlas-surface-2/30">
                      <td className="py-2 px-3 text-atlas-text-secondary">
                        {lot.id}
                      </td>
                      <td className="py-2 px-3 text-atlas-text-muted font-sans">
                        {formatDate(lot.acquisition_date)}
                      </td>
                      <td className="py-2 px-3 text-right text-atlas-text-secondary">
                        {formatQuantity(lot.original_quantity)}
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-atlas-text-primary">
                        {formatQuantity(lot.remaining_quantity)}
                      </td>
                      <td className="py-2 px-3 text-right text-atlas-text-secondary">
                        {formatPrice(lot.unit_cost_basis, lot.currency)}
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-atlas-text-primary">
                        {formatCurrency(lot.total_cost_basis, lot.currency)}
                      </td>
                      <td className="py-2 px-3 text-center font-sans">
                        {lot.is_fully_disposed ? (
                          <Badge variant="default" className="text-[9px]">
                            Disposed
                          </Badge>
                        ) : isPartiallyConsumed ? (
                          <Badge variant="warning" className="text-[9px]">
                            Partial
                          </Badge>
                        ) : (
                          <Badge variant="positive" className="text-[9px]">
                            Open
                          </Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
