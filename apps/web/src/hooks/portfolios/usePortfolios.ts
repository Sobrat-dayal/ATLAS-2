"use client";

import { useCallback, useEffect, useState } from "react";
import { portfoliosApi } from "@/lib/portfolios/api";
import {
  AccountDTO,
  CashBalanceDTO,
  CorrectTransactionPayload,
  CreateAccountPayload,
  CreatePortfolioPayload,
  CreateTransactionPayload,
  LotDTO,
  PortfolioDTO,
  PositionDTO,
  ReconciliationDTO,
  TransactionDTO,
  ValuationDTO,
} from "@/lib/portfolios/types";

export type PortfolioTab =
  | "overview"
  | "holdings"
  | "transactions"
  | "cash"
  | "valuation"
  | "accounts"
  | "performance"
  | "allocation"
  | "attribution"
  | "optimization";

export function usePortfolios() {
  const [portfolios, setPortfolios] = useState<PortfolioDTO[]>([]);
  const [activePortfolio, setActivePortfolio] = useState<PortfolioDTO | null>(null);
  const [accounts, setAccounts] = useState<AccountDTO[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>("ALL");
  const [activeTab, setActiveTab] = useState<PortfolioTab>("overview");

  const [positions, setPositions] = useState<PositionDTO[]>([]);
  const [cashBalances, setCashBalances] = useState<CashBalanceDTO[]>([]);
  const [transactions, setTransactions] = useState<TransactionDTO[]>([]);
  const [valuation, setValuation] = useState<ValuationDTO | null>(null);
  const [reconciliation, setReconciliation] = useState<ReconciliationDTO | null>(null);

  const [selectedPosition, setSelectedPosition] = useState<PositionDTO | null>(null);
  const [selectedLots, setSelectedLots] = useState<LotDTO[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [isCreatePortfolioOpen, setIsCreatePortfolioOpen] = useState(false);
  const [isCreateAccountOpen, setIsCreateAccountOpen] = useState(false);
  const [isAddTransactionOpen, setIsAddTransactionOpen] = useState(false);
  const [isCorrectionOpen, setIsCorrectionOpen] = useState(false);
  const [correctionTargetTx, setCorrectionTargetTx] = useState<TransactionDTO | null>(null);

  // Fetch portfolios list on mount using async subscription pattern
  useEffect(() => {
    let ignore = false;
    portfoliosApi.listPortfolios().then(
      (res) => {
        if (ignore) return;
        setPortfolios(res.items);
        if (res.items.length > 0) {
          setActivePortfolio((prev) => {
            if (prev && res.items.some((p) => p.id === prev.id)) {
              return res.items.find((p) => p.id === prev.id)!;
            }
            return res.items[0];
          });
        } else {
          setActivePortfolio(null);
        }
        setLoading(false);
      },
      (err) => {
        if (ignore) return;
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      }
    );
    return () => {
      ignore = true;
    };
  }, []);

  const refreshPortfolioData = useCallback(async () => {
    if (!activePortfolio) return;
    const pId = activePortfolio.id;
    const filterAccId = selectedAccountId === "ALL" ? undefined : selectedAccountId;

    try {
      const [accsRes, posRes, cashRes, txRes, valRes, recRes] = await Promise.allSettled([
        portfoliosApi.listAccounts(pId),
        portfoliosApi.listPositions(pId, filterAccId),
        portfoliosApi.getCashBalances(pId, filterAccId),
        portfoliosApi.listTransactions(pId, { accountId: filterAccId, limit: 100 }),
        portfoliosApi.getValuation(pId),
        portfoliosApi.getReconciliation(pId),
      ]);

      if (accsRes.status === "fulfilled") setAccounts(accsRes.value.items);
      if (posRes.status === "fulfilled") setPositions(posRes.value.items);
      if (cashRes.status === "fulfilled") setCashBalances(cashRes.value);
      if (txRes.status === "fulfilled") setTransactions(txRes.value.items);
      if (valRes.status === "fulfilled") setValuation(valRes.value);
      if (recRes.status === "fulfilled") setReconciliation(recRes.value);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [activePortfolio, selectedAccountId]);

  // Sync data when active portfolio or account filter changes
  useEffect(() => {
    if (!activePortfolio) return;
    let ignore = false;
    const pId = activePortfolio.id;
    const filterAccId = selectedAccountId === "ALL" ? undefined : selectedAccountId;

    Promise.allSettled([
      portfoliosApi.listAccounts(pId),
      portfoliosApi.listPositions(pId, filterAccId),
      portfoliosApi.getCashBalances(pId, filterAccId),
      portfoliosApi.listTransactions(pId, { accountId: filterAccId, limit: 100 }),
      portfoliosApi.getValuation(pId),
      portfoliosApi.getReconciliation(pId),
    ]).then(([accsRes, posRes, cashRes, txRes, valRes, recRes]) => {
      if (ignore) return;
      if (accsRes.status === "fulfilled") setAccounts(accsRes.value.items);
      if (posRes.status === "fulfilled") setPositions(posRes.value.items);
      if (cashRes.status === "fulfilled") setCashBalances(cashRes.value);
      if (txRes.status === "fulfilled") setTransactions(txRes.value.items);
      if (valRes.status === "fulfilled") setValuation(valRes.value);
      if (recRes.status === "fulfilled") setReconciliation(recRes.value);
    });

    return () => {
      ignore = true;
    };
  }, [activePortfolio, selectedAccountId]);

  // When selected position changes, fetch its tax lots
  useEffect(() => {
    let ignore = false;
    if (!activePortfolio || !selectedPosition) {
      queueMicrotask(() => {
        if (!ignore) setSelectedLots([]);
      });
      return () => {
        ignore = true;
      };
    }
    const filterAccId = selectedAccountId === "ALL" ? undefined : selectedAccountId;
    portfoliosApi
      .listLots(activePortfolio.id, selectedPosition.instrument_id, filterAccId)
      .then(
        (res) => {
          if (!ignore) setSelectedLots(res.items);
        },
        () => {
          if (!ignore) setSelectedLots([]);
        }
      );
    return () => {
      ignore = true;
    };
  }, [activePortfolio, selectedPosition, selectedAccountId]);

  // Portfolio actions
  const selectPortfolio = (pId: string) => {
    const found = portfolios.find((p) => p.id === pId);
    if (found) {
      setActivePortfolio(found);
      setSelectedAccountId("ALL");
      setSelectedPosition(null);
    }
  };

  const createPortfolio = async (payload: CreatePortfolioPayload) => {
    const created = await portfoliosApi.createPortfolio(payload);
    const res = await portfoliosApi.listPortfolios();
    setPortfolios(res.items);
    setActivePortfolio(created);
    setIsCreatePortfolioOpen(false);
  };

  const createAccount = async (payload: CreateAccountPayload) => {
    if (!activePortfolio) return;
    await portfoliosApi.createAccount(activePortfolio.id, payload);
    await refreshPortfolioData();
    setIsCreateAccountOpen(false);
  };

  const postTransaction = async (payload: CreateTransactionPayload) => {
    if (!activePortfolio) return;
    await portfoliosApi.postTransaction(activePortfolio.id, payload);
    await refreshPortfolioData();
    setIsAddTransactionOpen(false);
  };

  const reverseTransaction = async (txId: string, reason: string) => {
    if (!activePortfolio) return;
    await portfoliosApi.reverseTransaction(activePortfolio.id, txId, reason);
    await refreshPortfolioData();
  };

  const correctTransaction = async (txId: string, payload: CorrectTransactionPayload) => {
    if (!activePortfolio) return;
    await portfoliosApi.correctTransaction(activePortfolio.id, txId, payload);
    await refreshPortfolioData();
    setIsCorrectionOpen(false);
    setCorrectionTargetTx(null);
  };

  const recalculateValuation = async () => {
    if (!activePortfolio) return;
    try {
      const fresh = await portfoliosApi.recalculateValuation(activePortfolio.id);
      setValuation(fresh);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return {
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
    // Modals
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
  };
}
