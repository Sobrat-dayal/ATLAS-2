"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { portfoliosApi } from "@/lib/portfolios/api";
import {
  formatCurrency,
  formatPrice,
  formatQuantity,
} from "@/lib/portfolios/formatting";
import {
  AccountDTO,
  CreateTransactionPayload,
  PortfolioDTO,
  TransactionPreviewDTO,
  TransactionType,
} from "@/lib/portfolios/types";
import { AlertCircle, Calculator, CheckCircle2, X } from "lucide-react";

interface AddTransactionModalProps {
  portfolio: PortfolioDTO;
  accounts: AccountDTO[];
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (payload: CreateTransactionPayload) => Promise<void>;
}

export function AddTransactionModal({
  portfolio,
  accounts,
  isOpen,
  onClose,
  onSuccess,
}: AddTransactionModalProps) {
  const [txType, setTxType] = useState<TransactionType>("BUY");
  const [accountId, setAccountId] = useState<string>(accounts[0]?.id || "");
  const [symbol, setSymbol] = useState("AAPL");
  const [exchange, setExchange] = useState("NASDAQ");
  const [quantity, setQuantity] = useState("10");
  const [unitPrice, setUnitPrice] = useState("150.00");
  const [grossAmount, setGrossAmount] = useState("1000.00");
  const [fee, setFee] = useState("0");
  const [tax, setTax] = useState("0");
  const [currency, setCurrency] = useState(portfolio.base_currency);
  const [notes, setNotes] = useState("");

  const [preview, setPreview] = useState<TransactionPreviewDTO | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [postLoading, setPostLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCalculatePreview = async () => {
    try {
      setPreviewLoading(true);
      setError(null);

      const payload: CreateTransactionPayload = {
        account_id: accountId || accounts[0]?.id,
        transaction_type: txType,
        cash_currency: currency,
        symbol: txType === "BUY" || txType === "SELL" || txType === "STOCK_SPLIT_ADJUSTMENT" ? symbol : undefined,
        exchange: txType === "BUY" || txType === "SELL" || txType === "STOCK_SPLIT_ADJUSTMENT" ? exchange : undefined,
        quantity: quantity ? parseFloat(quantity) : undefined,
        unit_price: unitPrice ? parseFloat(unitPrice) : undefined,
        gross_amount: grossAmount ? parseFloat(grossAmount) : undefined,
        fee: fee ? parseFloat(fee) : 0,
        tax: tax ? parseFloat(tax) : 0,
        notes: notes || undefined,
      };

      const res = await portfoliosApi.previewTransaction(portfolio.id, payload);
      setPreview(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setPreviewLoading(false);
    }
  };

  const handlePost = async () => {
    try {
      setPostLoading(true);
      setError(null);

      const payload: CreateTransactionPayload = {
        account_id: accountId || accounts[0]?.id,
        transaction_type: txType,
        cash_currency: currency,
        symbol: txType === "BUY" || txType === "SELL" || txType === "STOCK_SPLIT_ADJUSTMENT" ? symbol : undefined,
        exchange: txType === "BUY" || txType === "SELL" || txType === "STOCK_SPLIT_ADJUSTMENT" ? exchange : undefined,
        quantity: quantity ? parseFloat(quantity) : undefined,
        unit_price: unitPrice ? parseFloat(unitPrice) : undefined,
        gross_amount: grossAmount ? parseFloat(grossAmount) : undefined,
        fee: fee ? parseFloat(fee) : 0,
        tax: tax ? parseFloat(tax) : 0,
        notes: notes || undefined,
      };

      await onSuccess(payload);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setPostLoading(false);
    }
  };

  const isSecurityTx =
    txType === "BUY" || txType === "SELL" || txType === "STOCK_SPLIT_ADJUSTMENT";
  const isCashAmountTx =
    txType === "CASH_DEPOSIT" ||
    txType === "CASH_WITHDRAWAL" ||
    txType === "CASH_DIVIDEND" ||
    txType === "CASH_INTEREST" ||
    txType === "ACCOUNT_FEE" ||
    txType === "WITHHOLDING_TAX";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default pb-3">
          <div>
            <h2 className="text-sm font-bold text-atlas-text-primary uppercase tracking-wide">
              Record Transaction to Ledger
            </h2>
            <p className="text-xs text-atlas-text-muted">
              {portfolio.name} · {portfolio.base_currency} Base
            </p>
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

        <div className="mt-4 space-y-3">
          {/* Type & Account Row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Transaction Type
              </label>
              <select
                value={txType}
                onChange={(e) => {
                  setTxType(e.target.value as TransactionType);
                  setPreview(null);
                }}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                <option value="BUY">BUY Security</option>
                <option value="SELL">SELL Security</option>
                <option value="CASH_DEPOSIT">CASH DEPOSIT</option>
                <option value="CASH_WITHDRAWAL">CASH WITHDRAWAL</option>
                <option value="CASH_DIVIDEND">CASH DIVIDEND</option>
                <option value="CASH_INTEREST">CASH INTEREST</option>
                <option value="ACCOUNT_FEE">ACCOUNT FEE</option>
                <option value="STOCK_SPLIT_ADJUSTMENT">STOCK SPLIT</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Investment Account
              </label>
              <select
                value={accountId}
                onChange={(e) => {
                  setAccountId(e.target.value);
                  setPreview(null);
                }}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.account_name} ({a.primary_currency})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Security Fields if applicable */}
          {isSecurityTx && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  Symbol
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => {
                    setSymbol(e.target.value.toUpperCase());
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  Exchange
                </label>
                <input
                  type="text"
                  value={exchange}
                  onChange={(e) => {
                    setExchange(e.target.value.toUpperCase());
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Quantity & Price */}
          {isSecurityTx && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  {txType === "STOCK_SPLIT_ADJUSTMENT" ? "Current Holdings" : "Quantity (Shares)"}
                </label>
                <input
                  type="number"
                  step="any"
                  value={quantity}
                  onChange={(e) => {
                    setQuantity(e.target.value);
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  {txType === "STOCK_SPLIT_ADJUSTMENT" ? "Split Ratio (e.g. 2 for 2:1)" : "Unit Price"}
                </label>
                <input
                  type="number"
                  step="any"
                  value={unitPrice}
                  onChange={(e) => {
                    setUnitPrice(e.target.value);
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Gross Amount for cash transactions */}
          {isCashAmountTx && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  Cash Amount
                </label>
                <input
                  type="number"
                  step="any"
                  value={grossAmount}
                  onChange={(e) => {
                    setGrossAmount(e.target.value);
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-atlas-text-secondary">
                  Currency
                </label>
                <select
                  value={currency}
                  onChange={(e) => {
                    setCurrency(e.target.value);
                    setPreview(null);
                  }}
                  className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                  <option value="JPY">JPY</option>
                </select>
              </div>
            </div>
          )}

          {/* Fee & Tax */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Transaction Fee
              </label>
              <input
                type="number"
                step="any"
                value={fee}
                onChange={(e) => {
                  setFee(e.target.value);
                  setPreview(null);
                }}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Withholding / Tax
              </label>
              <input
                type="number"
                step="any"
                value={tax}
                onChange={(e) => {
                  setTax(e.target.value);
                  setPreview(null);
                }}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="text-[11px] font-medium text-atlas-text-secondary">
              Notes / Audit Memo
            </label>
            <input
              type="text"
              placeholder="e.g. Q4 rebalance, cash funding"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>
        </div>

        {/* Live Accounting Preview Box */}
        {preview && (
          <div className="mt-4 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs font-mono">
            <div className="flex items-center gap-1.5 font-sans font-bold text-atlas-text-primary">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              Simulated Accounting Preview
            </div>

            <div className="mt-2 grid grid-cols-2 gap-2 text-[11px]">
              <div>
                <span className="text-atlas-text-muted">Net Cash Effect: </span>
                <span
                  className={
                    parseFloat(preview.net_cash_amount) >= 0
                      ? "text-emerald-400 font-bold"
                      : "text-rose-400 font-bold"
                  }
                >
                  {formatCurrency(preview.net_cash_amount, currency)}
                </span>
              </div>

              <div>
                <span className="text-atlas-text-muted">Est. Resulting Cash: </span>
                <span className="text-atlas-text-primary font-bold">
                  {formatCurrency(preview.estimated_resulting_cash, currency)}
                </span>
              </div>

              {preview.resulting_quantity && (
                <div>
                  <span className="text-atlas-text-muted">Resulting Shares: </span>
                  <span className="text-atlas-text-primary">
                    {formatQuantity(preview.resulting_quantity)}
                  </span>
                </div>
              )}

              {preview.unit_cost_basis && (
                <div>
                  <span className="text-atlas-text-muted">Unit Cost Basis: </span>
                  <span className="text-atlas-text-primary">
                    {formatPrice(preview.unit_cost_basis, currency)}
                  </span>
                </div>
              )}

              {preview.estimated_realized_pnl && (
                <div>
                  <span className="text-atlas-text-muted">Realized P&L: </span>
                  <span
                    className={
                      parseFloat(preview.estimated_realized_pnl) >= 0
                        ? "text-emerald-400 font-bold"
                        : "text-rose-400 font-bold"
                    }
                  >
                    {formatCurrency(preview.estimated_realized_pnl, currency)}
                  </span>
                </div>
              )}
            </div>

            {preview.warnings.length > 0 && (
              <div className="mt-2 space-y-1 font-sans text-[11px] text-amber-400">
                {preview.warnings.map((w, i) => (
                  <div key={i} className="flex items-center gap-1">
                    <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                    <span>{w}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Buttons */}
        <div className="mt-5 flex items-center justify-between border-t border-atlas-border-default pt-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleCalculatePreview}
            disabled={previewLoading}
            className="h-8 gap-1.5 text-xs"
          >
            <Calculator className="h-3.5 w-3.5" />
            {previewLoading ? "Simulating..." : "Calculate Preview"}
          </Button>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={onClose} className="h-8 text-xs">
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handlePost}
              disabled={postLoading}
              className="h-8 text-xs"
            >
              {postLoading ? "Posting..." : "Confirm & Post to Ledger"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

