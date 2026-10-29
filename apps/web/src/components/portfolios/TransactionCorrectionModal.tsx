"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { formatCurrency, formatDate } from "@/lib/portfolios/formatting";
import {
  CorrectTransactionPayload,
  CreateTransactionPayload,
  TransactionDTO,
} from "@/lib/portfolios/types";
import { AlertCircle, Edit3, X } from "lucide-react";

interface TransactionCorrectionModalProps {
  targetTx: TransactionDTO | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (targetTxId: string, payload: CorrectTransactionPayload) => Promise<void>;
}

export function TransactionCorrectionModal({
  targetTx,
  isOpen,
  onClose,
  onSuccess,
}: TransactionCorrectionModalProps) {
  const [quantity, setQuantity] = useState(targetTx?.quantity || "10");
  const [unitPrice, setUnitPrice] = useState(targetTx?.unit_price || "100.00");
  const [fee, setFee] = useState(targetTx?.fee || "0");
  const [tax, setTax] = useState(targetTx?.tax || "0");
  const [reason, setReason] = useState("Execution price correction");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !targetTx) return null;

  const handleCorrect = async () => {
    if (!reason.trim()) {
      setError("Please provide an audit rationale for the correction.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const replacementPayload: CreateTransactionPayload = {
        account_id: targetTx.account_id,
        transaction_type: targetTx.transaction_type,
        cash_currency: targetTx.cash_currency,
        symbol: targetTx.symbol || undefined,
        exchange: targetTx.exchange || undefined,
        quantity: quantity ? parseFloat(quantity) : undefined,
        unit_price: unitPrice ? parseFloat(unitPrice) : undefined,
        gross_amount: targetTx.gross_amount ? parseFloat(targetTx.gross_amount) : undefined,
        fee: fee ? parseFloat(fee) : 0,
        tax: tax ? parseFloat(tax) : 0,
        notes: `Replacement for ${targetTx.id}: ${reason}`,
      };

      await onSuccess(targetTx.id, {
        replacement: replacementPayload,
        reason,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="relative w-full max-w-lg rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-atlas-border-default pb-3">
          <div className="flex items-center gap-2">
            <Edit3 className="h-4 w-4 text-atlas-accent" />
            <h2 className="text-sm font-bold text-atlas-text-primary uppercase tracking-wide">
              Controlled Transaction Correction
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

        {/* Original Transaction Summary */}
        <div className="mt-3 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs">
          <div className="text-[11px] font-semibold text-atlas-text-muted">
            Original Journal Entry (Will be marked REVERSED):
          </div>
          <div className="mt-1 flex items-center justify-between font-mono">
            <span>
              {targetTx.transaction_type} {targetTx.symbol || ""}
            </span>
            <span>{formatDate(targetTx.trade_date)}</span>
          </div>
          <div className="mt-1 flex items-center justify-between font-mono text-[11px] text-atlas-text-secondary">
            <span>
              {targetTx.quantity} shares @ {targetTx.unit_price}
            </span>
            <span>Net: {formatCurrency(targetTx.net_cash_amount, targetTx.cash_currency)}</span>
          </div>
        </div>

        {/* Replacement Fields */}
        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Corrected Quantity
              </label>
              <input
                type="number"
                step="any"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Corrected Unit Price
              </label>
              <input
                type="number"
                step="any"
                value={unitPrice}
                onChange={(e) => setUnitPrice(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Corrected Fee
              </label>
              <input
                type="number"
                step="any"
                value={fee}
                onChange={(e) => setFee(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Corrected Tax
              </label>
              <input
                type="number"
                step="any"
                value={tax}
                onChange={(e) => setTax(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 font-mono text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] font-medium text-atlas-text-secondary">
              Correction Audit Rationale (Mandatory)
            </label>
            <input
              type="text"
              placeholder="Explain why this entry is being restated..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>
        </div>

        <div className="mt-5 flex items-center justify-end gap-2 border-t border-atlas-border-default pt-3">
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 text-xs">
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleCorrect}
            disabled={loading}
            className="h-8 text-xs"
          >
            {loading ? "Correcting..." : "Apply Controlled Correction"}
          </Button>
        </div>
      </div>
    </div>
  );
}

