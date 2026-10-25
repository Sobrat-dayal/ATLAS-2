"use client";

import { Badge, Input } from "@/design-system";
import { CompanySearchResult } from "@/lib/companies/types";
import { Building2, ChevronRight, Loader2, Search, Tag } from "lucide-react";

export interface CompanyEmptyStateProps {
  query: string;
  onQueryChange: (q: string) => void;
  results: CompanySearchResult[];
  loading: boolean;
  total: number;
  onSelectCompany: (companyId: string) => void;
}

export function CompanyEmptyState({
  query,
  onQueryChange,
  results,
  loading,
  total,
  onSelectCompany,
}: CompanyEmptyStateProps) {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Hero Search Box */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-6 space-y-4">
        <div>
          <h2 className="text-lg font-bold text-atlas-text-primary tracking-tight">
            Canonical Company Intelligence Directory
          </h2>
          <p className="text-xs text-atlas-text-muted mt-1">
            Search canonical corporate entities by legal name, display name, verified alias, corporate identifier (LEI, CIK), or associated security symbol.
          </p>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
          <Input
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search by company name, legal name, CIK, LEI, or ticker (e.g. Apple, AAPL, Microsoft, MSFT)..."
            className="pl-9 text-xs"
            autoFocus
          />
        </div>
      </div>

      {/* Results / Catalog View */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
              Corporate Directory Results
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              {total} {total === 1 ? "Company" : "Companies"}
            </Badge>
          </div>
          {loading && (
            <div className="flex items-center gap-1.5 text-xs text-atlas-text-muted">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-atlas-accent" />
              <span>Searching directory...</span>
            </div>
          )}
        </div>

        {results.length > 0 ? (
          <div className="divide-y divide-atlas-border-subtle">
            {results.map((comp) => (
              <button
                type="button"
                key={comp.company_entity_id}
                onClick={() => onSelectCompany(comp.company_entity_id)}
                className="w-full p-4 hover:bg-atlas-surface-2/70 text-left transition-colors flex items-center justify-between gap-4 group focus:outline-none focus:bg-atlas-surface-2"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm font-bold text-atlas-text-primary group-hover:text-atlas-accent transition-colors">
                      {comp.display_name}
                    </span>
                    {comp.primary_ticker && (
                      <Badge variant="default" className="font-mono text-[10px]">
                        {comp.primary_ticker}
                      </Badge>
                    )}
                    {comp.status && (
                      <Badge
                        variant={comp.status === "active" ? "positive" : "default"}
                        className="text-[9px] uppercase font-mono"
                      >
                        {comp.status}
                      </Badge>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-atlas-text-muted">
                    {comp.legal_name && comp.legal_name !== comp.display_name && (
                      <span>
                        Legal: <span className="text-atlas-text-secondary">{comp.legal_name}</span>
                      </span>
                    )}

                    {comp.sector && (
                      <span className="inline-flex items-center gap-1">
                        <Tag className="w-3 h-3" />
                        <span>{comp.sector}</span>
                        {comp.industry && <span className="text-atlas-text-muted">· {comp.industry}</span>}
                      </span>
                    )}

                    {comp.country && <span>Country: {comp.country}</span>}
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-atlas-text-muted group-hover:text-atlas-text-primary transition-colors">
                  <span className="hidden sm:inline font-medium">Open Overview</span>
                  <ChevronRight className="w-4 h-4" />
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-xs text-atlas-text-muted">
            {loading ? (
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin text-atlas-accent" />
                <span>Searching canonical company registry...</span>
              </div>
            ) : query.trim() ? (
              <div className="space-y-1">
                <p className="font-semibold text-atlas-text-secondary">No companies match &quot;{query}&quot;</p>
                <p>Try searching by registered legal name, ticker symbol, or CIK.</p>
              </div>
            ) : (
              <p>Type a company name or ticker to discover canonical corporate intelligence profiles.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
