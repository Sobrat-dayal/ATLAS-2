"use client";

import React, { useState } from "react";
import { Search, Filter, History, X } from "lucide-react";
import { RetrievalStrategy } from "@/lib/ai/research/types";

interface AiResearchSearchProps {
  onSearch: (params: {
    query: string;
    symbols?: string[];
    documentTypes?: string[];
    historicalAsOf?: string;
    strategy: RetrievalStrategy;
  }) => void;
  isLoading?: boolean;
}

export function AiResearchSearch({ onSearch, isLoading = false }: AiResearchSearchProps) {
  const [query, setQuery] = useState("");
  const [symbol, setSymbol] = useState("");
  const [historicalAsOf, setHistoricalAsOf] = useState("");
  const [docType, setDocType] = useState<string>("ALL");
  const [showFilters, setShowFilters] = useState(false);
  const [strategy, setStrategy] = useState<RetrievalStrategy>("HYBRID_FUSION");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    onSearch({
      query: query.trim(),
      symbols: symbol.trim() ? [symbol.trim().toUpperCase()] : undefined,
      documentTypes: docType !== "ALL" ? [docType] : undefined,
      historicalAsOf: historicalAsOf ? `${historicalAsOf}T23:59:59Z` : undefined,
      strategy,
    });
  };

  const handleQuickPrompt = (prompt: string, sym?: string) => {
    setQuery(prompt);
    if (sym) setSymbol(sym);
    onSearch({
      query: prompt,
      symbols: sym ? [sym] : undefined,
      strategy,
    });
  };

  return (
    <div className="space-y-2.5">
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a grounded research question (e.g. 'What was TEST_COMPANY revenue growth?')..."
            className="w-full h-9 pl-9 pr-24 rounded-lg bg-atlas-surface-1 border border-atlas-border-default text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-hidden focus:border-atlas-accent/60 transition-all"
          />
          <Search className="absolute left-3 h-3.5 w-3.5 text-atlas-text-muted pointer-events-none" />

          <div className="absolute right-1.5 flex items-center gap-1">
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`p-1 rounded text-xs transition-colors ${
                showFilters || symbol || historicalAsOf || docType !== "ALL"
                  ? "bg-atlas-accent/20 text-atlas-accent"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
              title="Toggle Research Filters & Historical As-of"
            >
              <Filter className="h-3.5 w-3.5" />
            </button>

            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="h-6 px-2.5 rounded bg-atlas-accent hover:bg-atlas-accent/90 disabled:opacity-50 text-[11px] font-medium text-white transition-all shadow-xs"
            >
              {isLoading ? "Searching..." : "Research"}
            </button>
          </div>
        </div>

        {/* Expandable Filters & Historical Vintage */}
        {showFilters && (
          <div className="p-3 rounded-lg bg-atlas-surface-2 border border-atlas-border-default space-y-2.5 text-xs animate-in fade-in slide-in-from-top-1 duration-150">
            <div className="flex items-center justify-between text-[11px] text-atlas-text-muted font-medium pb-1.5 border-b border-atlas-border-default/60">
              <span className="flex items-center gap-1.5">
                <Filter className="h-3 w-3 text-atlas-accent" />
                Retrieval & Point-in-Time Filters
              </span>
              <button
                type="button"
                onClick={() => {
                  setSymbol("");
                  setHistoricalAsOf("");
                  setDocType("ALL");
                  setStrategy("HYBRID_FUSION");
                }}
                className="hover:text-atlas-text-primary"
              >
                Reset
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {/* Symbol */}
              <div className="space-y-1">
                <label className="text-[10px] text-atlas-text-muted uppercase tracking-wider block">
                  Symbol / Company
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="e.g. TEST_COMPANY, MSFT"
                  className="w-full h-7 px-2 rounded bg-atlas-surface-1 border border-atlas-border-default text-xs text-atlas-text-primary font-mono focus:outline-hidden"
                />
              </div>

              {/* Historical As-Of (Fixture C) */}
              <div className="space-y-1">
                <label className="text-[10px] text-atlas-text-muted uppercase tracking-wider block flex items-center gap-1">
                  <History className="h-2.5 w-2.5" />
                  Historical As-Of Date
                </label>
                <input
                  type="date"
                  value={historicalAsOf}
                  onChange={(e) => setHistoricalAsOf(e.target.value)}
                  className="w-full h-7 px-2 rounded bg-atlas-surface-1 border border-atlas-border-default text-xs text-atlas-text-primary font-mono focus:outline-hidden"
                />
              </div>

              {/* Document Type */}
              <div className="space-y-1">
                <label className="text-[10px] text-atlas-text-muted uppercase tracking-wider block">
                  Document Type
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full h-7 px-2 rounded bg-atlas-surface-1 border border-atlas-border-default text-xs text-atlas-text-primary focus:outline-hidden"
                >
                  <option value="ALL">All Documents</option>
                  <option value="10-K">Annual Report (10-K)</option>
                  <option value="10-Q">Quarterly Report (10-Q)</option>
                  <option value="CAPEX_PLAN">Capital Allocation Plan</option>
                  <option value="TRANSCRIPT">Earnings Call Transcript</option>
                  <option value="RESEARCH_REPORT">Equity Research Note</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </form>

      {/* Suggested Quick Questions */}
      <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-atlas-text-muted">
        <span>Suggested:</span>
        <button
          type="button"
          onClick={() => handleQuickPrompt("What was TEST_COMPANY's revenue growth?", "TEST_COMPANY")}
          className="px-2 py-0.5 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-default text-atlas-text-secondary hover:text-atlas-text-primary transition-colors font-mono text-[10px]"
        >
          TEST_COMPANY Revenue Growth
        </button>
        <button
          type="button"
          onClick={() => handleQuickPrompt("Compare planned capital expenditures between 2024 and 2025", "TEST_COMPANY")}
          className="px-2 py-0.5 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-default text-atlas-text-secondary hover:text-atlas-text-primary transition-colors font-mono text-[10px]"
        >
          CapEx Plan Comparison
        </button>
        <button
          type="button"
          onClick={() => handleQuickPrompt("Compare GAAP and Non-GAAP operating income", "TEST_COMPANY")}
          className="px-2 py-0.5 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-default text-atlas-text-secondary hover:text-atlas-text-primary transition-colors font-mono text-[10px]"
        >
          GAAP vs Non-GAAP Reconciliation
        </button>
      </div>
    </div>
  );
}

