"use client";

import React, { useEffect, useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import { listSources } from "@/lib/research/api";
import { ResearchSourceReference, ResearchSourceType } from "@/lib/research/types";

interface ResearchSourceLibraryProps {
  onAttachSourceToInvestigation?: (source: ResearchSourceReference) => void;
}

const SOURCE_TYPES: { label: string; value?: ResearchSourceType }[] = [
  { label: "All Source Types", value: undefined },
  { label: "Annual Report (10-K)", value: "ANNUAL_REPORT" },
  { label: "Quarterly Report (10-Q)", value: "QUARTERLY_REPORT" },
  { label: "Financial Statement Fact", value: "FINANCIAL_STATEMENT" },
  { label: "News Article", value: "NEWS_ARTICLE" },
  { label: "Economic Release", value: "ECONOMIC_RELEASE" },
  { label: "Market Dataset", value: "MARKET_DATASET" },
  { label: "Authorized External Reference", value: "AUTHORIZED_EXTERNAL_REFERENCE" },
];

export function ResearchSourceLibrary({ onAttachSourceToInvestigation }: ResearchSourceLibraryProps) {
  const [sources, setSources] = useState<ResearchSourceReference[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<ResearchSourceType | undefined>(undefined);
  const [selectedSource, setSelectedSource] = useState<ResearchSourceReference | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    listSources({
      source_type: selectedType,
      q: searchQuery || undefined,
    })
      .then((res) => {
        if (isMounted) {
          setSources(res.items);
          if (res.items.length > 0 && !selectedSource) {
            setSelectedSource(res.items[0]);
          }
        }
      })
      .catch((err) => console.error("Error fetching sources:", err))
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedType, searchQuery]);

  return (
    <div className="flex h-full flex-col p-4">
      {/* Header and Filter Controls */}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5 rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-2.5">
        <div className="flex flex-1 flex-wrap items-center gap-2">
          <div className="w-72">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search sources (e.g. Apple 10-K, CPI, Fed Rate)..."
              className="h-8 text-xs"
            />
          </div>

          <select
            value={selectedType || ""}
            onChange={(e) =>
              setSelectedType(e.target.value ? (e.target.value as ResearchSourceType) : undefined)
            }
            className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            {SOURCE_TYPES.map((t) => (
              <option key={t.label} value={t.value || ""}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div className="font-mono text-xs text-atlas-text-muted">
          {sources.length} canonical sources
        </div>
      </div>

      {/* Main Content: Table + Inspector */}
      <div className="flex flex-1 gap-3 overflow-hidden">
        {/* Source Table */}
        <div className="flex-1 overflow-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1">
          {isLoading ? (
            <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
              Loading verified research sources...
            </div>
          ) : sources.length === 0 ? (
            <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
              No research sources match the filter.
            </div>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 z-10 border-b border-atlas-border-default bg-atlas-surface-2 font-mono text-[11px] uppercase tracking-wider text-atlas-text-secondary">
                <tr>
                  <th className="px-3 py-2">Document Title & Publisher</th>
                  <th className="px-3 py-2">Source Type</th>
                  <th className="px-3 py-2">Entity</th>
                  <th className="px-3 py-2">Period / Vintage</th>
                  <th className="px-3 py-2">Published</th>
                  <th className="px-3 py-2 text-right">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default font-normal">
                {sources.map((src) => {
                  const isSelected = selectedSource?.source_reference_id === src.source_reference_id;
                  return (
                    <tr
                      key={src.source_reference_id}
                      onClick={() => setSelectedSource(src)}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-atlas-surface-hover border-l-2 border-l-atlas-accent"
                          : "hover:bg-atlas-surface-hover"
                      }`}
                    >
                      <td className="px-3 py-2.5">
                        <div className="font-semibold text-atlas-text-primary">{src.source_title}</div>
                        <div className="font-mono text-[11px] text-atlas-text-muted">
                          {src.publisher_id || src.provider_id}
                          {src.canonical_document_id && ` • Acc: ${src.canonical_document_id}`}
                        </div>
                      </td>

                      <td className="px-3 py-2.5 whitespace-nowrap">
                        <Badge variant="outline" className="font-mono text-[10px]">
                          {src.source_type.replace(/_/g, " ")}
                        </Badge>
                      </td>

                      <td className="px-3 py-2.5 whitespace-nowrap">
                        {src.canonical_entity_id ? (
                          <Badge variant="primary" className="font-mono text-[10px]">
                            {src.canonical_entity_id}
                          </Badge>
                        ) : (
                          <span className="text-atlas-text-muted">—</span>
                        )}
                      </td>

                      <td className="px-3 py-2.5 whitespace-nowrap font-mono text-[11px] text-atlas-text-secondary">
                        {src.reporting_period || "—"}
                      </td>

                      <td className="px-3 py-2.5 whitespace-nowrap font-mono text-[10px] text-atlas-text-muted">
                        {src.published_at
                          ? new Date(src.published_at).toLocaleDateString()
                          : "—"}
                      </td>

                      <td className="px-3 py-2.5 whitespace-nowrap text-right">
                        {src.source_url ? (
                          <a
                            href={src.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center gap-1 text-[11px] font-mono text-atlas-accent hover:underline"
                          >
                            Source ↗
                          </a>
                        ) : (
                          <span className="text-atlas-text-muted text-[10px]">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Source Inspector Sidebar */}
        <div className="w-80 overflow-y-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs">
          {selectedSource ? (
            <div className="space-y-3">
              <div>
                <span className="font-mono text-[10px] text-atlas-text-muted uppercase">Source Inspection</span>
                <h3 className="mt-0.5 text-xs font-bold text-atlas-text-primary">
                  {selectedSource.source_title}
                </h3>
              </div>

              <div className="space-y-1.5 rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-2.5 font-mono text-[11px]">
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Source ID:</span>
                  <span className="text-atlas-text-primary font-bold">{selectedSource.source_reference_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Type:</span>
                  <span className="text-atlas-text-primary">{selectedSource.source_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Provider:</span>
                  <span className="text-atlas-text-primary">{selectedSource.provider_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Publisher:</span>
                  <span className="text-atlas-text-primary">{selectedSource.publisher_id || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Period:</span>
                  <span className="text-atlas-text-primary">{selectedSource.reporting_period || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Revision:</span>
                  <span className="text-atlas-text-primary">{selectedSource.source_revision || "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Rights:</span>
                  <span className="text-atlas-positive">{selectedSource.rights_policy}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-atlas-text-muted">Availability:</span>
                  <Badge variant="positive" className="text-[9px]">
                    {selectedSource.availability_status}
                  </Badge>
                </div>
              </div>

              {selectedSource.provenance && Object.keys(selectedSource.provenance).length > 0 && (
                <div>
                  <span className="font-mono text-[10px] text-atlas-text-muted uppercase">Provenance Payload</span>
                  <pre className="mt-1 overflow-x-auto rounded-xs bg-atlas-surface-0 p-2 font-mono text-[10px] text-atlas-text-secondary">
                    {JSON.stringify(selectedSource.provenance, null, 2)}
                  </pre>
                </div>
              )}

              {selectedSource.source_url && (
                <div className="pt-2">
                  <a
                    href={selectedSource.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-center rounded-sm bg-atlas-surface-2 border border-atlas-border-default py-1.5 text-xs font-medium text-atlas-text-primary hover:bg-atlas-surface-hover"
                  >
                    Open Original Source Document ↗
                  </a>
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center text-center text-atlas-text-muted">
              Select a source to inspect metadata and provenance.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
