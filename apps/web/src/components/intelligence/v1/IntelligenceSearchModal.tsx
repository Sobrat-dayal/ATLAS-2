"use client";

import React, { useState, useEffect } from "react";
import { IntelligenceSearchResult } from "@/lib/intelligence/v1/types";
import { executeUnifiedSearch } from "@/lib/intelligence/v1/api";
import { Search, X, Building2, Radio, Database, ArrowRight, ShieldCheck } from "lucide-react";

interface IntelligenceSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectResult: (result: IntelligenceSearchResult) => void;
}

export function IntelligenceSearchModal({
  isOpen,
  onClose,
  onSelectResult
}: IntelligenceSearchModalProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<IntelligenceSearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      setResults([]);
      return;
    }
  }, [isOpen]);

  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      setLoading(true);
      executeUnifiedSearch(q, 10)
        .then((res) => setResults(res))
        .catch((err) => {
          console.error("Search failed:", err);
          setResults([]);
        })
        .finally(() => setLoading(false));
    }, 150);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/80 backdrop-blur-sm p-4 font-mono text-xs">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-2xl shadow-2xl flex flex-col overflow-hidden max-h-[80vh]">
        {/* Search Input Bar */}
        <div className="p-3 border-b border-zinc-800 bg-zinc-900/60 flex items-center gap-2">
          <Search className="w-4 h-4 text-sky-400 shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Events, Companies, Issuers, Central Banks, or Sources (e.g. AAPL, Fed, Earthquake)..."
            className="w-full bg-transparent text-zinc-100 placeholder-zinc-500 text-xs focus:outline-none"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="p-1 text-zinc-400 hover:text-zinc-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={onClose}
            className="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-[10px]"
          >
            ESC
          </button>
        </div>

        {/* Results List */}
        <div className="overflow-y-auto p-2 flex-1 divide-y divide-zinc-900">
          {loading && (
            <div className="p-6 text-center text-zinc-500">Searching canonical registries...</div>
          )}

          {!loading && query && results.length === 0 && (
            <div className="p-8 text-center text-zinc-500">
              No matching canonical entities or verified events found for &quot;{query}&quot;.
            </div>
          )}

          {!loading &&
            results.map((item) => (
              <div
                key={`${item.result_type}-${item.canonical_id}`}
                onClick={() => {
                  onSelectResult(item);
                  onClose();
                }}
                className="p-2.5 hover:bg-zinc-900/80 rounded cursor-pointer transition-colors flex items-center justify-between group"
              >
                <div className="flex items-start gap-2.5">
                  <div className="p-1.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 mt-0.5">
                    {item.result_type === "ENTITY" ? (
                      <Building2 className="w-3.5 h-3.5 text-sky-400" />
                    ) : item.result_type === "EVENT" ? (
                      <Radio className="w-3.5 h-3.5 text-blue-400" />
                    ) : (
                      <Database className="w-3.5 h-3.5 text-emerald-400" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5 font-medium text-zinc-100">
                      <span>{item.display_title}</span>
                      <span className="text-[10px] px-1 rounded bg-zinc-800 text-zinc-400 uppercase">
                        {item.entity_type || item.result_type}
                      </span>
                    </div>
                    <div className="text-[11px] text-zinc-400 mt-0.5">
                      {item.disambiguation}
                    </div>
                    {item.source_reference && (
                      <div className="text-[10px] text-zinc-500 mt-0.5">
                        Source: {item.source_reference}
                      </div>
                    )}
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-zinc-600 group-hover:text-sky-400 transition-colors" />
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

