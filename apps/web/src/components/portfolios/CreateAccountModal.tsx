"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { AccountType, CreateAccountPayload, PortfolioDTO } from "@/lib/portfolios/types";
import { AlertCircle, Layers, X } from "lucide-react";

interface CreateAccountModalProps {
  portfolio: PortfolioDTO;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateAccountPayload) => Promise<void>;
}

export function CreateAccountModal({
  portfolio,
  isOpen,
  onClose,
  onSubmit,
}: CreateAccountModalProps) {
  const [accountName, setAccountName] = useState("");
  const [accountType, setAccountType] = useState<AccountType>("INVESTMENT_ACCOUNT");
  const [primaryCurrency, setPrimaryCurrency] = useState(portfolio.base_currency);
  const [custodianName, setCustodianName] = useState("");
  const [accountMask, setAccountMask] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountName.trim()) {
      setError("Please enter a valid account name.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        account_name: accountName.trim(),
        account_type: accountType,
        primary_currency: primaryCurrency,
        custodian_name: custodianName.trim() || undefined,
        account_number_mask: accountMask.trim() || undefined,
      });
      setAccountName("");
      setCustodianName("");
      setAccountMask("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-md rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-atlas-border-default pb-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-atlas-accent" />
            <h2 className="text-sm font-bold uppercase tracking-wide text-atlas-text-primary">
              Add Investment Account
            </h2>
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

        {error && (
          <div className="mt-3 flex items-center gap-2 rounded-xs border border-rose-500/30 bg-rose-500/10 p-2 text-xs text-rose-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <div>
            <label className="text-[11px] font-medium text-atlas-text-secondary">
              Account Name *
            </label>
            <input
              type="text"
              placeholder="e.g. Primary Trading, Fidelity Taxable"
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              required
              className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Account Type
              </label>
              <select
                value={accountType}
                onChange={(e) => setAccountType(e.target.value as AccountType)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                <option value="INVESTMENT_ACCOUNT">Investment Account</option>
                <option value="BROKERAGE_RECORD">Brokerage Record</option>
                <option value="CASH_ACCOUNT">Cash Account</option>
                <option value="MANUAL_PORTFOLIO_ACCOUNT">Manual Accounting</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Primary Currency
              </label>
              <select
                value={primaryCurrency}
                onChange={(e) => setPrimaryCurrency(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="INR">INR</option>
                <option value="JPY">JPY</option>
                <option value="CAD">CAD</option>
                <option value="AUD">AUD</option>
                <option value="CHF">CHF</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Custodian (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Morgan Stanley, IBKR"
                value={custodianName}
                onChange={(e) => setCustodianName(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Account Mask (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. ****8891"
                value={accountMask}
                onChange={(e) => setAccountMask(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-5 flex items-center justify-end gap-2 border-t border-atlas-border-default pt-3">
            <Button variant="ghost" size="sm" type="button" onClick={onClose} className="h-8 text-xs">
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={loading} className="h-8 text-xs">
              {loading ? "Adding..." : "Add Account"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

