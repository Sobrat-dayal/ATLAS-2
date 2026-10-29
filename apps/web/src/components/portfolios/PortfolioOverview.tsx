"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  formatCurrency,
  formatDate,
  formatPnL,
  formatQuantity,
  getReconciliationBadge,
  getTransactionTypeBadge,
  getValuationStatusBadge,
} from "@/lib/portfolios/formatting";
import {
  CashBalanceDTO,
  PortfolioDTO,
  PositionDTO,
  ReconciliationDTO,
  TransactionDTO,
  ValuationDTO,
} from "@/lib/portfolios/types";
import {
  AlertTriangle,
  ArrowRight,
  Coins,
  DollarSign,
  TrendingUp,
  Wallet,
} from "lucide-react";

interface PortfolioOverviewProps {
  portfolio: PortfolioDTO;
  positions: PositionDTO[];
  cashBalances: CashBalanceDTO[];
  transactions: TransactionDTO[];
  valuation: ValuationDTO | null;
  reconciliation: ReconciliationDTO | null;
  onNavigateTab: (tab: "holdings" | "transactions" | "cash" | "valuation") => void;
  onSelectPosition: (pos: PositionDTO) => void;
}

export function PortfolioOverview({
  portfolio,
  positions,
  cashBalances,
  transactions,
  valuation,
  reconciliation,
  onNavigateTab,
  onSelectPosition,
}: PortfolioOverviewProps) {
  const baseCur = portfolio.base_currency;

  const totalValDisplay = valuation?.verified_total_portfolio_value
    ? formatCurrency(valuation.verified_total_portfolio_value, baseCur)
    : valuation?.known_valued_subtotal
    ? `${formatCurrency(valuation.known_valued_subtotal, baseCur)}*`
    : "—";

  const isPartial = valuation && valuation.valuation_status !== "COMPLETE";
  const realizedPnLObj = formatPnL(valuation?.total_realized_pnl, baseCur);
  const unrealizedPnLObj = formatPnL(valuation?.total_unrealized_pnl, baseCur);

  return (
    <div className="space-y-4 p-4">
      {/* Missing Data Warning Banner if partial */}
      {isPartial && (
        <div className="flex items-center justify-between rounded-sm border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-400">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
            <div>
              <span className="font-semibold">Partial Valuation Notice: </span>
              {valuation?.valuation_status === "PARTIAL_MISSING_PRICES" && (
                <span>
                  {valuation.missing_prices_count} security holding(s) lack eligible market quotes. A complete verified total is withheld to preserve accounting integrity.
                </span>
              )}
              {valuation?.valuation_status === "PARTIAL_MISSING_FX" && (
                <span>
                  Foreign currency cash or quotes lack a canonical FX conversion rate to {baseCur}.
                </span>
              )}
              {valuation?.valuation_status === "PARTIAL_STALE_DATA" && (
                <span>
                  Market quotes contain stale historical marks.
                </span>
              )}
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onNavigateTab("valuation")}
            className="h-7 text-[11px]"
          >
            Inspect Sources
          </Button>
        </div>
      )}

      {/* Institutional Top KPI Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {/* Total Value */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-atlas-text-secondary">
              Total Portfolio Value
            </span>
            <DollarSign className="h-4 w-4 text-atlas-text-muted" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-atlas-text-primary">
            {totalValDisplay}
          </div>
          <div className="mt-1 flex items-center gap-1.5">
            {valuation && (
              <Badge
                variant={getValuationStatusBadge(valuation.valuation_status).variant}
                className="text-[10px]"
              >
                {getValuationStatusBadge(valuation.valuation_status).label}
              </Badge>
            )}
            <span className="text-[11px] text-atlas-text-muted font-mono">
              {baseCur} Reporting
            </span>
          </div>
        </div>

        {/* Settled Cash */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-atlas-text-secondary">
              Total Cash
            </span>
            <Wallet className="h-4 w-4 text-atlas-text-muted" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-atlas-text-primary">
            {valuation
              ? formatCurrency(valuation.total_cash_market_value, baseCur)
              : "—"}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-muted">
            {cashBalances.length} currency balance(s)
          </div>
        </div>

        {/* Total Positions */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-atlas-text-secondary">
              Holdings Value
            </span>
            <Coins className="h-4 w-4 text-atlas-text-muted" />
          </div>
          <div className="mt-1 text-xl font-bold tracking-tight text-atlas-text-primary">
            {valuation?.total_positions_market_value
              ? formatCurrency(valuation.total_positions_market_value, baseCur)
              : "—"}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-muted">
            Cost Basis: {valuation ? formatCurrency(valuation.total_cost_basis, baseCur) : "—"}
          </div>
        </div>

        {/* Realized Accounting P&L */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-atlas-text-secondary">
              Realized Accounting P&L
            </span>
            <TrendingUp className="h-4 w-4 text-atlas-text-muted" />
          </div>
          <div
            className={`mt-1 text-xl font-bold tracking-tight ${
              realizedPnLObj.isPositive
                ? "text-emerald-400"
                : realizedPnLObj.isNegative
                ? "text-rose-400"
                : "text-atlas-text-primary"
            }`}
          >
            {realizedPnLObj.text}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-muted">
            From closed lots (FIFO)
          </div>
        </div>

        {/* Unrealized Accounting P&L */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-atlas-text-secondary">
              Unrealized Accounting P&L
            </span>
            <TrendingUp className="h-4 w-4 text-atlas-text-muted" />
          </div>
          <div
            className={`mt-1 text-xl font-bold tracking-tight ${
              unrealizedPnLObj.isPositive
                ? "text-emerald-400"
                : unrealizedPnLObj.isNegative
                ? "text-rose-400"
                : "text-atlas-text-primary"
            }`}
          >
            {unrealizedPnLObj.text}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-muted">
            Marked to market
          </div>
        </div>
      </div>

      {/* Two Columns: Holdings & Recent Activity */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Holdings Table (2 Cols) */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-atlas-border-default pb-2">
            <div>
              <h3 className="text-xs font-bold tracking-wide uppercase text-atlas-text-primary">
                Current Security Holdings
              </h3>
              <p className="text-[11px] text-atlas-text-muted">
                Derived deterministically from posted transaction ledger
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onNavigateTab("holdings")}
              className="h-7 gap-1 text-[11px] text-atlas-accent"
            >
              View All ({positions.length})
              <ArrowRight className="h-3 w-3" />
            </Button>
          </div>

          <div className="mt-2 overflow-x-auto">
            {positions.length === 0 ? (
              <div className="py-8 text-center text-xs text-atlas-text-muted">
                No open security holdings in this portfolio.
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-atlas-border-default text-[11px] font-semibold text-atlas-text-muted">
                    <th className="py-2 pr-3">Security</th>
                    <th className="py-2 px-3 text-right">Shares</th>
                    <th className="py-2 px-3 text-right">Avg Basis</th>
                    <th className="py-2 px-3 text-right">Market Price</th>
                    <th className="py-2 px-3 text-right">Market Value</th>
                    <th className="py-2 pl-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-atlas-border-default/50 font-mono">
                  {positions.slice(0, 5).map((pos) => {
                    const posVal = valuation?.position_valuations.find(
                      (v) => v.instrument_id === pos.instrument_id
                    );
                    return (
                      <tr
                        key={pos.instrument_id}
                        className="hover:bg-atlas-surface-1/60 transition-colors"
                      >
                        <td className="py-2.5 pr-3 font-sans">
                          <div className="font-bold text-atlas-text-primary">
                            {pos.symbol}
                          </div>
                          <div className="text-[10px] text-atlas-text-muted">
                            {pos.exchange} · {pos.open_lot_count} lot(s)
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-right font-medium">
                          {formatQuantity(pos.quantity)}
                        </td>
                        <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                          {formatCurrency(pos.average_unit_cost, pos.cost_basis_currency)}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          {posVal?.mark_price ? (
                            <span className="text-atlas-text-primary">
                              {formatCurrency(posVal.mark_price, posVal.price_currency || baseCur)}
                            </span>
                          ) : (
                            <span className="text-atlas-text-muted italic">Unpriced</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                          {posVal?.base_market_value
                            ? formatCurrency(posVal.base_market_value, baseCur)
                            : "—"}
                        </td>
                        <td className="py-2.5 pl-3 text-right font-sans">
                          <button
                            onClick={() => onSelectPosition(pos)}
                            className="rounded-xs px-2 py-0.5 text-[11px] font-medium text-atlas-accent hover:underline"
                          >
                            Inspect Lots
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Ledger Integrity & Audit (1 Col) */}
        <div className="space-y-4">
          <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
            <h3 className="text-xs font-bold tracking-wide uppercase text-atlas-text-primary">
              Ledger Reconciliation
            </h3>
            <div className="mt-2 space-y-2 text-xs">
              <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-1.5">
                <span className="text-atlas-text-secondary">Audit Status</span>
                {reconciliation && (
                  <Badge variant={getReconciliationBadge(reconciliation.status).variant}>
                    {getReconciliationBadge(reconciliation.status).label}
                  </Badge>
                )}
              </div>
              <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-1.5">
                <span className="text-atlas-text-secondary">Transactions Checked</span>
                <span className="font-mono text-atlas-text-primary">
                  {reconciliation?.total_transactions_checked || 0}
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-1.5">
                <span className="text-atlas-text-secondary">Open Tax Lots Checked</span>
                <span className="font-mono text-atlas-text-primary">
                  {reconciliation?.total_lots_checked || 0}
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-1.5">
                <span className="text-atlas-text-secondary">Cost Basis Accounting</span>
                <span className="font-mono text-atlas-text-primary">
                  {portfolio.cost_basis_method}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-atlas-text-secondary">Last As-of Valuation</span>
                <span className="font-mono text-[11px] text-atlas-text-muted">
                  {formatDate(valuation?.as_of)}
                </span>
              </div>
            </div>
          </div>

          {/* Recent Activity Mini-Journal */}
          <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
            <div className="flex items-center justify-between border-b border-atlas-border-default pb-2">
              <h3 className="text-xs font-bold tracking-wide uppercase text-atlas-text-primary">
                Recent Journal
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigateTab("transactions")}
                className="h-6 text-[11px] text-atlas-accent"
              >
                Journal
              </Button>
            </div>
            <div className="mt-2 space-y-2">
              {transactions.length === 0 ? (
                <div className="py-4 text-center text-xs text-atlas-text-muted">
                  No posted transactions yet.
                </div>
              ) : (
                transactions.slice(0, 4).map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between border-b border-atlas-border-default/30 pb-1.5 text-xs font-mono"
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <Badge
                          variant={getTransactionTypeBadge(tx.transaction_type).variant}
                          className="text-[9px] px-1 py-0 font-sans"
                        >
                          {getTransactionTypeBadge(tx.transaction_type).label}
                        </Badge>
                        <span className="font-sans font-medium text-atlas-text-primary">
                          {tx.symbol || tx.transaction_type}
                        </span>
                      </div>
                      <div className="text-[10px] text-atlas-text-muted font-sans">
                        {formatDate(tx.trade_date)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div
                        className={`font-semibold ${
                          parseFloat(tx.net_cash_amount) >= 0
                            ? "text-emerald-400"
                            : "text-rose-400"
                        }`}
                      >
                        {formatCurrency(tx.net_cash_amount, tx.cash_currency)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

