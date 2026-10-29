/**
 * ATLAS Portfolios V1 — TypeScript Domain Types and API Contracts (Stage 110).
 */

export type PortfolioType = "PERSONAL" | "MODEL_ACCOUNTING" | "INSTITUTIONAL";

export type PortfolioStatus = "ACTIVE" | "ARCHIVED";

export type AccountType =
  | "BROKERAGE_RECORD"
  | "INVESTMENT_ACCOUNT"
  | "CASH_ACCOUNT"
  | "MANUAL_PORTFOLIO_ACCOUNT";

export type AccountStatus = "ACTIVE" | "CLOSED" | "ARCHIVED";

export type TransactionType =
  | "BUY"
  | "SELL"
  | "CASH_DEPOSIT"
  | "CASH_WITHDRAWAL"
  | "CASH_TRANSFER_IN"
  | "CASH_TRANSFER_OUT"
  | "CASH_DIVIDEND"
  | "CASH_INTEREST"
  | "ACCOUNT_FEE"
  | "WITHHOLDING_TAX"
  | "STOCK_SPLIT_ADJUSTMENT"
  | "CORRECTION_REVERSAL";

export type TransactionStatus = "POSTED" | "REVERSED" | "CORRECTED";

export type CashBalanceType =
  | "POSTED_CASH"
  | "SETTLED_CASH"
  | "UNSETTLED_RECEIVABLE"
  | "UNSETTLED_PAYABLE"
  | "AVAILABLE_CASH";

export type CostBasisMethod = "FIFO";

export type ValuationCompletenessStatus =
  | "COMPLETE"
  | "PARTIAL_MISSING_PRICES"
  | "PARTIAL_MISSING_FX"
  | "PARTIAL_STALE_DATA"
  | "UNAVAILABLE"
  | "FAILED";

export type QuoteFreshness =
  | "REALTIME"
  | "DELAYED"
  | "END_OF_DAY"
  | "HISTORICAL"
  | "STALE"
  | "UNAVAILABLE";

export type ReconciliationStatus =
  | "RECONCILED"
  | "RECONCILIATION_WARNING"
  | "OUT_OF_BALANCE"
  | "INCOMPLETE_INPUTS";

export interface PortfolioDTO {
  id: string;
  user_id: string;
  name: string;
  portfolio_type: PortfolioType;
  base_currency: string;
  status: PortfolioStatus;
  cost_basis_method: CostBasisMethod;
  description?: string | null;
  account_count: number;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface AccountDTO {
  id: string;
  portfolio_id: string;
  user_id: string;
  account_name: string;
  account_type: AccountType;
  primary_currency: string;
  custodian_name?: string | null;
  account_number_mask?: string | null;
  status: AccountStatus;
  created_at: string;
  updated_at: string;
}

export interface TransactionDTO {
  id: string;
  portfolio_id: string;
  account_id: string;
  user_id: string;
  transaction_type: TransactionType;
  status: TransactionStatus;
  cash_currency: string;
  trade_date: string;
  settlement_date: string;
  instrument_id?: string | null;
  symbol?: string | null;
  exchange?: string | null;
  company_name?: string | null;
  quantity?: string | null;
  unit_price?: string | null;
  gross_amount?: string | null;
  fee: string;
  tax: string;
  net_cash_amount: string;
  idempotency_key?: string | null;
  notes?: string | null;
  reverses_transaction_id?: string | null;
  reversed_by_transaction_id?: string | null;
  created_at: string;
}

export interface TransactionPreviewDTO {
  transaction_type: string;
  gross_amount: string;
  fee: string;
  tax: string;
  net_cash_amount: string;
  estimated_resulting_cash: string;
  resulting_quantity?: string | null;
  unit_cost_basis?: string | null;
  consumed_basis?: string | null;
  estimated_realized_pnl?: string | null;
  warnings: string[];
}

export interface PositionDTO {
  portfolio_id: string;
  account_id?: string | null;
  instrument_id: string;
  symbol: string;
  exchange: string;
  company_name?: string | null;
  quantity: string;
  open_lot_count: number;
  remaining_cost_basis: string;
  cost_basis_currency: string;
  average_unit_cost?: string | null;
  realized_pnl: string;
  unrealized_pnl?: string | null;
  as_of: string;
}

export interface LotDTO {
  id: string;
  portfolio_id: string;
  account_id: string;
  instrument_id: string;
  acquisition_transaction_id: string;
  acquisition_date: string;
  original_quantity: string;
  remaining_quantity: string;
  unit_cost_basis: string;
  total_cost_basis: string;
  currency: string;
  is_fully_disposed: boolean;
  disposed_at?: string | null;
}

export interface CashBalanceDTO {
  account_id: string;
  currency: string;
  posted_cash: string;
  settled_cash: string;
  unsettled_receivable: string;
  unsettled_payable: string;
  available_cash: string;
  as_of: string;
}

export interface CashLedgerEntryDTO {
  id: string;
  account_id: string;
  transaction_id: string;
  currency: string;
  amount: string;
  balance_type: string;
  effective_date: string;
  description: string;
  created_at: string;
}

export interface PositionValuationDTO {
  instrument_id: string;
  symbol: string;
  exchange: string;
  quantity: string;
  remaining_basis: string;
  basis_currency: string;
  valuation_status: ValuationCompletenessStatus;
  quote_freshness: QuoteFreshness;
  account_id?: string | null;
  company_name?: string | null;
  mark_price?: string | null;
  price_currency?: string | null;
  mark_as_of?: string | null;
  mark_source?: string | null;
  native_market_value?: string | null;
  fx_rate_to_base?: string | null;
  fx_pair?: string | null;
  fx_as_of?: string | null;
  base_market_value?: string | null;
  unrealized_pnl?: string | null;
}

export interface CashValuationDTO {
  account_id: string;
  currency: string;
  posted_cash: string;
  settled_cash: string;
  unsettled_receivable: string;
  unsettled_payable: string;
  available_cash: string;
  fx_rate_to_base: string;
  base_cash_value: string;
  as_of: string;
}

export interface ValuationDTO {
  id: string;
  portfolio_id: string;
  as_of: string;
  base_currency: string;
  valuation_status: ValuationCompletenessStatus;
  known_valued_subtotal: string;
  verified_total_portfolio_value?: string | null;
  total_positions_market_value?: string | null;
  total_cash_market_value: string;
  total_cost_basis: string;
  total_unrealized_pnl?: string | null;
  total_realized_pnl: string;
  missing_prices_count: number;
  missing_fx_count: number;
  stale_quotes_count: number;
  position_valuations: PositionValuationDTO[];
  cash_valuations: CashValuationDTO[];
  source_manifest: Record<string, unknown>;
  calculation_version: string;
  created_at: string;
}

export interface ReconciliationDTO {
  portfolio_id: string;
  status: ReconciliationStatus;
  reconciliation_timestamp: string;
  total_transactions_checked: number;
  total_lots_checked: number;
  total_positions_checked: number;
  total_cash_entries_checked: number;
  discrepancies: string[];
  warnings: string[];
  is_balanced: boolean;
}

export interface CreatePortfolioPayload {
  name: string;
  base_currency?: string;
  portfolio_type?: PortfolioType;
  description?: string;
}

export interface CreateAccountPayload {
  account_name: string;
  account_type?: AccountType;
  primary_currency?: string;
  custodian_name?: string;
  account_number_mask?: string;
}

export interface CreateTransactionPayload {
  account_id: string;
  transaction_type: TransactionType;
  cash_currency?: string;
  trade_date?: string;
  settlement_date?: string;
  instrument_id?: string;
  symbol?: string;
  exchange?: string;
  company_name?: string;
  quantity?: number;
  unit_price?: number;
  gross_amount?: number;
  fee?: number;
  tax?: number;
  idempotency_key?: string;
  notes?: string;
}

export interface CorrectTransactionPayload {
  replacement: CreateTransactionPayload;
  reason: string;
}

