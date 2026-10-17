"use client";

/**
 * Indicator Picker Dialog Component (Stage 69).
 *
 * Allows users to discover and select registered technical indicators from
 * the allowlisted catalog to add to the active chart.
 */

import React, { useState } from "react";
import { Check, Search, TrendingUp, X } from "lucide-react";
import { IndicatorDefinition } from "@/lib/charts";

export interface IndicatorPickerProps {
  isOpen: boolean;
  onClose: () => void;
  catalog: IndicatorDefinition[];
  isLoading?: boolean;
  onAddIndicator?: (indicatorId: string) => void;
  onSelect?: (indicatorId: string) => void;
  activeCount?: number;
}

export function IndicatorPicker({
  isOpen,
  onClose,
  catalog,
  isLoading = false,
  onAddIndicator,
  onSelect,
  activeCount = 0,
}: IndicatorPickerProps) {
  const handleSelect = (id: string) => {
    if (onSelect) {
      onSelect(id);
    } else if (onAddIndicator) {
      onAddIndicator(id);
    }
  };
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(
    catalog.length > 0 ? catalog[0].indicator_id : null
  );

  if (!isOpen) return null;

  const filtered = catalog.filter((ind) => {
    if (!search.trim()) return true;
    const q = search.trim().toLowerCase();
    return (
      ind.display_name.toLowerCase().includes(q) ||
      ind.indicator_id.toLowerCase().includes(q) ||
      ind.category.toLowerCase().includes(q) ||
      ind.description.toLowerCase().includes(q)
    );
  });

  const selectedDef = catalog.find((ind) => ind.indicator_id === (selectedId || (filtered[0]?.indicator_id)));

  const handleAdd = () => {
    if (selectedDef) {
      handleSelect(selectedDef.indicator_id);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div
        className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl flex flex-col overflow-hidden text-zinc-100 font-sans"
        role="dialog"
        aria-modal="true"
        aria-label="Technical Indicators Catalog"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/80 bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100 font-mono">
              TECHNICAL INDICATORS
            </h2>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">
              {catalog.length} Available
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-100 p-1 rounded hover:bg-zinc-800 transition-colors"
            aria-label="Close indicator picker"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="p-3 border-b border-zinc-800 bg-zinc-950">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-zinc-500" />
            <input
              type="text"
              placeholder="Search indicators by name, category, or description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 font-sans"
              autoFocus
            />
          </div>
        </div>

        {/* Body Split */}
        <div className="grid grid-cols-1 md:grid-cols-2 min-h-[300px] max-h-[420px] overflow-hidden">
          {/* Left: List */}
          <div className="border-r border-zinc-800/80 overflow-y-auto p-2 space-y-1">
            {isLoading ? (
              <div className="p-6 text-center text-xs text-zinc-500 font-mono">
                Loading approved indicator registry...
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-6 text-center text-xs text-zinc-500 font-mono">
                No indicators match search query.
              </div>
            ) : (
              filtered.map((ind) => {
                const isSelected = (selectedDef?.indicator_id === ind.indicator_id);
                return (
                  <button
                    key={ind.indicator_id}
                    type="button"
                    onClick={() => setSelectedId(ind.indicator_id)}
                    className={`w-full text-left px-3 py-2 rounded text-xs transition-colors flex items-center justify-between ${
                      isSelected
                        ? "bg-cyan-500/10 border border-cyan-500/30 text-cyan-200"
                        : "hover:bg-zinc-900 border border-transparent text-zinc-300"
                    }`}
                  >
                    <div>
                      <div className="font-medium">{ind.display_name}</div>
                      <div className="text-[10px] text-zinc-500 font-mono flex items-center gap-2 mt-0.5">
                        <span className="text-cyan-400">{ind.category}</span>
                        <span>•</span>
                        <span>{ind.rendering_target.replace("_", " ")}</span>
                      </div>
                    </div>
                    {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                  </button>
                );
              })
            )}
          </div>

          {/* Right: Selected Detail */}
          <div className="p-4 bg-zinc-950/60 overflow-y-auto flex flex-col justify-between">
            {selectedDef ? (
              <div className="space-y-4 text-xs">
                <div>
                  <h3 className="font-semibold text-sm text-zinc-100">
                    {selectedDef.display_name}
                  </h3>
                  <div className="text-[11px] font-mono text-zinc-500 mt-0.5">
                    {selectedDef.indicator_id} (v{selectedDef.version})
                  </div>
                </div>

                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-400 font-semibold mb-1">
                    Description
                  </div>
                  <p className="text-zinc-300 leading-relaxed">
                    {selectedDef.description}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-zinc-800/80">
                  <div>
                    <span className="text-[10px] font-mono text-zinc-500">Inputs:</span>
                    <div className="text-zinc-300 font-mono mt-0.5 uppercase">
                      {selectedDef.input_requirements.join(", ")}
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-zinc-500">Target:</span>
                    <div className="text-zinc-300 font-mono mt-0.5">
                      {selectedDef.rendering_target === "PRICE_OVERLAY" ? "Price Overlay" : "Subpane"}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-400 font-semibold mb-1.5">
                    Default Parameters
                  </div>
                  <div className="space-y-1">
                    {selectedDef.parameters.map((p) => (
                      <div
                        key={p.name}
                        className="flex items-center justify-between px-2 py-1 bg-zinc-900 border border-zinc-800/80 rounded text-[11px] font-mono"
                      >
                        <span className="text-zinc-400">{p.name}</span>
                        <span className="text-cyan-400 font-semibold">{String(p.default)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-zinc-500 text-center py-10 font-mono">
                Select an indicator to inspect specification.
              </div>
            )}

            {/* Action footer */}
            <div className="pt-4 border-t border-zinc-800 flex items-center justify-between mt-4">
              <span className="text-[11px] text-zinc-500 font-mono">
                Active: {activeCount}/5
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded text-xs text-zinc-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAdd}
                  disabled={!selectedDef || activeCount >= 5}
                  className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded text-xs font-medium font-mono transition-colors flex items-center gap-1.5"
                >
                  <span>Add to Chart</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
