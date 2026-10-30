"use client";

import React, { useState } from "react";
import {
  CreateOptimizationStudyRequestDTO,
  OptimizationObjective,
  OptimizationStudyDTO,
  UniverseAssetDTO,
} from "@/lib/portfolios/optimization/types";
import { Archive, CheckCircle, FolderOpen, Plus, Sparkles } from "lucide-react";

interface OptimizationStudyListProps {
  studies: OptimizationStudyDTO[];
  activeStudy: OptimizationStudyDTO | null;
  universe: UniverseAssetDTO[];
  onSelectStudy: (studyId: string) => Promise<void>;
  onCreateStudy: (req: CreateOptimizationStudyRequestDTO) => Promise<void>;
  onArchiveStudy: (studyId: string) => Promise<void>;
}

export function OptimizationStudyList({
  studies,
  activeStudy,
  universe,
  onSelectStudy,
  onCreateStudy,
  onArchiveStudy,
}: OptimizationStudyListProps) {
  const [showCreate, setShowCreate] = useState<boolean>(false);
  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [defaultObjective, setDefaultObjective] = useState<OptimizationObjective>("MINIMUM_VARIANCE");
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await onCreateStudy({
        name: name.trim(),
        description: description.trim() || undefined,
        default_objective: defaultObjective,
        universe_symbols: universe.map((u) => u.symbol),
      });
      setName("");
      setDescription("");
      setShowCreate(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create study.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Bar */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <FolderOpen className="h-4 w-4 text-atlas-accent" />
              <h3 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
                Optimization Research Studies
              </h3>
            </div>
            <p className="mt-0.5 text-xs text-atlas-text-muted">
              Organize multiple parameter setups, universe subsets, and investment mandates into named studies.
            </p>
          </div>

          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-atlas-surface-0 hover:bg-atlas-accent/90 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>{showCreate ? "Cancel" : "New Study"}</span>
          </button>
        </div>
      </div>

      {/* Create Study Form */}
      {showCreate && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
            Create Optimization Study
          </h4>

          {error && (
            <div className="mb-3 rounded bg-rose-500/10 p-2 text-xs text-rose-300">
              {error}
            </div>
          )}

          <form onSubmit={handleCreate} className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="text-[11px] text-atlas-text-muted">Study Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Core Multi-Asset Rebalance 2026"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-3 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-atlas-text-muted">Default Objective</label>
                <select
                  value={defaultObjective}
                  onChange={(e) => setDefaultObjective(e.target.value as OptimizationObjective)}
                  className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-3 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
                >
                  <option value="MINIMUM_VARIANCE">Minimum Variance</option>
                  <option value="MAXIMUM_SHARPE">Maximum Sharpe Ratio</option>
                  <option value="MEAN_VARIANCE_UTILITY">Mean-Variance Quadratic Utility</option>
                  <option value="RISK_PARITY">Equal Risk Contribution (Risk Parity)</option>
                  <option value="TARGET_RETURN_MIN_VARIANCE">Target Return Minimum Variance</option>
                  <option value="MAXIMUM_EXPECTED_RETURN">Maximum Expected Return</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] text-atlas-text-muted">Description (Optional)</label>
              <textarea
                rows={2}
                placeholder="Investment hypothesis, constraints rationale, or benchmark targets..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-3 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded border border-atlas-border-default/60 px-3 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !name.trim()}
                className="rounded bg-atlas-accent px-4 py-1 text-xs font-semibold text-atlas-surface-0 hover:bg-atlas-accent/90 disabled:opacity-50"
              >
                {submitting ? "Creating..." : "Create Study"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Studies List */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 overflow-hidden">
        {studies.length === 0 ? (
          <div className="p-8 text-center text-xs text-atlas-text-muted">
            No optimization studies created yet. Create a study to organize your optimization runs.
          </div>
        ) : (
          <div className="divide-y divide-atlas-border-default/40">
            {studies.map((s) => {
              const isSelected = activeStudy?.study_id === s.study_id;

              return (
                <div
                  key={s.study_id}
                  className={`flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between transition-colors ${
                    isSelected ? "bg-atlas-accent/5" : "hover:bg-atlas-surface-2/30"
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-atlas-text-primary text-sm">
                        {s.name}
                      </span>
                      {isSelected && (
                        <span className="flex items-center gap-1 rounded bg-cyan-500/10 px-2 py-0.5 text-[10px] font-bold text-cyan-300 border border-cyan-500/20">
                          <CheckCircle className="h-3 w-3" />
                          ACTIVE STUDY
                        </span>
                      )}
                      <span className="rounded bg-atlas-surface-2 px-2 py-0.5 text-[10px] font-mono text-atlas-text-muted">
                        {s.default_objective}
                      </span>
                    </div>
                    {s.description && (
                      <p className="text-xs text-atlas-text-secondary">{s.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-[11px] text-atlas-text-muted">
                      <span>Universe: {s.universe_symbols?.length || 0} assets</span>
                      <span>Currency: {s.base_currency}</span>
                      <span>Created: {new Date(s.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {!isSelected && (
                      <button
                        onClick={() => onSelectStudy(s.study_id)}
                        className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-3 py-1 text-xs font-medium text-atlas-text-secondary hover:border-atlas-accent hover:text-atlas-text-primary"
                      >
                        Select
                      </button>
                    )}
                    <button
                      onClick={() => onArchiveStudy(s.study_id)}
                      className="rounded p-1 text-atlas-text-muted hover:bg-rose-500/10 hover:text-rose-400"
                      title="Archive study"
                    >
                      <Archive className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
