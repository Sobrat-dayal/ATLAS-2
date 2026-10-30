"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  getReconciliationBadge,
  getValuationStatusBadge,
} from "@/lib/portfolios/formatting";
import {
  AccountDTO,
  PortfolioDTO,
  ReconciliationDTO,
  ValuationDTO,
} from "@/lib/portfolios/types";
import { PortfolioTab } from "@/hooks/portfolios/usePortfolios";
import {
  Briefcase,
  Layers,
  Plus,
  RefreshCw,
} from "lucide-react";

interface PortfolioHeaderProps {
  portfolios: PortfolioDTO[];
  activePortfolio: PortfolioDTO | null;
  accounts: AccountDTO[];
  selectedAccountId: string;
  activeTab: PortfolioTab;
  valuation: ValuationDTO | null;
  reconciliation: ReconciliationDTO | null;
  onSelectPortfolio: (id: string) => void;
  onSelectAccount: (id: string) => void;
  onTabChange: (tab: PortfolioTab) => void;
  onOpenCreatePortfolio: () => void;
  onOpenCreateAccount: () => void;
  onOpenAddTransaction: () => void;
  onRecalculateValuation: () => void;
}

export function PortfolioHeader({
  portfolios,
  activePortfolio,
  accounts,
  selectedAccountId,
  activeTab,
  valuation,
  reconciliation,
  onSelectPortfolio,
  onSelectAccount,
  onTabChange,
  onOpenCreatePortfolio,
  onOpenCreateAccount,
  onOpenAddTransaction,
  onRecalculateValuation,
}: PortfolioHeaderProps) {
  const valBadge = valuation
    ? getValuationStatusBadge(valuation.valuation_status)
    : null;
  const recBadge = reconciliation
    ? getReconciliationBadge(reconciliation.status)
    : null;

  return (
    <div className="border-b border-atlas-border-default bg-atlas-surface-0 px-4 py-3 shrink-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Module Title & Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-sm bg-atlas-accent/10 text-atlas-accent">
              <Briefcase className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold tracking-tight text-atlas-text-primary">
                  PORTFOLIOS
                </span>
                <Badge variant="outline" className="font-mono text-[10px]">
                  STAGE 110 V1
                </Badge>
                {valBadge && (
                  <Badge variant={valBadge.variant} className="text-[10px]">
                    {valBadge.label}
                  </Badge>
                )}
                {recBadge && (
                  <Badge variant={recBadge.variant} className="text-[10px]">
                    {recBadge.label}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          <div className="h-4 w-px bg-atlas-border-default hidden sm:block" />

          {/* Portfolio Selector */}
          <div className="flex items-center gap-2">
            <label htmlFor="portfolio-select" className="sr-only">Select Portfolio</label>
            <select
              id="portfolio-select"
              aria-label="Select Portfolio"
              value={activePortfolio?.id || ""}
              onChange={(e) => onSelectPortfolio(e.target.value)}
              className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs font-semibold text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              {portfolios.length === 0 ? (
                <option value="">No Portfolios</option>
              ) : (
                portfolios.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.base_currency})
                  </option>
                ))
              )}
            </select>

            {/* Account Selector */}
            {activePortfolio && (
              <>
                <label htmlFor="account-select" className="sr-only">Select Account</label>
                <select
                  id="account-select"
                  aria-label="Select Account"
                  value={selectedAccountId}
                  onChange={(e) => onSelectAccount(e.target.value)}
                  className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-medium text-atlas-text-secondary focus:border-atlas-accent focus:outline-none"
                >
                  <option value="ALL">All Accounts ({accounts.length})</option>
                  {accounts.map((acc) => (
                    <option key={acc.id} value={acc.id}>
                      {acc.account_name} ({acc.primary_currency})
                    </option>
                  ))}
                </select>
              </>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {activePortfolio && (
            <>
              <Button
                variant="primary"
                size="sm"
                onClick={onOpenAddTransaction}
                className="h-8 gap-1 text-xs"
              >
                <Plus className="h-3.5 w-3.5" />
                Add Transaction
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={onOpenCreateAccount}
                className="h-8 gap-1 text-xs"
              >
                <Layers className="h-3.5 w-3.5" />
                New Account
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onRecalculateValuation}
                className="h-8 gap-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary"
                title="Recalculate Marked Valuation"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Recalculate
              </Button>
            </>
          )}

          <Button
            variant="secondary"
            size="sm"
            onClick={onOpenCreatePortfolio}
            className="h-8 gap-1 text-xs"
          >
            <Plus className="h-3.5 w-3.5" />
            New Portfolio
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      {activePortfolio && (
        <div className="mt-3 flex items-center border-t border-atlas-border-default/60 pt-2">
          <nav className="flex space-x-1" aria-label="Portfolio Workspaces">
            {(
              [
                { id: "overview", label: "Overview" },
                { id: "performance", label: "Performance Analytics" },
                { id: "allocation", label: "Allocation & Exposures" },
                { id: "holdings", label: "Holdings & Lots" },
                { id: "transactions", label: "Transaction Journal" },
                { id: "cash", label: "Cash Workspace" },
                { id: "valuation", label: "Valuation & Mark Sources" },
                { id: "accounts", label: "Investment Accounts" },
              ] as const
            ).map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`rounded-sm px-3 py-1.5 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      )}
    </div>
  );
}

