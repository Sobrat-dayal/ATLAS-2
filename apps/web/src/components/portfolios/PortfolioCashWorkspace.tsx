"use client";

import React, { useEffect, useState } from "react";
import { Badge } from "@/design-system";
import { portfoliosApi } from "@/lib/portfolios/api";
import { formatCurrency, formatDate } from "@/lib/portfolios/formatting";
import {
  AccountDTO,
  CashBalanceDTO,
  CashLedgerEntryDTO,
  PortfolioDTO,
  ValuationDTO,
} from "@/lib/portfolios/types";
import { Landmark, Receipt } from "lucide-react";

interface PortfolioCashWorkspaceProps {
  portfolio: PortfolioDTO;
  accounts: AccountDTO[];
  cashBalances: CashBalanceDTO[];
  valuation: ValuationDTO | null;
}

export function PortfolioCashWorkspace({
  portfolio,
  accounts,
  cashBalances,
  valuation,
}: PortfolioCashWorkspaceProps) {
  const [selectedAccId, setSelectedAccId] = useState<string>("");
  const [ledgerEntries, setLedgerEntries] = useState<CashLedgerEntryDTO[]>([]);
  const [loadingLedger, setLoadingLedger] = useState(false);

  const baseCur = portfolio.base_currency;
  const activeAccountId = selectedAccId || accounts[0]?.id || "";

  useEffect(() => {
    if (!activeAccountId) return;
    let ignore = false;
    portfoliosApi
      .getCashLedger(portfolio.id, activeAccountId)
      .then((entries) => {
        if (!ignore) {
          setLedgerEntries(entries);
          setLoadingLedger(false);
        }
      })
      .catch(() => {
        if (!ignore) {
          setLedgerEntries([]);
          setLoadingLedger(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [portfolio.id, activeAccountId]);

  return (
    <div className="space-y-4 p-4">
      {/* Balances Summary Table */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
        <div className="flex items-center justify-between border-b border-atlas-border-default pb-2">
          <div className="flex items-center gap-2">
            <Landmark className="h-4 w-4 text-atlas-accent" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Multi-Currency Cash Balances by Account
            </h2>
          </div>
          <span className="text-xs text-atlas-text-muted">
            Total Cash: {valuation ? formatCurrency(valuation.total_cash_market_value, baseCur) : "—"}
          </span>
        </div>

        <div className="mt-2 overflow-x-auto">
          {cashBalances.length === 0 ? (
            <div className="py-6 text-center text-xs text-atlas-text-muted">
              No cash balances found. Record a cash deposit to fund an account.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-atlas-border-default text-[10px] font-semibold text-atlas-text-muted">
                  <th className="py-2 px-3 font-sans">Account</th>
                  <th className="py-2 px-3 font-sans">Currency</th>
                  <th className="py-2 px-3 text-right">Posted Cash</th>
                  <th className="py-2 px-3 text-right">Settled Cash</th>
                  <th className="py-2 px-3 text-right">Pending Recv</th>
                  <th className="py-2 px-3 text-right">Pending Pay</th>
                  <th className="py-2 px-3 text-right">Available Cash</th>
                  <th className="py-2 px-3 text-right">FX to {baseCur}</th>
                  <th className="py-2 px-3 text-right">Value ({baseCur})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30">
                {cashBalances.map((cb, idx) => {
                  const acc = accounts.find((a) => a.id === cb.account_id);
                  const cashVal = valuation?.cash_valuations.find(
                    (v) => v.account_id === cb.account_id && v.currency === cb.currency
                  );

                  return (
                    <tr key={idx} className="hover:bg-atlas-surface-1">
                      <td className="py-2.5 px-3 font-sans text-atlas-text-primary font-medium">
                        {acc?.account_name || cb.account_id}
                      </td>
                      <td className="py-2.5 px-3 font-sans">
                        <Badge variant="outline" className="text-[10px]">
                          {cb.currency}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                        {formatCurrency(cb.posted_cash, cb.currency)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                        {formatCurrency(cb.settled_cash, cb.currency)}
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-muted">
                        {formatCurrency(cb.unsettled_receivable, cb.currency)}
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-muted">
                        {formatCurrency(cb.unsettled_payable, cb.currency)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-medium text-emerald-400">
                        {formatCurrency(cb.available_cash, cb.currency)}
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                        {cashVal ? cashVal.fx_rate_to_base : "1.0000"}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-atlas-text-primary">
                        {cashVal ? formatCurrency(cashVal.base_cash_value, baseCur) : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Cash Ledger Audit Trail */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default pb-2">
          <div className="flex items-center gap-2">
            <Receipt className="h-4 w-4 text-atlas-accent" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Account Cash Journal & Audit Trail
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="cash-account-select" className="sr-only">Select Account for Cash Journal</label>
            <select
              id="cash-account-select"
              aria-label="Select Account for Cash Journal"
              value={activeAccountId}
              onChange={(e) => setSelectedAccId(e.target.value)}
              className="h-7 rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-medium text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.account_name} ({a.primary_currency})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-2 overflow-x-auto">
          {loadingLedger ? (
            <div className="py-8 text-center text-xs text-atlas-text-muted">
              Loading ledger entries...
            </div>
          ) : ledgerEntries.length === 0 ? (
            <div className="py-8 text-center text-xs text-atlas-text-muted">
              No cash ledger entries for this account.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-atlas-border-default text-[10px] font-semibold text-atlas-text-muted">
                  <th className="py-2 px-3 font-sans">Date</th>
                  <th className="py-2 px-3 font-sans">Entry ID</th>
                  <th className="py-2 px-3 font-sans">Description</th>
                  <th className="py-2 px-3 font-sans">Classification</th>
                  <th className="py-2 px-3 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30">
                {ledgerEntries.map((e) => {
                  const amt = parseFloat(e.amount);
                  return (
                    <tr key={e.id} className="hover:bg-atlas-surface-1">
                      <td className="py-2 px-3 text-atlas-text-muted font-sans text-[11px]">
                        {formatDate(e.effective_date)}
                      </td>
                      <td className="py-2 px-3 text-atlas-text-secondary text-[11px]">
                        {e.id}
                      </td>
                      <td className="py-2 px-3 font-sans text-atlas-text-primary font-medium">
                        {e.description}
                      </td>
                      <td className="py-2 px-3 font-sans">
                        <Badge variant="outline" className="text-[9px]">
                          {e.balance_type}
                        </Badge>
                      </td>
                      <td
                        className={`py-2 px-3 text-right font-bold ${
                          amt >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {formatCurrency(e.amount, e.currency)}
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
