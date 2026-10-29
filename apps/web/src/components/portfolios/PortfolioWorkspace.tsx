"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { usePortfolios } from "@/hooks/portfolios/usePortfolios";
import { AccountsWorkspace } from "./AccountsWorkspace";
import { AddTransactionModal } from "./AddTransactionModal";
import { CreateAccountModal } from "./CreateAccountModal";
import { CreatePortfolioModal } from "./CreatePortfolioModal";
import { PortfolioCashWorkspace } from "./PortfolioCashWorkspace";
import { PortfolioHeader } from "./PortfolioHeader";
import { PortfolioHoldingsTable } from "./PortfolioHoldingsTable";
import { PortfolioOverview } from "./PortfolioOverview";
import { PortfolioPositionInspector } from "./PortfolioPositionInspector";
import { PortfolioValuationWorkspace } from "./PortfolioValuationWorkspace";
import { TransactionCorrectionModal } from "./TransactionCorrectionModal";
import { TransactionHistory } from "./TransactionHistory";
import { TransactionDTO } from "@/lib/portfolios/types";
import { AlertCircle, Briefcase, Plus, RefreshCw } from "lucide-react";

export function PortfolioWorkspace() {
  const {
    portfolios,
    activePortfolio,
    accounts,
    selectedAccountId,
    setSelectedAccountId,
    activeTab,
    setActiveTab,
    positions,
    cashBalances,
    transactions,
    valuation,
    reconciliation,
    selectedPosition,
    setSelectedPosition,
    selectedLots,
    loading,
    error,
    refreshPortfolioData,
    selectPortfolio,
    createPortfolio,
    createAccount,
    postTransaction,
    reverseTransaction,
    correctTransaction,
    recalculateValuation,
    isCreatePortfolioOpen,
    setIsCreatePortfolioOpen,
    isCreateAccountOpen,
    setIsCreateAccountOpen,
    isAddTransactionOpen,
    setIsAddTransactionOpen,
    isCorrectionOpen,
    setIsCorrectionOpen,
    correctionTargetTx,
    setCorrectionTargetTx,
  } = usePortfolios();

  const [reversalConfirmTx, setReversalConfirmTx] = useState<TransactionDTO | null>(null);
  const [reversalReason, setReversalReason] = useState("Erroneous entry");

  const handleReverseClick = (tx: TransactionDTO) => {
    setReversalConfirmTx(tx);
    setReversalReason("Erroneous entry");
  };

  const handleConfirmReverse = async () => {
    if (!reversalConfirmTx) return;
    await reverseTransaction(reversalConfirmTx.id, reversalReason);
    setReversalConfirmTx(null);
  };

  const handleCorrectClick = (tx: TransactionDTO) => {
    setCorrectionTargetTx(tx);
    setIsCorrectionOpen(true);
  };

  if (loading && portfolios.length === 0) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-3">
        <RefreshCw className="h-6 w-6 animate-spin text-atlas-accent" />
        <p className="text-xs text-atlas-text-muted">Loading portfolio ledgers...</p>
      </div>
    );
  }

  // Global Empty State
  if (!loading && portfolios.length === 0) {
    return (
      <div className="flex flex-col min-h-[calc(100vh-8rem)]">
        <div className="border-b border-atlas-border-default bg-atlas-surface-0 px-4 py-3 shrink-0">
          <div className="flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-atlas-accent" />
            <h1 className="text-sm font-bold tracking-tight text-atlas-text-primary">
              PORTFOLIOS
            </h1>
            <Badge variant="outline" className="font-mono text-[10px]">
              STAGE 110 V1
            </Badge>
          </div>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-sm bg-atlas-surface-2 text-atlas-text-secondary">
            <Briefcase className="h-6 w-6 text-atlas-accent" />
          </div>
          <h2 className="mt-4 text-base font-bold text-atlas-text-primary">
            No Portfolios Recorded
          </h2>
          <p className="mt-1.5 max-w-md text-xs text-atlas-text-muted">
            Create an institutional portfolio foundation to manage investment accounts, record immutable transaction ledgers, track FIFO tax lots, and calculate marked valuations.
          </p>
          <div className="mt-5">
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsCreatePortfolioOpen(true)}
              className="gap-1.5 text-xs"
            >
              <Plus className="h-3.5 w-3.5" />
              Create First Portfolio
            </Button>
          </div>
        </div>

        {/* Create Modal */}
        <CreatePortfolioModal
          isOpen={isCreatePortfolioOpen}
          onClose={() => setIsCreatePortfolioOpen(false)}
          onSubmit={createPortfolio}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-[calc(100vh-8rem)] bg-atlas-background">
      {/* Header */}
      <PortfolioHeader
        portfolios={portfolios}
        activePortfolio={activePortfolio}
        accounts={accounts}
        selectedAccountId={selectedAccountId}
        activeTab={activeTab}
        valuation={valuation}
        reconciliation={reconciliation}
        onSelectPortfolio={selectPortfolio}
        onSelectAccount={setSelectedAccountId}
        onTabChange={setActiveTab}
        onOpenCreatePortfolio={() => setIsCreatePortfolioOpen(true)}
        onOpenCreateAccount={() => setIsCreateAccountOpen(true)}
        onOpenAddTransaction={() => setIsAddTransactionOpen(true)}
        onRecalculateValuation={recalculateValuation}
      />

      {/* Global Error Banner if any */}
      {error && (
        <div className="m-4 flex items-center justify-between rounded-xs border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-400">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshPortfolioData}
            className="h-6 text-[10px] text-rose-400"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Active Tab Workspace */}
      <div className="flex-1 overflow-y-auto">
        {activePortfolio && (
          <>
            {activeTab === "overview" && (
              <PortfolioOverview
                portfolio={activePortfolio}
                positions={positions}
                cashBalances={cashBalances}
                transactions={transactions}
                valuation={valuation}
                reconciliation={reconciliation}
                onNavigateTab={(tab) => {
                  setActiveTab(tab);
                  setSelectedPosition(null);
                }}
                onSelectPosition={(pos) => {
                  setSelectedPosition(pos);
                  setActiveTab("holdings");
                }}
              />
            )}

            {activeTab === "holdings" && (
              <div className="space-y-4">
                {selectedPosition && (
                  <div className="p-4 pb-0">
                    <PortfolioPositionInspector
                      position={selectedPosition}
                      lots={selectedLots}
                      valuation={valuation}
                      baseCurrency={activePortfolio.base_currency}
                      onClose={() => setSelectedPosition(null)}
                    />
                  </div>
                )}
                <PortfolioHoldingsTable
                  portfolio={activePortfolio}
                  positions={positions}
                  accounts={accounts}
                  valuation={valuation}
                  onSelectPosition={(pos) => setSelectedPosition(pos)}
                />
              </div>
            )}

            {activeTab === "transactions" && (
              <TransactionHistory
                transactions={transactions}
                accounts={accounts}
                onReverse={handleReverseClick}
                onCorrect={handleCorrectClick}
              />
            )}

            {activeTab === "cash" && (
              <PortfolioCashWorkspace
                portfolio={activePortfolio}
                accounts={accounts}
                cashBalances={cashBalances}
                valuation={valuation}
              />
            )}

            {activeTab === "valuation" && (
              <PortfolioValuationWorkspace
                portfolio={activePortfolio}
                valuation={valuation}
                onRecalculate={recalculateValuation}
              />
            )}

            {activeTab === "accounts" && (
              <AccountsWorkspace
                portfolio={activePortfolio}
                accounts={accounts}
                onOpenCreateAccount={() => setIsCreateAccountOpen(true)}
              />
            )}
          </>
        )}
      </div>

      {/* Modals */}
      {activePortfolio && (
        <>
          <CreateAccountModal
            portfolio={activePortfolio}
            isOpen={isCreateAccountOpen}
            onClose={() => setIsCreateAccountOpen(false)}
            onSubmit={createAccount}
          />

          <AddTransactionModal
            portfolio={activePortfolio}
            accounts={accounts}
            isOpen={isAddTransactionOpen}
            onClose={() => setIsAddTransactionOpen(false)}
            onSuccess={postTransaction}
          />

          <TransactionCorrectionModal
            targetTx={correctionTargetTx}
            isOpen={isCorrectionOpen}
            onClose={() => {
              setIsCorrectionOpen(false);
              setCorrectionTargetTx(null);
            }}
            onSuccess={correctTransaction}
          />
        </>
      )}

      <CreatePortfolioModal
        isOpen={isCreatePortfolioOpen}
        onClose={() => setIsCreatePortfolioOpen(false)}
        onSubmit={createPortfolio}
      />

      {/* Controlled Reversal Confirmation Dialog */}
      {reversalConfirmTx && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-5 shadow-2xl">
            <h2 className="text-sm font-bold text-atlas-text-primary uppercase tracking-wide">
              Confirm Transaction Reversal
            </h2>
            <p className="mt-2 text-xs text-atlas-text-muted">
              Are you sure you want to reverse journal entry{" "}
              <span className="font-mono text-atlas-text-primary">{reversalConfirmTx.id}</span> (
              {reversalConfirmTx.transaction_type} {reversalConfirmTx.symbol || ""})?
            </p>
            <div className="mt-3">
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Audit Reason:
              </label>
              <input
                type="text"
                value={reversalReason}
                onChange={(e) => setReversalReason(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
            <div className="mt-4 flex items-center justify-end gap-2 border-t border-atlas-border-default pt-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setReversalConfirmTx(null)}
                className="h-8 text-xs"
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={handleConfirmReverse}
                className="h-8 text-xs"
              >
                Confirm Reversal
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

