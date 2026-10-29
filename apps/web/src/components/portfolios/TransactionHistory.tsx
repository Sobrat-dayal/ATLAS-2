"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  formatCurrency,
  formatDate,
  formatPrice,
  formatQuantity,
  getTransactionTypeBadge,
} from "@/lib/portfolios/formatting";
import {
  AccountDTO,
  TransactionDTO,
} from "@/lib/portfolios/types";
import { Edit2, RotateCcw, Search } from "lucide-react";

interface TransactionHistoryProps {
  transactions: TransactionDTO[];
  accounts: AccountDTO[];
  onReverse: (tx: TransactionDTO) => void;
  onCorrect: (tx: TransactionDTO) => void;
}

export function TransactionHistory({
  transactions,
  accounts,
  onReverse,
  onCorrect,
}: TransactionHistoryProps) {
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<string>("ALL");

  const filtered = transactions.filter((t) => {
    if (filterType !== "ALL" && t.transaction_type !== filterType) return false;
    const q = search.toLowerCase().trim();
    if (!q) return true;
    return (
      (t.symbol && t.symbol.toLowerCase().includes(q)) ||
      (t.notes && t.notes.toLowerCase().includes(q)) ||
      t.id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-3 p-4">
      {/* Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default pb-3">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search */}
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search symbol, notes, ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 pl-8 pr-2.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-none"
            />
          </div>

          {/* Type Filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-secondary focus:border-atlas-accent focus:outline-none"
          >
            <option value="ALL">All Transaction Types</option>
            <option value="BUY">BUY</option>
            <option value="SELL">SELL</option>
            <option value="CASH_DEPOSIT">CASH DEPOSIT</option>
            <option value="CASH_WITHDRAWAL">CASH WITHDRAWAL</option>
            <option value="CASH_DIVIDEND">CASH DIVIDEND</option>
            <option value="CASH_INTEREST">CASH INTEREST</option>
            <option value="ACCOUNT_FEE">ACCOUNT FEE</option>
            <option value="STOCK_SPLIT_ADJUSTMENT">STOCK SPLIT</option>
            <option value="CORRECTION_REVERSAL">REVERSAL</option>
          </select>
        </div>

        <span className="text-xs text-atlas-text-muted">
          Showing {filtered.length} of {transactions.length} journal records
        </span>
      </div>

      {/* Transaction Table */}
      <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-0">
        {filtered.length === 0 ? (
          <div className="py-12 text-center text-xs text-atlas-text-muted">
            {search || filterType !== "ALL"
              ? "No transactions matching filter criteria."
              : "No transactions recorded yet."}
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default bg-atlas-surface-1/70 text-[11px] font-semibold text-atlas-text-muted">
                <th className="py-2.5 px-3">Trade Date</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Security / Notes</th>
                <th className="py-2.5 px-3">Account</th>
                <th className="py-2.5 px-3 text-right">Shares</th>
                <th className="py-2.5 px-3 text-right">Unit Price</th>
                <th className="py-2.5 px-3 text-right">Fee / Tax</th>
                <th className="py-2.5 px-3 text-right">Net Cash Effect</th>
                <th className="py-2.5 px-3 text-center">Status</th>
                <th className="py-2.5 pr-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40 font-mono">
              {filtered.map((tx) => {
                const badge = getTransactionTypeBadge(tx.transaction_type);
                const acc = accounts.find((a) => a.id === tx.account_id);
                const netCash = parseFloat(tx.net_cash_amount);
                const isReversed = tx.status === "REVERSED";

                return (
                  <tr
                    key={tx.id}
                    className={`hover:bg-atlas-surface-1 transition-colors ${
                      isReversed ? "opacity-60 bg-atlas-surface-1/30" : ""
                    }`}
                  >
                    {/* Date */}
                    <td className="py-2.5 px-3 text-atlas-text-muted font-sans text-[11px]">
                      {formatDate(tx.trade_date)}
                    </td>

                    {/* Type Badge */}
                    <td className="py-2.5 px-3 font-sans">
                      <Badge variant={badge.variant} className="text-[10px] px-1.5 py-0.5">
                        {badge.label}
                      </Badge>
                    </td>

                    {/* Security / Notes */}
                    <td className="py-2.5 px-3 font-sans">
                      {tx.symbol ? (
                        <div className="font-bold text-atlas-text-primary">
                          {tx.symbol}
                          {tx.exchange ? ` (${tx.exchange})` : ""}
                        </div>
                      ) : (
                        <div className="text-atlas-text-primary font-medium">
                          {tx.notes || tx.transaction_type}
                        </div>
                      )}
                      {tx.notes && tx.symbol && (
                        <div className="text-[10px] text-atlas-text-muted">
                          {tx.notes}
                        </div>
                      )}
                    </td>

                    {/* Account */}
                    <td className="py-2.5 px-3 font-sans text-[11px] text-atlas-text-secondary">
                      {acc?.account_name || tx.account_id}
                    </td>

                    {/* Shares */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-primary">
                      {tx.quantity ? formatQuantity(tx.quantity) : "—"}
                    </td>

                    {/* Unit Price */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                      {tx.unit_price ? formatPrice(tx.unit_price, tx.cash_currency) : "—"}
                    </td>

                    {/* Fee & Tax */}
                    <td className="py-2.5 px-3 text-right text-atlas-text-muted text-[11px]">
                      {parseFloat(tx.fee) > 0 || parseFloat(tx.tax) > 0 ? (
                        <span>
                          {formatCurrency(parseFloat(tx.fee) + parseFloat(tx.tax), tx.cash_currency)}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>

                    {/* Net Cash Amount */}
                    <td
                      className={`py-2.5 px-3 text-right font-bold ${
                        netCash > 0
                          ? "text-emerald-400"
                          : netCash < 0
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {formatCurrency(tx.net_cash_amount, tx.cash_currency)}
                    </td>

                    {/* Status */}
                    <td className="py-2.5 px-3 text-center font-sans">
                      {isReversed ? (
                        <Badge variant="negative" className="text-[9px]">
                          REVERSED
                        </Badge>
                      ) : (
                        <Badge variant="positive" className="text-[9px]">
                          POSTED
                        </Badge>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-2.5 pr-3 text-right font-sans">
                      {!isReversed && tx.transaction_type !== "CORRECTION_REVERSAL" && (
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onReverse(tx)}
                            className="h-6 w-6 p-0 text-atlas-text-muted hover:text-rose-400"
                            title="Reverse Transaction"
                          >
                            <RotateCcw className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onCorrect(tx)}
                            className="h-6 w-6 p-0 text-atlas-text-muted hover:text-atlas-accent"
                            title="Correct Transaction"
                          >
                            <Edit2 className="h-3 w-3" />
                          </Button>
                        </div>
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
  );
}
