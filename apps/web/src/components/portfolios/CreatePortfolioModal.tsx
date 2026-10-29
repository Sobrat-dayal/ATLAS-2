"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { CreatePortfolioPayload, PortfolioType } from "@/lib/portfolios/types";
import { AlertCircle, Briefcase, X } from "lucide-react";

interface CreatePortfolioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CreatePortfolioPayload) => Promise<void>;
}

export function CreatePortfolioModal({
  isOpen,
  onClose,
  onSubmit,
}: CreatePortfolioModalProps) {
  const [name, setName] = useState("");
  const [baseCurrency, setBaseCurrency] = useState("USD");
  const [portfolioType, setPortfolioType] = useState<PortfolioType>("PERSONAL");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Please enter a valid portfolio name.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        name: name.trim(),
        base_currency: baseCurrency,
        portfolio_type: portfolioType,
        description: description.trim() || undefined,
      });
      setName("");
      setDescription("");
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
            <Briefcase className="h-4 w-4 text-atlas-accent" />
            <h2 className="text-sm font-bold uppercase tracking-wide text-atlas-text-primary">
              Create New Portfolio
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
              Portfolio Name *
            </label>
            <input
              type="text"
              placeholder="e.g. Global Tech High-Conviction"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Base Reporting Currency *
              </label>
              <select
                value={baseCurrency}
                onChange={(e) => setBaseCurrency(e.target.value)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="INR">INR (₹)</option>
                <option value="JPY">JPY (¥)</option>
                <option value="CAD">CAD ($)</option>
                <option value="AUD">AUD ($)</option>
                <option value="CHF">CHF (Fr)</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-medium text-atlas-text-secondary">
                Portfolio Classification
              </label>
              <select
                value={portfolioType}
                onChange={(e) => setPortfolioType(e.target.value as PortfolioType)}
                className="mt-1 h-8 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                <option value="PERSONAL">PERSONAL</option>
                <option value="MODEL_ACCOUNTING">MODEL ACCOUNTING</option>
                <option value="INSTITUTIONAL">INSTITUTIONAL</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-[11px] font-medium text-atlas-text-secondary">
              Description (Optional)
            </label>
            <textarea
              rows={2}
              placeholder="Investment mandate, benchmark notes, or thesis..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>

          <div className="mt-5 flex items-center justify-end gap-2 border-t border-atlas-border-default pt-3">
            <Button variant="ghost" size="sm" type="button" onClick={onClose} className="h-8 text-xs">
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={loading} className="h-8 text-xs">
              {loading ? "Creating..." : "Create Portfolio"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

