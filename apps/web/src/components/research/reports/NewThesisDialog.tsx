"use client";

import React, { useState } from "react";
import { Button, Input } from "@/design-system";
import { CreateThesisDTO } from "@/lib/research/types";

interface NewThesisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateThesisDTO) => Promise<void>;
}

export function NewThesisDialog({ isOpen, onClose, onSubmit }: NewThesisDialogProps) {
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [targetEntityId, setTargetEntityId] = useState("");
  const [targetEntityName, setTargetEntityName] = useState("");
  const [horizonMonths, setHorizonMonths] = useState<number>(12);
  const [convictionScore, setConvictionScore] = useState<number>(75);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Thesis title is required.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({
        title: title.trim(),
        summary: summary.trim() || undefined,
        target_entity_id: targetEntityId.trim() || undefined,
        target_entity_name: targetEntityName.trim() || undefined,
        horizon_months: Number(horizonMonths) || 12,
        conviction_score: Number(convictionScore) / 100,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create investment thesis.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-xl overflow-hidden flex flex-col">
        <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-3">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              CREATE STRUCTURED INVESTMENT THESIS
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Define a core thesis with clear investment horizon, conviction scoring, and anchored argument architecture.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary text-sm font-mono"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="rounded-xs border border-atlas-negative/30 bg-atlas-negative/10 p-2 text-xs text-atlas-negative">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
              Thesis Title *
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Hyperscaler Cloud CapEx Expansion Drives Custom Silicon Leverage"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
              Executive Summary / Central Hypothesis
            </label>
            <textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              rows={3}
              placeholder="State the core mechanism of the investment opportunity and edge..."
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Target Entity Ticker / Identifier
              </label>
              <Input
                value={targetEntityId}
                onChange={(e) => setTargetEntityId(e.target.value)}
                placeholder="e.g. NVDA"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Target Entity Name
              </label>
              <Input
                value={targetEntityName}
                onChange={(e) => setTargetEntityName(e.target.value)}
                placeholder="e.g. NVIDIA Corporation"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Horizon (Months)
              </label>
              <Input
                type="number"
                min={1}
                max={60}
                value={horizonMonths}
                onChange={(e) => setHorizonMonths(Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Initial Conviction Score: {convictionScore}%
              </label>
              <input
                type="range"
                min={0}
                max={100}
                value={convictionScore}
                onChange={(e) => setConvictionScore(Number(e.target.value))}
                className="w-full h-2 bg-atlas-surface-2 rounded-lg appearance-none cursor-pointer mt-2"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default">
            <Button variant="secondary" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Thesis"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
