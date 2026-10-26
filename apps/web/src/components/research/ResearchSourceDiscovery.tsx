"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import {
  ResearchSearchHit,
  ResearchSourceDiscoveryQuery,
  ResearchSourceType,
  ResearchSourceTypeItem,
  SearchMode,
} from "@/lib/research/types";

interface ResearchSourceDiscoveryProps {
  query: ResearchSourceDiscoveryQuery;
  results: ResearchSearchHit[];
  totalMatches: number;
  isLoading: boolean;
  sourceTypes: ResearchSourceTypeItem[];
  onSearch: (q: Partial<ResearchSourceDiscoveryQuery>) => void;
  onOpenDocument: (documentId: string) => void;
  onCompareDocument: (documentId: string) => void;
  onLinkToInvestigation?: (sourceReferenceId: string) => void;
}

const FILING_TYPES = [
  { label: "All Filings", value: "" },
  { label: "Form 10-K (Annual)", value: "10-K" },
  { label: "Form 10-Q (Quarterly)", value: "10-Q" },
  { label: "Form 8-K (Current)", value: "8-K" },
  { label: "CPI Economic Release", value: "CPI" },
  { label: "FOMC Rate Decision", value: "FED_DECISION" },
];

const QUICK_ENTITIES = [
  { label: "All Entities", value: "" },
  { label: "Apple (AAPL)", value: "AAPL" },
  { label: "Microsoft (MSFT)", value: "MSFT" },
  { label: "BLS (Macro)", value: "BLS" },
  { label: "Federal Reserve", value: "FED" },
];

export function ResearchSourceDiscovery({
  query,
  results,
  totalMatches,
  isLoading,
  sourceTypes,
  onSearch,
  onOpenDocument,
  onCompareDocument,
  onLinkToInvestigation,
}: ResearchSourceDiscoveryProps) {
  const [textQuery, setTextQuery] = useState(query.text_query || "");
  const [selectedEntity, setSelectedEntity] = useState(query.entity_ids?.[0] || "");
  const [selectedFilingType, setSelectedFilingType] = useState(query.filing_types?.[0] || "");
  const [selectedSourceType, setSelectedSourceType] = useState(query.source_type_ids?.[0] || "");
  const [searchMode, setSearchMode] = useState<SearchMode>(query.search_mode || "HYBRID");

  const handleExecuteSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    onSearch({
      text_query: textQuery,
      entity_ids: selectedEntity ? [selectedEntity] : [],
      filing_types: selectedFilingType ? [selectedFilingType] : [],
      source_type_ids: selectedSourceType ? [selectedSourceType as ResearchSourceType] : [],
      search_mode: searchMode,
    });
  };

  const handleClear = () => {
    setTextQuery("");
    setSelectedEntity("");
    setSelectedFilingType("");
    setSelectedSourceType("");
    setSearchMode("HYBRID");
    onSearch({
      text_query: "",
      entity_ids: [],
      filing_types: [],
      source_type_ids: [],
      search_mode: "HYBRID",
    });
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0 p-4">
      {/* Search Header Banner */}
      <div className="mb-3 shrink-0 rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
        <div className="mb-2.5 flex items-center justify-between">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Institutional Source Discovery & Regulatory Retrieval
            </h2>
            <p className="text-[11px] text-atlas-text-muted">
              Multi-facet indexed search across SEC EDGAR filings, official BLS releases, and central bank records.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-atlas-text-muted">Search Mode:</span>
            <div className="flex rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-0.5">
              {(["HYBRID", "KEYWORD", "SEMANTIC"] as SearchMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setSearchMode(mode)}
                  className={`rounded-xs px-2 py-0.5 text-[10px] font-medium transition-colors ${
                    searchMode === mode
                      ? "bg-atlas-accent text-white"
                      : "text-atlas-text-secondary hover:text-atlas-text-primary"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Search Input Bar */}
        <form onSubmit={handleExecuteSearch} className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <Input
                value={textQuery}
                onChange={(e) => setTextQuery(e.target.value)}
                placeholder="Search across documents, sections, and financial statements (e.g. 'iPhone revenue', 'operating margin', 'inflation')..."
                className="h-8 text-xs font-mono"
              />
            </div>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={isLoading}
              className="h-8 px-4 text-xs font-semibold"
            >
              {isLoading ? "Searching..." : "Search Sources"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleClear}
              className="h-8 px-3 text-xs"
            >
              Reset
            </Button>
          </div>

          {/* Facets & Filters */}
          <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-atlas-border-default/60">
            {/* Entity Filter */}
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-bold text-atlas-text-muted">Entity:</span>
              <select
                value={selectedEntity}
                onChange={(e) => setSelectedEntity(e.target.value)}
                className="h-7 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {QUICK_ENTITIES.map((ent) => (
                  <option key={ent.label} value={ent.value}>
                    {ent.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Filing Type Filter */}
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-bold text-atlas-text-muted">Filing Type:</span>
              <select
                value={selectedFilingType}
                onChange={(e) => setSelectedFilingType(e.target.value)}
                className="h-7 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {FILING_TYPES.map((f) => (
                  <option key={f.label} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Source Type Filter */}
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-bold text-atlas-text-muted">Source Type:</span>
              <select
                value={selectedSourceType}
                onChange={(e) => setSelectedSourceType(e.target.value)}
                className="h-7 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                <option value="">All Source Types</option>
                {sourceTypes.map((st) => (
                  <option key={st.source_type} value={st.source_type}>
                    {st.display_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="ml-auto text-[11px] font-mono text-atlas-text-muted">
              {isLoading ? "Executing search query..." : `${totalMatches} sources indexed`}
            </div>
          </div>
        </form>
      </div>

      {/* Results List */}
      <div className="flex-1 overflow-y-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1">
        {results.length === 0 ? (
          <div className="flex h-64 flex-col items-center justify-center p-6 text-center">
            <span className="mb-2 font-mono text-sm text-atlas-text-muted">
              {isLoading ? "Executing multi-facet source retrieval..." : "No research sources matched criteria"}
            </span>
            <p className="max-w-md text-xs text-atlas-text-secondary">
              Try broadening your query, removing entity filters, or querying broad canonical terms such as &quot;10-K&quot;, &quot;Apple&quot;, or &quot;CPI&quot;.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-atlas-border-default">
            {results.map((hit) => {
              const scorePct = Math.min(100, Math.round(hit.score * 100));
              const firstSpan = hit.matched_spans && hit.matched_spans.length > 0 ? hit.matched_spans[0] : null;

              return (
                <div
                  key={`${hit.source_reference_id}-${hit.canonical_document_id || hit.source_title}`}
                  className="p-3.5 transition-colors hover:bg-atlas-surface-2"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="flex-1">
                      {/* Top Badges */}
                      <div className="mb-1 flex flex-wrap items-center gap-1.5">
                        <Badge variant="primary" className="font-mono text-[10px]">
                          {hit.source_type}
                        </Badge>
                        {hit.canonical_entity_id && (
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {hit.canonical_entity_id}
                          </Badge>
                        )}
                        {hit.reporting_period && (
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {hit.reporting_period}
                          </Badge>
                        )}
                        <span className="text-[10px] font-mono text-atlas-text-muted">
                          Pub: {hit.publisher_id || "EDGAR"} • {hit.published_at?.split("T")[0] || "—"}
                        </span>
                      </div>

                      {/* Title */}
                      <h3 className="text-sm font-semibold text-atlas-text-primary">
                        {hit.source_title}
                      </h3>

                      {/* Location / Section */}
                      {firstSpan?.section_heading && (
                        <p className="mt-0.5 text-[11px] font-medium text-atlas-accent">
                          Section: {firstSpan.section_heading}
                        </p>
                      )}

                      {/* Matched Snippet */}
                      {hit.matched_snippet && (
                        <div className="mt-1.5 rounded-xs border border-atlas-border-default/40 bg-atlas-surface-0/70 p-2 font-mono text-xs leading-relaxed text-atlas-text-secondary">
                          <span className="text-atlas-text-muted mr-1.5">[Snippet]</span>
                          {hit.matched_snippet}
                        </div>
                      )}

                      {/* Canonical accession and location refs */}
                      <div className="mt-2 flex flex-wrap items-center gap-3 text-[10px] font-mono text-atlas-text-muted">
                        <span>Source ID: {hit.source_reference_id}</span>
                        {hit.canonical_document_id && (
                          <span>Accession: {hit.canonical_document_id}</span>
                        )}
                      </div>
                    </div>

                    {/* Right column: Score bar & Actions */}
                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-mono text-atlas-text-muted">Relevance:</span>
                        <div className="w-16 h-1.5 rounded-full bg-atlas-surface-3 overflow-hidden">
                          <div
                            className="h-full bg-atlas-accent"
                            style={{ width: `${scorePct}%` }}
                          />
                        </div>
                        <span className="font-mono text-[10px] font-bold text-atlas-text-primary">
                          {scorePct}%
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() =>
                            onOpenDocument(hit.canonical_document_id || hit.source_reference_id)
                          }
                          className="h-7 text-xs font-medium"
                        >
                          View Document & Tables
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() =>
                            onCompareDocument(hit.canonical_document_id || hit.source_reference_id)
                          }
                          className="h-7 text-xs font-medium"
                        >
                          Compare
                        </Button>
                        {onLinkToInvestigation && (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => onLinkToInvestigation(hit.source_reference_id)}
                            className="h-7 text-xs font-medium"
                          >
                            + Link
                          </Button>
                        )}
                      </div>
                    </div>
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
