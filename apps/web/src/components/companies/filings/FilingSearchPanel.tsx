"use client";

import React, { useState } from "react";
import { FilingSearchHitDTO } from "@/lib/companies/filings";
import {
  Search,
  FileText,
  Clock,
  Calendar,
  ExternalLink,
  ChevronRight,
  AlertCircle,
} from "lucide-react";

interface FilingSearchPanelProps {
  onSearch: (query: string) => Promise<void>;
  searchHits: FilingSearchHitDTO[];
  isSearching: boolean;
  onSelectFiling: (filingId: string) => void;
}

export const FilingSearchPanel: React.FC<FilingSearchPanelProps> = ({
  onSearch,
  searchHits,
  isSearching,
  onSelectFiling,
}) => {
  const [query, setQuery] = useState<string>("");

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleSampleQuery = (sample: string) => {
    setQuery(sample);
    onSearch(sample);
  };

  const highlightSnippet = (snippet: string, term: string) => {
    if (!term.trim()) return snippet;
    const parts = snippet.split(new RegExp(`(${term})`, "gi"));
    return (
      <>
        {parts.map((part, i) =>
          part.toLowerCase() === term.toLowerCase() ? (
            <mark key={i} className="bg-primary/20 text-primary font-bold px-0.5 rounded">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </>
    );
  };

  return (
    <div className="space-y-4">
      {/* Search Header Form */}
      <form onSubmit={handleFormSubmit} className="space-y-2">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search full-text disclosures (e.g. Services revenue, supply chain, operating income, dividends)..."
            className="w-full pl-9 pr-24 py-2 text-xs rounded-lg bg-background border border-border focus:outline-none focus:ring-1 focus:ring-primary text-foreground placeholder:text-muted-foreground shadow-sm"
          />
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="absolute right-1.5 top-1.5 px-3 py-1 text-xs font-semibold rounded bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {isSearching ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Quick Sample Queries */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
          <span>Quick queries:</span>
          {[
            "Services revenue",
            "Cash and cash equivalents",
            "Gross margin",
            "Apple Intelligence",
            "Common stock",
          ].map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => handleSampleQuery(sample)}
              className="px-2 py-0.5 rounded bg-muted/60 hover:bg-muted text-foreground transition-colors cursor-pointer border border-border/40 font-mono text-[10px]"
            >
              {sample}
            </button>
          ))}
        </div>
      </form>

      {/* Results Header */}
      {query && (
        <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
          <span>Found {searchHits.length} verified disclosure matches</span>
          <span>Lexical & Section-Grounded Index</span>
        </div>
      )}

      {/* Results Cards List */}
      <div className="space-y-2.5">
        {searchHits.length > 0 ? (
          searchHits.map((hit, idx) => (
            <div
              key={`${hit.filing_id}-${idx}`}
              onClick={() => onSelectFiling(hit.filing_id)}
              className="p-3.5 rounded-lg border border-border/60 bg-card/40 hover:border-border hover:bg-card/70 transition-all cursor-pointer space-y-2"
            >
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-primary/10 text-primary border border-primary/20">
                    {hit.form_type}
                  </span>
                  <span className="font-mono text-muted-foreground text-[11px]">
                    Period: <span className="text-foreground font-semibold">{hit.reporting_period}</span>
                  </span>
                  <span className="font-mono text-muted-foreground text-[11px]">
                    Filed: {hit.filing_date}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-[11px] font-medium text-primary hover:underline">
                  <span>Inspect Document</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </div>
              </div>

              {hit.section_name && (
                <div className="text-[11px] font-mono text-muted-foreground flex items-center gap-1">
                  <FileText className="w-3 h-3 text-muted-foreground" />
                  <span>Section: {hit.section_name}</span>
                </div>
              )}

              <div className="p-2.5 rounded bg-background/80 border border-border/40 text-xs leading-relaxed text-foreground/90 font-mono">
                {highlightSnippet(hit.matched_snippet, query)}
              </div>

              <div className="text-[10px] font-mono text-muted-foreground flex items-center justify-between">
                <span>Accession: {hit.accession_number}</span>
                <span>Score: {hit.score.toFixed(2)}</span>
              </div>
            </div>
          ))
        ) : query && !isSearching ? (
          <div className="p-8 text-center rounded-lg border border-dashed border-border text-muted-foreground text-xs space-y-2">
            <AlertCircle className="w-5 h-5 mx-auto text-muted-foreground/80" />
            <p>No regulatory disclosure text matched &ldquo;{query}&rdquo;.</p>
            <p className="text-[11px]">
              Try broader search terms like &ldquo;revenue&rdquo;, &ldquo;operating&rdquo;, or &ldquo;cash&rdquo;.
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
};
