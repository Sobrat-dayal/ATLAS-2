"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import {
  DocumentSearchHit,
  ResearchDocumentOutline,
  ResearchDocumentProcessingStatus,
  ResearchDocumentSection,
  ResearchDocumentTable,
  ResearchEvidenceCandidate,
  ResearchInvestigation,
  ResearchSourceReference,
} from "@/lib/research/types";
import { getDocumentProcessingStatusDisplay } from "@/lib/research/formatting";

interface ResearchDocumentViewerProps {
  documentId: string;
  document: ResearchSourceReference | null;
  processingStatus: ResearchDocumentProcessingStatus | null;
  outline: ResearchDocumentOutline | null;
  activeSectionId: string | null;
  activeSection: ResearchDocumentSection | null;
  tables: ResearchDocumentTable[];
  searchQuery: string;
  searchHits: DocumentSearchHit[];
  isSearching: boolean;
  candidates: ResearchEvidenceCandidate[];
  isLoading: boolean;
  investigations: ResearchInvestigation[];
  onSelectSection: (sectionId: string) => void;
  onSearchInDocument: (query: string, sectionId?: string) => void;
  onConvertCandidate: (candidateId: string, investigationId: string) => Promise<any>;
  onCompareWithAnother: (docId: string) => void;
}

export function ResearchDocumentViewer({
  documentId,
  document,
  processingStatus,
  outline,
  activeSectionId,
  activeSection,
  tables,
  searchQuery,
  searchHits,
  isSearching,
  candidates,
  isLoading,
  investigations,
  onSelectSection,
  onSearchInDocument,
  onConvertCandidate,
  onCompareWithAnother,
}: ResearchDocumentViewerProps) {
  const [leftTab, setLeftTab] = useState<"OUTLINE" | "SEARCH">("OUTLINE");
  const [centerMode, setCenterMode] = useState<"TEXT" | "TABLES">("TEXT");
  const [selectedTableIndex, setSelectedTableIndex] = useState<number>(0);
  const [localSearchInput, setLocalSearchInput] = useState<string>(searchQuery);
  const [convertingCandId, setConvertingCandId] = useState<string | null>(null);
  const [selectedTargetInvId, setSelectedTargetInvId] = useState<string>(
    investigations.length > 0 ? investigations[0].investigation_id : ""
  );

  const statusDisplay = getDocumentProcessingStatusDisplay(
    processingStatus?.processing_status || "COMPLETED"
  );

  const activeTable = tables.length > selectedTableIndex ? tables[selectedTableIndex] : null;

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchInDocument(localSearchInput);
    setLeftTab("SEARCH");
  };

  const handlePromoteCandidate = async (candidateId: string) => {
    if (!selectedTargetInvId) return;
    setConvertingCandId(candidateId);
    try {
      await onConvertCandidate(candidateId, selectedTargetInvId);
    } finally {
      setConvertingCandId(null);
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Top Document Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5 shrink-0">
        <div className="flex flex-wrap items-center gap-2.5">
          <Badge variant="outline" className="font-mono text-[10px] font-bold">
            {document?.canonical_document_id || documentId}
          </Badge>
          <h2 className="text-sm font-bold text-atlas-text-primary">
            {document?.source_title || outline?.document_title || "Research Document Intelligence"}
          </h2>
          {document?.canonical_entity_id && (
            <Badge variant="primary" className="font-mono text-[10px]">
              {document.canonical_entity_id}
            </Badge>
          )}
          {document?.reporting_period && (
            <Badge variant="outline" className="font-mono text-[10px]">
              {document.reporting_period}
            </Badge>
          )}
          <Badge variant={statusDisplay.variant} className="text-[10px]">
            {statusDisplay.label}
          </Badge>
          {document?.source_revision && (
            <span className="text-[10px] font-mono text-atlas-text-muted">
              Rev: {document.source_revision}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Mode Switcher */}
          <div className="flex rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-0.5">
            <button
              onClick={() => setCenterMode("TEXT")}
              className={`rounded-xs px-2.5 py-1 text-xs font-medium transition-colors ${
                centerMode === "TEXT"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Document Content
            </button>
            <button
              onClick={() => setCenterMode("TABLES")}
              className={`rounded-xs px-2.5 py-1 text-xs font-medium transition-colors ${
                centerMode === "TABLES"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Financial Tables ({tables.length})
            </button>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => onCompareWithAnother(documentId)}
            className="h-7 text-xs font-medium"
          >
            Compare vs Prior Period
          </Button>
        </div>
      </div>

      {/* 3-Pane Reader Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Pane: Outline Tree & In-Doc Search */}
        <div className="flex w-72 flex-col border-r border-atlas-border-default bg-atlas-surface-1 shrink-0 overflow-hidden">
          {/* Left Pane Navigation Header */}
          <div className="flex border-b border-atlas-border-default p-1 bg-atlas-surface-0">
            <button
              onClick={() => setLeftTab("OUTLINE")}
              className={`flex-1 py-1 text-xs font-semibold rounded-xs transition-colors ${
                leftTab === "OUTLINE"
                  ? "bg-atlas-surface-2 text-atlas-text-primary"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Outline ({outline?.sections?.length || 0})
            </button>
            <button
              onClick={() => setLeftTab("SEARCH")}
              className={`flex-1 py-1 text-xs font-semibold rounded-xs transition-colors ${
                leftTab === "SEARCH"
                  ? "bg-atlas-surface-2 text-atlas-text-primary"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              In-Doc Search ({searchHits.length})
            </button>
          </div>

          {/* Left Pane Content */}
          <div className="flex-1 overflow-y-auto p-2">
            {leftTab === "OUTLINE" ? (
              <div className="space-y-1">
                {!outline || !outline.sections || outline.sections.length === 0 ? (
                  <p className="p-3 text-xs text-atlas-text-muted">
                    {isLoading ? "Generating document outline..." : "No sections parsed."}
                  </p>
                ) : (
                  outline.sections.map((sec) => {
                    const isSelected = sec.section_id === activeSectionId;
                    return (
                      <button
                        key={sec.section_id}
                        onClick={() => onSelectSection(sec.section_id)}
                        className={`w-full text-left rounded-xs p-2 text-xs transition-colors ${
                          isSelected
                            ? "bg-atlas-accent/15 border-l-2 border-atlas-accent text-atlas-text-primary font-medium"
                            : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted mb-0.5">
                          <span className="font-mono truncate">{sec.section_path || "Section"}</span>
                          {sec.page_number && <span>p. {sec.page_number}</span>}
                        </div>
                        <div className="line-clamp-2 leading-snug">{sec.heading}</div>
                      </button>
                    );
                  })
                )}
              </div>
            ) : (
              <div className="flex flex-col h-full">
                <form onSubmit={handleSearchSubmit} className="mb-2">
                  <Input
                    value={localSearchInput}
                    onChange={(e) => setLocalSearchInput(e.target.value)}
                    placeholder="Search in document..."
                    className="h-7 text-xs font-mono"
                  />
                </form>

                <div className="flex-1 overflow-y-auto space-y-1.5">
                  {isSearching ? (
                    <div className="p-3 text-xs text-atlas-text-muted font-mono">
                      Searching document text spans...
                    </div>
                  ) : searchHits.length === 0 ? (
                    <div className="p-3 text-center text-xs text-atlas-text-muted">
                      {localSearchInput ? "No matching text spans found." : "Enter a search term above."}
                    </div>
                  ) : (
                    searchHits.map((hit, idx) => (
                      <div
                        key={`${hit.span_id}-${idx}`}
                        className="rounded-xs border border-atlas-border-default/60 bg-atlas-surface-0 p-2 text-xs"
                      >
                        {hit.section_heading && (
                          <div className="text-[10px] font-bold text-atlas-accent mb-1 truncate">
                            {hit.section_heading}
                          </div>
                        )}
                        <p className="font-mono text-[11px] leading-relaxed text-atlas-text-secondary">
                          {hit.snippet}
                        </p>
                        <div className="mt-1 flex items-center justify-between text-[10px] text-atlas-text-muted">
                          <span>Span: {hit.match_start}–{hit.match_end}</span>
                          {hit.section_id && (
                            <button
                              onClick={() => onSelectSection(hit.section_id!)}
                              className="text-atlas-accent hover:underline"
                            >
                              Jump to Section →
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Center Pane: Document Reader or Financial Table */}
        <div className="flex flex-1 flex-col overflow-hidden bg-atlas-surface-0">
          {centerMode === "TEXT" ? (
            <div className="flex-1 overflow-y-auto p-6 max-w-4xl mx-auto w-full">
              {activeSection ? (
                <div>
                  {/* Section Heading Header */}
                  <div className="mb-4 pb-3 border-b border-atlas-border-default">
                    <div className="flex items-center gap-2 text-xs font-mono text-atlas-text-muted mb-1">
                      <span className="font-bold text-atlas-accent">
                        {activeSection.section_path || "Section"}
                      </span>
                      {activeSection.page_number && (
                        <span>Page {activeSection.page_number}</span>
                      )}
                      <span>• Offsets: {activeSection.start_char_offset}–{activeSection.end_char_offset}</span>
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-atlas-text-primary">
                      {activeSection.heading}
                    </h1>
                  </div>

                  {/* Section Text Reader */}
                  <div className="prose prose-invert max-w-none text-xs leading-relaxed text-atlas-text-primary space-y-3 font-mono selection:bg-atlas-accent/30">
                    {activeSection.text_preview ? (
                      activeSection.text_preview.split("\n\n").map((p: string, pIdx: number) => (
                        <p key={pIdx} className="text-xs text-atlas-text-secondary">
                          <span className="text-atlas-text-muted/60 select-none mr-2 text-[10px]">
                            [{pIdx + 1}]
                          </span>
                          {p}
                        </p>
                      ))
                    ) : (
                      <p className="text-atlas-text-muted">No text preview available for this section.</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
                  {isLoading ? "Loading document section..." : "Select a section from the outline."}
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden p-4">
              {/* Table Selector Tabs */}
              {tables.length > 0 && (
                <div className="mb-3 flex items-center gap-2 overflow-x-auto border-b border-atlas-border-default pb-2">
                  {tables.map((tbl, idx) => (
                    <button
                      key={tbl.table_id}
                      onClick={() => setSelectedTableIndex(idx)}
                      className={`whitespace-nowrap rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                        selectedTableIndex === idx
                          ? "bg-atlas-accent text-white"
                          : "bg-atlas-surface-1 text-atlas-text-secondary hover:text-atlas-text-primary"
                      }`}
                    >
                      {tbl.title || `Table ${idx + 1}`}
                    </button>
                  ))}
                </div>
              )}

              {activeTable ? (
                <div className="flex-1 overflow-y-auto space-y-4">
                  {/* Table Header Details */}
                  <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-bold text-atlas-text-primary">
                          {activeTable.title}
                        </h3>
                        <p className="text-[11px] text-atlas-text-muted">
                          Period: {activeTable.period_label} • Table ID: {activeTable.table_id}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="font-mono text-[10px]">
                          Unit: {activeTable.unit_scale}
                        </Badge>
                        <Badge variant="outline" className="font-mono text-[10px]">
                          Currency: {activeTable.currency}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Financial Matrix Table */}
                  <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1">
                    <table className="w-full text-left text-xs">
                      <thead className="border-b border-atlas-border-default bg-atlas-surface-2 text-[11px] uppercase font-bold text-atlas-text-muted">
                        <tr>
                          <th className="p-2.5">Line Item / Concept</th>
                          {activeTable.headers.slice(1).map((h, hIdx) => (
                            <th key={hIdx} className="p-2.5 text-right font-mono">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-atlas-border-default/60">
                        {activeTable.row_labels.map((rowLabel, rIdx) => {
                          const cellRow = activeTable.cells[rIdx] || [];
                          return (
                            <tr key={rIdx} className="hover:bg-atlas-surface-2/60 transition-colors">
                              <td className="p-2.5 font-medium text-atlas-text-primary">
                                {rowLabel}
                              </td>
                              {cellRow.map((cellVal, cIdx) => (
                                <td
                                  key={cIdx}
                                  className="p-2.5 text-right font-mono text-atlas-text-secondary"
                                >
                                  {cellVal}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Footnotes */}
                  {activeTable.footnotes && activeTable.footnotes.length > 0 && (
                    <div className="rounded-xs border border-atlas-border-default/40 bg-atlas-surface-1/70 p-3 text-[11px] text-atlas-text-muted">
                      <div className="font-bold uppercase text-[10px] mb-1">Footnotes & Disclosures:</div>
                      <ul className="list-disc pl-4 space-y-0.5 font-mono">
                        {activeTable.footnotes.map((fn, fIdx) => (
                          <li key={fIdx}>{fn}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
                  No structured financial tables extracted for this document.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Pane: Source Inspector & Candidate Evidence Discovery */}
        <div className="flex w-80 flex-col border-l border-atlas-border-default bg-atlas-surface-1 shrink-0 overflow-hidden">
          <div className="border-b border-atlas-border-default p-2.5 bg-atlas-surface-0">
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Evidence Candidates ({candidates.length})
            </h3>
            <p className="text-[11px] text-atlas-text-muted">
              Source-verified disclosures ready for 1-click conversion to research evidence.
            </p>
          </div>

          {/* Investigation Selector for Promotion */}
          {investigations.length > 0 && (
            <div className="p-2 border-b border-atlas-border-default bg-atlas-surface-2/40">
              <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1">
                Target Investigation:
              </label>
              <select
                value={selectedTargetInvId}
                onChange={(e) => setSelectedTargetInvId(e.target.value)}
                className="w-full h-7 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {investigations.map((inv) => (
                  <option key={inv.investigation_id} value={inv.investigation_id}>
                    {inv.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Candidates List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {candidates.length === 0 ? (
              <div className="p-4 text-center text-xs text-atlas-text-muted">
                No candidate evidence disclosures extracted for this document.
              </div>
            ) : (
              candidates.map((cand) => (
                <div
                  key={cand.candidate_id}
                  className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-2.5 text-xs shadow-xs"
                >
                  <div className="flex items-center justify-between text-[10px] text-atlas-text-muted mb-1">
                    <Badge variant="outline" className="font-mono text-[9px]">
                      {cand.evidence_type}
                    </Badge>
                    <span className="font-mono">{cand.location_reference}</span>
                  </div>

                  <p className="font-medium text-atlas-text-primary mb-1.5 leading-snug">
                    {cand.extracted_text}
                  </p>

                  {cand.numeric_value !== undefined && cand.numeric_value !== null && (
                    <div className="mb-2 flex items-center gap-1.5 text-[10px] font-mono text-atlas-accent">
                      <span>Value:</span>
                      <span className="font-bold">
                        {cand.currency || ""}{" "}
                        {new Intl.NumberFormat("en-US").format(cand.numeric_value)}
                      </span>
                      {cand.unit && <span>{cand.unit}</span>}
                      {cand.reporting_period && <span>({cand.reporting_period})</span>}
                    </div>
                  )}

                  <Button
                    variant="primary"
                    size="sm"
                    disabled={convertingCandId === cand.candidate_id || !selectedTargetInvId}
                    onClick={() => handlePromoteCandidate(cand.candidate_id)}
                    className="w-full h-6 text-[10px] font-semibold"
                  >
                    {convertingCandId === cand.candidate_id
                      ? "Converting..."
                      : "+ Promote to Evidence"}
                  </Button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
