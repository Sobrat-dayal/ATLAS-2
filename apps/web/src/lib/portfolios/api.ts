/**
 * ATLAS Portfolios V1 — Typed API Client.
 */

import {
  AccountDTO,
  CashBalanceDTO,
  CashLedgerEntryDTO,
  CorrectTransactionPayload,
  CreateAccountPayload,
  CreatePortfolioPayload,
  CreateTransactionPayload,
  LotDTO,
  PortfolioDTO,
  PositionDTO,
  ReconciliationDTO,
  TransactionDTO,
  TransactionPreviewDTO,
  ValuationDTO,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === "object" && errorJson.detail.message) {
          errorDetail = errorJson.detail.message;
        } else {
          errorDetail = String(errorJson.detail);
        }
      } else if (errorJson.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      errorDetail = `${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const portfoliosApi = {
  // -------------------------------------------------------------------------
  // Portfolio CRUD
  // -------------------------------------------------------------------------

  async listPortfolios(): Promise<{ items: PortfolioDTO[]; total: number }> {
    return request("/portfolios");
  },

  async createPortfolio(payload: CreatePortfolioPayload): Promise<PortfolioDTO> {
    return request("/portfolios", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getPortfolio(id: string): Promise<PortfolioDTO> {
    return request(`/portfolios/${id}`);
  },

  async updatePortfolio(
    id: string,
    payload: { name?: string; description?: string; status?: string; revision: number }
  ): Promise<PortfolioDTO> {
    return request(`/portfolios/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  async deletePortfolio(id: string): Promise<void> {
    return request(`/portfolios/${id}`, {
      method: "DELETE",
    });
  },

  // -------------------------------------------------------------------------
  // Account Operations
  // -------------------------------------------------------------------------

  async listAccounts(portfolioId: string): Promise<{ items: AccountDTO[]; total: number }> {
    return request(`/portfolios/${portfolioId}/accounts`);
  },

  async createAccount(portfolioId: string, payload: CreateAccountPayload): Promise<AccountDTO> {
    return request(`/portfolios/${portfolioId}/accounts`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getAccount(portfolioId: string, accountId: string): Promise<AccountDTO> {
    return request(`/portfolios/${portfolioId}/accounts/${accountId}`);
  },

  async updateAccount(
    portfolioId: string,
    accountId: string,
    payload: Partial<CreateAccountPayload>
  ): Promise<AccountDTO> {
    return request(`/portfolios/${portfolioId}/accounts/${accountId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  async deleteAccount(portfolioId: string, accountId: string): Promise<void> {
    return request(`/portfolios/${portfolioId}/accounts/${accountId}`, {
      method: "DELETE",
    });
  },

  // -------------------------------------------------------------------------
  // Holdings & Lots
  // -------------------------------------------------------------------------

  async listPositions(
    portfolioId: string,
    accountId?: string
  ): Promise<{ items: PositionDTO[]; total: number }> {
    const endpoint = accountId
      ? `/portfolios/${portfolioId}/accounts/${accountId}/positions`
      : `/portfolios/${portfolioId}/positions`;
    return request(endpoint);
  },

  async listLots(
    portfolioId: string,
    instrumentId: string,
    accountId?: string
  ): Promise<{ items: LotDTO[]; total: number }> {
    const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : "";
    return request(`/portfolios/${portfolioId}/positions/${instrumentId}/lots${query}`);
  },

  // -------------------------------------------------------------------------
  // Transactions
  // -------------------------------------------------------------------------

  async listTransactions(
    portfolioId: string,
    filters?: {
      accountId?: string;
      instrumentId?: string;
      txType?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<{ items: TransactionDTO[]; total: number }> {
    const params = new URLSearchParams();
    if (filters?.accountId) params.set("account_id", filters.accountId);
    if (filters?.instrumentId) params.set("instrument_id", filters.instrumentId);
    if (filters?.txType) params.set("tx_type", filters.txType);
    if (filters?.limit) params.set("limit", String(filters.limit));
    if (filters?.offset) params.set("offset", String(filters.offset));

    const qs = params.toString() ? `?${params.toString()}` : "";
    return request(`/portfolios/${portfolioId}/transactions${qs}`);
  },

  async previewTransaction(
    portfolioId: string,
    payload: CreateTransactionPayload
  ): Promise<TransactionPreviewDTO> {
    return request(`/portfolios/${portfolioId}/transactions/preview`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async postTransaction(
    portfolioId: string,
    payload: CreateTransactionPayload
  ): Promise<TransactionDTO> {
    return request(`/portfolios/${portfolioId}/transactions`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async reverseTransaction(
    portfolioId: string,
    transactionId: string,
    reason: string
  ): Promise<TransactionDTO> {
    return request(`/portfolios/${portfolioId}/transactions/${transactionId}/reverse`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  },

  async correctTransaction(
    portfolioId: string,
    transactionId: string,
    payload: CorrectTransactionPayload
  ): Promise<TransactionDTO> {
    return request(`/portfolios/${portfolioId}/transactions/${transactionId}/correct`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // -------------------------------------------------------------------------
  // Cash Management
  // -------------------------------------------------------------------------

  async getCashBalances(portfolioId: string, accountId?: string): Promise<CashBalanceDTO[]> {
    const endpoint = accountId
      ? `/portfolios/${portfolioId}/accounts/${accountId}/cash`
      : `/portfolios/${portfolioId}/cash`;
    return request(endpoint);
  },

  async getCashLedger(portfolioId: string, accountId: string): Promise<CashLedgerEntryDTO[]> {
    return request(`/portfolios/${portfolioId}/accounts/${accountId}/cash-ledger`);
  },

  // -------------------------------------------------------------------------
  // Valuation & Reconciliation
  // -------------------------------------------------------------------------

  async getValuation(portfolioId: string): Promise<ValuationDTO> {
    return request(`/portfolios/${portfolioId}/valuation`);
  },

  async recalculateValuation(portfolioId: string): Promise<ValuationDTO> {
    return request(`/portfolios/${portfolioId}/valuations`, {
      method: "POST",
    });
  },

  async getReconciliation(portfolioId: string): Promise<ReconciliationDTO> {
    return request(`/portfolios/${portfolioId}/reconciliation`);
  },
};

