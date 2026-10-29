"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  formatCurrency,
  formatDate,
  formatPnL,
  formatPrice,
  formatQuantity,
  getQuoteFreshnessBadge,
  getValuationStatusBadge,
} from "@/lib/portfolios/formatting";
import { PortfolioDTO, ValuationDTO } from "@/lib/portfolios/types";
import {
  AlertTriangle,
  Database,
  RefreshCw,
  Scale,
  ShieldCheck,
} from "lucide-react";

interface PortfolioValuationWorkspaceProps {
  portfolio: PortfolioDTO;
  valuation: ValuationDTO | null;
  onRecalculate: () => void;
}

export function PortfolioValuationWorkspace({
  portfolio,
  valuation,
  onRecalculate,
}: PortfolioValuationWorkspaceProps) {
  const baseCur = portfolio.base_currency;

  if (!valuation) {
    return (
      <div className="p-8 text-center text-xs text-atlas-text-muted">
        No valuation generated yet.
        <div className="mt-3">
          <Button variant="primary" size="sm" onClick={onRecalculate}>
            Compute Valuation Snapshot
          </Button>
        </div>
      </div>
    );
  }

  const isComplete = valuation.valuation_status === "COMPLETE";
  const badge = getValuationStatusBadge(valuation.valuation_status);

  return (
    <div className="space-y-4 p-4">
      {/* Top Banner: Valuation Status & Subtotal */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default pb-3">
          <div>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-atlas-accent" />
              <h2 className="text-base font-bold text-atlas-text-primary">
                Marked-to-Market Portfolio Valuation Snapshot
              </h2>
              <Badge variant={badge.variant}>{badge.label}</Badge>
            </div>
            <p className="mt-1 text-xs text-atlas-text-muted">
              Snapshot ID: <span className="font-mono">{valuation.id}</span> · As-of:{" "}
              <span className="font-mono">{formatDate(valuation.as_of)}</span> · Base Currency:{" "}
              <span className="font-mono font-bold text-atlas-text-primary">{baseCur}</span>
            </p>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={onRecalculate}
            className="h-8 gap-1.5 text-xs"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Recalculate Marks
          </Button>
        </div>

        {/* Completeness Explanation */}
        {!isComplete && (
          <div className="mt-3 flex items-start gap-2 rounded-xs border border-amber-500/30 bg-amber-500/10 p-2.5 text-xs text-amber-400">
            <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold">Incomplete Valuation Notice:</div>
              {valuation.missing_prices_count > 0 && (
                <div>
                  • {valuation.missing_prices_count} position(s) lack market quotes.
                </div>
              )}
              {valuation.missing_fx_count > 0 && (
                <div>• Foreign currency balances lack canonical FX conversion rates.</div>
              )}
              <div className="mt-1 text-[11px] text-amber-400/80">
                To guarantee institutional financial integrity, ATLAS does not extrapolate or publish a false total. Only the Known Valued Subtotal is verified.
              </div>
            </div>
          </div>
        )}

        {/* Valuation Numbers Grid */}
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6 font-mono">
          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Verified Total Value
            </div>
            <div className="mt-1 text-base font-bold text-atlas-text-primary">
              {valuation.verified_total_portfolio_value
                ? formatCurrency(valuation.verified_total_portfolio_value, baseCur)
                : "—"}
            </div>
          </div>

          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Known Valued Subtotal
            </div>
            <div className="mt-1 text-base font-bold text-atlas-text-primary">
              {formatCurrency(valuation.known_valued_subtotal, baseCur)}
            </div>
          </div>

          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Holdings Value ({baseCur})
            </div>
            <div className="mt-1 text-base font-bold text-atlas-text-primary">
              {valuation.total_positions_market_value
                ? formatCurrency(valuation.total_positions_market_value, baseCur)
                : "—"}
            </div>
          </div>

          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Cash Value ({baseCur})
            </div>
            <div className="mt-1 text-base font-bold text-atlas-text-primary">
              {formatCurrency(valuation.total_cash_market_value, baseCur)}
            </div>
          </div>

          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Total Cost Basis
            </div>
            <div className="mt-1 text-base font-bold text-atlas-text-secondary">
              {formatCurrency(valuation.total_cost_basis, baseCur)}
            </div>
          </div>

          <div className="rounded-xs bg-atlas-surface-1 p-2.5">
            <div className="text-[10px] text-atlas-text-muted font-sans">
              Unrealized P&L
            </div>
            <div
              className={`mt-1 text-base font-bold ${
                parseFloat(valuation.total_unrealized_pnl || "0") >= 0
                  ? "text-emerald-400"
                  : "text-rose-400"
              }`}
            >
              {valuation.total_unrealized_pnl
                ? formatPnL(valuation.total_unrealized_pnl, baseCur).text
                : "—"}
            </div>
          </div>
        </div>
      </div>

      {/* Position Marks Table */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
        <div className="flex items-center justify-between border-b border-atlas-border-default pb-2">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-atlas-accent" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Security Marks & Market Value Calculation
            </h3>
          </div>
          <span className="text-xs text-atlas-text-muted">
            {valuation.position_valuations.length} instrument(s) marked
          </span>
        </div>

        <div className="mt-2 overflow-x-auto">
          {valuation.position_valuations.length === 0 ? (
            <div className="py-6 text-center text-xs text-atlas-text-muted">
              No security positions to value.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-atlas-border-default text-[10px] font-semibold text-atlas-text-muted">
                  <th className="py-2 px-3 font-sans">Security</th>
                  <th className="py-2 px-3 text-right">Shares</th>
                  <th className="py-2 px-3 text-right">Mark Price</th>
                  <th className="py-2 px-3 font-sans text-center">Quote Freshness</th>
                  <th className="py-2 px-3 font-sans">Source Provenance</th>
                  <th className="py-2 px-3 text-right">FX Rate to {baseCur}</th>
                  <th className="py-2 px-3 text-right">Base Market Value</th>
                  <th className="py-2 px-3 text-right">Unrealized P&L</th>
                  <th className="py-2 px-3 font-sans text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30">
                {valuation.position_valuations.map((pv) => {
                  const freshnessBadge = getQuoteFreshnessBadge(pv.quote_freshness);
                  const statusBadge = getValuationStatusBadge(pv.valuation_status);
                  const pnlObj = pv.unrealized_pnl
                    ? formatPnL(pv.unrealized_pnl, baseCur)
                    : { text: "—", isPositive: false, isNegative: false };

                  return (
                    <tr key={pv.instrument_id} className="hover:bg-atlas-surface-1">
                      <td className="py-2.5 px-3 font-sans">
                        <div className="font-bold text-atlas-text-primary">{pv.symbol}</div>
                        <div className="text-[10px] text-atlas-text-muted">{pv.exchange}</div>
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-primary">
                        {formatQuantity(pv.quantity)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                        {pv.mark_price
                          ? formatPrice(pv.mark_price, pv.price_currency || baseCur)
                          : "—"}
                      </td>
                      <td className="py-2.5 px-3 text-center font-sans">
                        <Badge variant={freshnessBadge.variant} className="text-[9px]">
                          {freshnessBadge.label}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 font-sans text-[11px] text-atlas-text-muted">
                        {pv.mark_source || "CANONICAL_EXCHANGE"}
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                        {pv.fx_rate_to_base ? pv.fx_rate_to_base : "1.0000"}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                        {pv.base_market_value
                          ? formatCurrency(pv.base_market_value, baseCur)
                          : "—"}
                      </td>
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
                      <td className="py-2.5 px-3 text-center font-sans">
                        <Badge variant={statusBadge.variant} className="text-[9px]">
                          {statusBadge.label}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Source Manifest Box */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3 text-xs">
        <div className="flex items-center gap-2 border-b border-atlas-border-default pb-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <h3 className="font-bold uppercase tracking-wider text-atlas-text-primary">
            Market Data & Provenance Manifest
          </h3>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-4 text-atlas-text-muted font-mono text-[11px] sm:grid-cols-4">
          <div>
            <span className="font-sans text-atlas-text-secondary font-medium">Calculation Engine: </span>
            v{valuation.calculation_version}
          </div>
          <div>
            <span className="font-sans text-atlas-text-secondary font-medium">Quotes Resolved: </span>
            {valuation.position_valuations.filter((p) => p.mark_price !== null).length} of{" "}
            {valuation.position_valuations.length}
          </div>
          <div>
            <span className="font-sans text-atlas-text-secondary font-medium">FX Pairs Resolved: </span>
            {valuation.cash_valuations.length}
          </div>
          <div>
            <span className="font-sans text-atlas-text-secondary font-medium">Cost-Basis Policy: </span>
            FIFO Tax Lots
          </div>
        </div>
      </div>
    </div>
  );
}

