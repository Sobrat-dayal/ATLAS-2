"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import {
  EvidenceLocationType,
  InvestigationLifecycleStatus,
  ResearchClaim,
  ResearchClaimCategory,
  ResearchEvidence,
  ResearchEvidenceStatus,
  ResearchHypothesis,
  ResearchHypothesisStatus,
  ResearchInvestigation,
  ResearchNote,
  ResearchNoteType,
  ResearchQuestion,
  ResearchQuestionStatus,
  ResearchSourceReference,
} from "@/lib/research/types";

interface InvestigationWorkspaceProps {
  investigation: ResearchInvestigation;
  notes: ResearchNote[];
  questions: ResearchQuestion[];
  hypotheses: ResearchHypothesis[];
  claims: ResearchClaim[];
  linkedSources: ResearchSourceReference[];
  evidenceList: ResearchEvidence[];
  activeSection: string;
  onSectionChange: (section: any) => void;
  onBack: () => void;
  onUpdateInvestigationStatus: (status: InvestigationLifecycleStatus) => void;
  onCreateNote: (title: string, noteType: ResearchNoteType) => Promise<any>;
  onSaveNote: (noteId: string, title: string, body: string, noteType: ResearchNoteType) => Promise<any>;
  onAddQuestion: (text: string) => Promise<any>;
  onUpdateQuestionStatus: (id: string, status: ResearchQuestionStatus) => Promise<any>;
  onAddHypothesis: (statement: string) => Promise<any>;
  onUpdateHypothesisStatus: (id: string, status: ResearchHypothesisStatus) => Promise<any>;
  onCreateClaim: (statement: string, category: ResearchClaimCategory) => Promise<any>;
  onAttachEvidence: (sourceId: string, location: string, page?: number, excerpt?: string) => Promise<any>;
  selectedEvidence: ResearchEvidence | null;
  onSelectEvidence: (ev: ResearchEvidence | null) => void;
  selectedSource: ResearchSourceReference | null;
  onSelectSource: (src: ResearchSourceReference | null) => void;
}

export function InvestigationWorkspace({
  investigation,
  notes,
  questions,
  hypotheses,
  claims,
  linkedSources,
  evidenceList,
  activeSection,
  onSectionChange,
  onBack,
  onUpdateInvestigationStatus,
  onCreateNote,
  onSaveNote,
  onAddQuestion,
  onUpdateQuestionStatus,
  onAddHypothesis,
  onUpdateHypothesisStatus,
  onCreateClaim,
  onAttachEvidence,
  selectedEvidence,
  onSelectEvidence,
  selectedSource,
  onSelectSource,
}: InvestigationWorkspaceProps) {
  // Active Note Editor State
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(
    notes.length > 0 ? notes[0].note_id : null
  );
  const activeNote = notes.find((n) => n.note_id === selectedNoteId) || notes[0];

  const [noteTitle, setNoteTitle] = useState(activeNote?.title || "");
  const [noteBody, setNoteBody] = useState(activeNote?.body_document || "");
  const [noteType, setNoteType] = useState<ResearchNoteType>(
    activeNote?.note_type || "ANALYSIS"
  );
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // When selected note changes in sidebar, update editor fields
  const handleSelectNote = (n: ResearchNote) => {
    setSelectedNoteId(n.note_id);
    setNoteTitle(n.title);
    setNoteBody(n.body_document);
    setNoteType(n.note_type);
    setSaveMessage(null);
  };

  const handleSaveActiveNote = async () => {
    if (!activeNote) return;
    setIsSaving(true);
    setSaveMessage(null);
    try {
      await onSaveNote(activeNote.note_id, noteTitle, noteBody, noteType);
      setSaveMessage("Saved revision successfully.");
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (err: any) {
      setSaveMessage(`Error: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Modals / Simple inputs
  const [newQuestionText, setNewQuestionText] = useState("");
  const [newHypothesisText, setNewHypothesisText] = useState("");
  const [newClaimText, setNewClaimText] = useState("");
  const [newClaimCategory, setNewClaimCategory] = useState<ResearchClaimCategory>(
    "ANALYST_INTERPRETATION"
  );
  const [newNoteTitle, setNewNoteTitle] = useState("");

  // Attach Evidence form
  const [evidenceSourceId, setEvidenceSourceId] = useState(
    linkedSources.length > 0 ? linkedSources[0].source_reference_id : ""
  );
  const [evidenceLocation, setEvidenceLocation] = useState("");
  const [evidencePage, setEvidencePage] = useState<number | undefined>(undefined);
  const [evidenceExcerpt, setEvidenceExcerpt] = useState("");
  const [showAttachEvidence, setShowAttachEvidence] = useState(false);

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Investigation Workspace Header */}
      <div className="border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Button variant="secondary" size="xs" onClick={onBack}>
              ← All Investigations
            </Button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold text-atlas-text-primary">
                  {investigation.title}
                </h1>
                {investigation.primary_subject_entity_id && (
                  <Badge variant="primary" className="font-mono text-[10px]">
                    {investigation.primary_subject_entity_id}
                  </Badge>
                )}
                <Badge variant="outline" className="font-mono text-[10px]">
                  Rev v{investigation.revision}
                </Badge>
              </div>
              {investigation.research_objective && (
                <p className="line-clamp-1 text-xs text-atlas-text-muted">
                  Objective: {investigation.research_objective}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] text-atlas-text-muted">Status:</span>
            <select
              value={investigation.status}
              onChange={(e) =>
                onUpdateInvestigationStatus(e.target.value as InvestigationLifecycleStatus)
              }
              className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs font-semibold text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
            >
              <option value="DRAFT">Draft</option>
              <option value="ACTIVE">Active</option>
              <option value="ON_HOLD">On Hold</option>
              <option value="COMPLETED">Completed</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* 3-Pane Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigator (Width: 200px) */}
        <div className="w-52 shrink-0 border-r border-atlas-border-default bg-atlas-surface-1 p-2">
          <div className="mb-2 px-2 text-[10px] font-bold uppercase tracking-wider text-atlas-text-muted">
            Investigation Artifacts
          </div>
          <nav className="space-y-1">
            {[
              { id: "NOTES", label: "Structured Notes", count: notes.length },
              { id: "QUESTIONS", label: "Research Questions", count: questions.length },
              { id: "HYPOTHESES", label: "Hypotheses", count: hypotheses.length },
              { id: "CLAIMS", label: "Claims & Findings", count: claims.length },
              { id: "SOURCES", label: "Linked Sources", count: linkedSources.length },
              { id: "EVIDENCE", label: "Evidence Records", count: evidenceList.length },
            ].map((sec) => (
              <button
                key={sec.id}
                onClick={() => onSectionChange(sec.id)}
                className={`flex w-full items-center justify-between rounded-xs px-2.5 py-1.5 text-xs font-medium transition-colors ${
                  activeSection === sec.id
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                }`}
              >
                <span>{sec.label}</span>
                <span className="font-mono text-[10px] opacity-80">{sec.count}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Center Main Work Area */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* SECTION: NOTES */}
          {activeSection === "NOTES" && (
            <div className="flex h-full overflow-hidden">
              {/* Note List Sidebar */}
              <div className="w-64 shrink-0 border-r border-atlas-border-default bg-atlas-surface-1 p-2.5 flex flex-col">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-atlas-text-muted">
                    Notes ({notes.length})
                  </span>
                </div>

                <div className="mb-2 flex gap-1">
                  <Input
                    value={newNoteTitle}
                    onChange={(e) => setNewNoteTitle(e.target.value)}
                    placeholder="New note title..."
                    className="h-7 text-xs"
                  />
                  <Button
                    variant="primary"
                    size="xs"
                    onClick={async () => {
                      if (!newNoteTitle.trim()) return;
                      await onCreateNote(newNoteTitle.trim(), "ANALYSIS");
                      setNewNoteTitle("");
                    }}
                  >
                    + Add
                  </Button>
                </div>

                <div className="flex-1 overflow-y-auto space-y-1">
                  {notes.map((n) => {
                    const isSelected = activeNote?.note_id === n.note_id;
                    return (
                      <div
                        key={n.note_id}
                        onClick={() => handleSelectNote(n)}
                        className={`cursor-pointer rounded-xs p-2 text-xs transition-colors ${
                          isSelected
                            ? "bg-atlas-surface-hover border-l-2 border-l-atlas-accent"
                            : "hover:bg-atlas-surface-hover"
                        }`}
                      >
                        <div className="font-semibold text-atlas-text-primary line-clamp-1">
                          {n.title}
                        </div>
                        <div className="mt-1 flex items-center justify-between font-mono text-[10px] text-atlas-text-muted">
                          <span>{n.note_type}</span>
                          <span>v{n.revision}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Note Editor Pane */}
              <div className="flex flex-1 flex-col overflow-hidden bg-atlas-surface-0 p-4">
                {activeNote ? (
                  <div className="flex h-full flex-col space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default pb-2">
                      <div className="flex-1">
                        <Input
                          value={noteTitle}
                          onChange={(e) => setNoteTitle(e.target.value)}
                          className="h-8 font-semibold text-xs"
                          placeholder="Note title..."
                        />
                      </div>

                      <div className="flex items-center gap-2">
                        <select
                          value={noteType}
                          onChange={(e) => setNoteType(e.target.value as ResearchNoteType)}
                          className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
                        >
                          <option value="OBSERVATION">Observation</option>
                          <option value="ANALYSIS">Analysis</option>
                          <option value="HYPOTHESIS">Hypothesis</option>
                          <option value="ASSUMPTION">Assumption</option>
                          <option value="CONCLUSION">Conclusion</option>
                          <option value="GENERAL_NOTE">General Note</option>
                        </select>

                        <Button
                          variant="primary"
                          size="sm"
                          onClick={handleSaveActiveNote}
                          disabled={isSaving}
                        >
                          {isSaving ? "Saving..." : "Save Revision"}
                        </Button>
                      </div>
                    </div>

                    {saveMessage && (
                      <div className="text-[11px] font-mono text-atlas-positive">
                        ✓ {saveMessage}
                      </div>
                    )}

                    {/* Markdown Textarea */}
                    <div className="flex-1">
                      <textarea
                        value={noteBody}
                        onChange={(e) => setNoteBody(e.target.value)}
                        placeholder="Write structured research note using Markdown (support headers, bullet points, citations)..."
                        className="h-full w-full resize-none rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 font-mono text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-hidden"
                      />
                    </div>

                    <div className="flex items-center justify-between font-mono text-[10px] text-atlas-text-muted">
                      <div>
                        Length: {noteBody.length} chars • Words:{" "}
                        {noteBody.trim() ? noteBody.trim().split(/\s+/).length : 0}
                      </div>
                      <div>
                        Note ID: {activeNote.note_id} • Rev v{activeNote.revision}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex h-full items-center justify-center text-xs text-atlas-text-muted">
                    No note selected. Create a note in the sidebar.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* SECTION: QUESTIONS */}
          {activeSection === "QUESTIONS" && (
            <div className="flex flex-1 flex-col p-4 overflow-y-auto">
              <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-2">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                    Research Questions ({questions.length})
                  </h2>
                  <p className="text-[11px] text-atlas-text-muted">
                    Analyst-authored inquiries guiding this investigation.
                  </p>
                </div>
              </div>

              {/* Add Question input */}
              <div className="mb-4 flex gap-2">
                <Input
                  value={newQuestionText}
                  onChange={(e) => setNewQuestionText(e.target.value)}
                  placeholder="Enter research question (e.g. How has operating margin changed?)..."
                  className="flex-1 text-xs"
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={async () => {
                    if (!newQuestionText.trim()) return;
                    await onAddQuestion(newQuestionText.trim());
                    setNewQuestionText("");
                  }}
                >
                  + Add Question
                </Button>
              </div>

              <div className="space-y-2">
                {questions.map((q) => (
                  <div
                    key={q.question_id}
                    className="flex items-center justify-between rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="font-semibold text-atlas-text-primary">
                        {q.question_text}
                      </div>
                      <div className="flex items-center gap-2 font-mono text-[10px] text-atlas-text-muted">
                        <span>ID: {q.question_id}</span>
                        {q.related_entity_ids.length > 0 && (
                          <span>Entities: {q.related_entity_ids.join(", ")}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          q.status === "ADDRESSED"
                            ? "positive"
                            : q.status === "UNDER_REVIEW"
                            ? "warning"
                            : "outline"
                        }
                      >
                        {q.status}
                      </Badge>
                      <Button
                        variant="secondary"
                        size="xs"
                        onClick={() =>
                          onUpdateQuestionStatus(
                            q.question_id,
                            q.status === "ADDRESSED" ? "OPEN" : "ADDRESSED"
                          )
                        }
                      >
                        {q.status === "ADDRESSED" ? "Reopen" : "Mark Addressed"}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: HYPOTHESES */}
          {activeSection === "HYPOTHESES" && (
            <div className="flex flex-1 flex-col p-4 overflow-y-auto">
              <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-2">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                    Research Hypotheses ({hypotheses.length})
                  </h2>
                  <p className="text-[11px] text-atlas-text-muted">
                    Propositions under evaluation. Hypotheses are ideas to test, strictly distinct from verified facts.
                  </p>
                </div>
              </div>

              {/* Add Hypothesis input */}
              <div className="mb-4 flex gap-2">
                <Input
                  value={newHypothesisText}
                  onChange={(e) => setNewHypothesisText(e.target.value)}
                  placeholder="Enter hypothesis statement (e.g. Services margin stability buffers hardware replacement cycle)..."
                  className="flex-1 text-xs"
                />
                <Button
                  variant="primary"
                  size="sm"
                  onClick={async () => {
                    if (!newHypothesisText.trim()) return;
                    await onAddHypothesis(newHypothesisText.trim());
                    setNewHypothesisText("");
                  }}
                >
                  + Propose Hypothesis
                </Button>
              </div>

              <div className="space-y-2">
                {hypotheses.map((h) => (
                  <div
                    key={h.hypothesis_id}
                    className="flex items-center justify-between rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs"
                  >
                    <div className="space-y-1 flex-1 pr-4">
                      <div className="font-semibold text-atlas-text-primary">
                        {h.statement}
                      </div>
                      <div className="font-mono text-[10px] text-atlas-text-muted">
                        ID: {h.hypothesis_id} • Rev v{h.revision}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <select
                        value={h.status}
                        onChange={(e) =>
                          onUpdateHypothesisStatus(
                            h.hypothesis_id,
                            e.target.value as ResearchHypothesisStatus
                          )
                        }
                        className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
                      >
                        <option value="PROPOSED">PROPOSED</option>
                        <option value="UNDER_TEST">UNDER_TEST</option>
                        <option value="SUPPORTED_BY_AVAILABLE_EVIDENCE">
                          SUPPORTED
                        </option>
                        <option value="CONTRADICTED_BY_AVAILABLE_EVIDENCE">
                          CONTRADICTED
                        </option>
                        <option value="INCONCLUSIVE">INCONCLUSIVE</option>
                        <option value="RETIRED">RETIRED</option>
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: CLAIMS */}
          {activeSection === "CLAIMS" && (
            <div className="flex flex-1 flex-col p-4 overflow-y-auto">
              <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-2">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                    Research Claims & Assertions ({claims.length})
                  </h2>
                  <p className="text-[11px] text-atlas-text-muted">
                    Clear distinction between source-reported facts, assumptions, and analyst interpretations.
                  </p>
                </div>
              </div>

              {/* Add Claim */}
              <div className="mb-4 flex gap-2">
                <Input
                  value={newClaimText}
                  onChange={(e) => setNewClaimText(e.target.value)}
                  placeholder="Enter claim or finding statement..."
                  className="flex-1 text-xs"
                />
                <select
                  value={newClaimCategory}
                  onChange={(e) =>
                    setNewClaimCategory(e.target.value as ResearchClaimCategory)
                  }
                  className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2 text-xs font-mono text-atlas-text-primary"
                >
                  <option value="SOURCE_REPORTED_FACT">Source Fact</option>
                  <option value="ANALYST_INTERPRETATION">Analyst Interpretation</option>
                  <option value="ASSUMPTION">Assumption</option>
                  <option value="ESTIMATE">Estimate</option>
                  <option value="OPEN_QUESTION">Open Question</option>
                </select>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={async () => {
                    if (!newClaimText.trim()) return;
                    await onCreateClaim(newClaimText.trim(), newClaimCategory);
                    setNewClaimText("");
                  }}
                >
                  + Add Claim
                </Button>
              </div>

              <div className="space-y-2">
                {claims.map((c) => (
                  <div
                    key={c.claim_id}
                    className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <Badge
                        variant={
                          c.claim_category === "SOURCE_REPORTED_FACT"
                            ? "positive"
                            : c.claim_category === "ANALYST_INTERPRETATION"
                            ? "primary"
                            : "outline"
                        }
                        className="font-mono text-[10px]"
                      >
                        {c.claim_category.replace(/_/g, " ")}
                      </Badge>
                      <Badge variant="outline" className="text-[10px]">
                        {c.evidence_status.replace(/_/g, " ")}
                      </Badge>
                    </div>

                    <div className="font-semibold text-atlas-text-primary">
                      {c.statement}
                    </div>

                    <div className="flex items-center gap-3 font-mono text-[10px] text-atlas-text-muted">
                      <span>Claim ID: {c.claim_id}</span>
                      <span>•</span>
                      <span>Author: {c.author_user_id}</span>
                      <span>•</span>
                      <span>
                        Supporting Evidences: {c.supporting_evidence_ids.length}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: SOURCES */}
          {activeSection === "SOURCES" && (
            <div className="flex flex-1 flex-col p-4 overflow-y-auto">
              <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-2">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                    Linked Research Sources ({linkedSources.length})
                  </h2>
                  <p className="text-[11px] text-atlas-text-muted">
                    Official filings, financial statements, and news articles associated with this investigation.
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                {linkedSources.map((src) => (
                  <div
                    key={src.source_reference_id}
                    onClick={() => onSelectSource(src)}
                    className="flex cursor-pointer items-center justify-between rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs hover:bg-atlas-surface-hover"
                  >
                    <div className="space-y-1">
                      <div className="font-semibold text-atlas-text-primary">
                        {src.source_title}
                      </div>
                      <div className="font-mono text-[11px] text-atlas-text-muted">
                        {src.publisher_id || src.provider_id} • Period:{" "}
                        {src.reporting_period || "—"}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {src.source_type}
                      </Badge>
                      {src.source_url && (
                        <a
                          href={src.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="text-[11px] font-mono text-atlas-accent hover:underline"
                        >
                          Source ↗
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: EVIDENCE */}
          {activeSection === "EVIDENCE" && (
            <div className="flex flex-1 flex-col p-4 overflow-y-auto">
              <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-2">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                    Verified Evidence Records ({evidenceList.length})
                  </h2>
                  <p className="text-[11px] text-atlas-text-muted">
                    Specific source spans, page numbers, and quotes backing findings.
                  </p>
                </div>
                <Button
                  variant="primary"
                  size="xs"
                  onClick={() => setShowAttachEvidence(!showAttachEvidence)}
                >
                  {showAttachEvidence ? "Close Form" : "+ Attach Evidence"}
                </Button>
              </div>

              {/* Attach Evidence Form */}
              {showAttachEvidence && (
                <div className="mb-4 rounded-sm border border-atlas-accent/40 bg-atlas-surface-1 p-3 space-y-3">
                  <div className="text-xs font-bold text-atlas-text-primary">
                    Attach New Evidence Reference
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] text-atlas-text-secondary">
                        Source Document
                      </label>
                      <select
                        value={evidenceSourceId}
                        onChange={(e) => setEvidenceSourceId(e.target.value)}
                        className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary"
                      >
                        {linkedSources.map((s) => (
                          <option key={s.source_reference_id} value={s.source_reference_id}>
                            {s.source_title.slice(0, 45)}...
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] text-atlas-text-secondary">
                        Location Reference (e.g. Item 1A, Table 4)
                      </label>
                      <Input
                        value={evidenceLocation}
                        onChange={(e) => setEvidenceLocation(e.target.value)}
                        placeholder="Item 1A Risk Factors"
                        className="h-7 text-xs"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] text-atlas-text-secondary">
                      Permitted Excerpt / Quotation
                    </label>
                    <textarea
                      value={evidenceExcerpt}
                      onChange={(e) => setEvidenceExcerpt(e.target.value)}
                      placeholder="Verbatim text quotation from source..."
                      rows={2}
                      className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs font-mono text-atlas-text-primary"
                    />
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button
                      variant="primary"
                      size="xs"
                      onClick={async () => {
                        if (!evidenceLocation.trim()) return;
                        await onAttachEvidence(
                          evidenceSourceId,
                          evidenceLocation.trim(),
                          evidencePage,
                          evidenceExcerpt.trim()
                        );
                        setShowAttachEvidence(false);
                        setEvidenceLocation("");
                        setEvidenceExcerpt("");
                      }}
                    >
                      Save Evidence Record
                    </Button>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                {evidenceList.map((ev) => (
                  <div
                    key={ev.evidence_id}
                    onClick={() => onSelectEvidence(ev)}
                    className="cursor-pointer rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3 text-xs space-y-1.5 hover:bg-atlas-surface-hover"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-atlas-text-primary">
                        📍 {ev.source_location_reference}
                      </span>
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {ev.source_location_type}
                      </Badge>
                    </div>

                    {ev.allowed_excerpt && (
                      <blockquote className="border-l-2 border-atlas-accent/60 pl-2 text-[11px] italic text-atlas-text-secondary">
                        "{ev.allowed_excerpt}"
                      </blockquote>
                    )}

                    <div className="flex items-center justify-between font-mono text-[10px] text-atlas-text-muted">
                      <span>Source: {ev.source_title || ev.source_reference_id}</span>
                      {ev.page_number && <span>Page {ev.page_number}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Inspector Sidebar (Width: 280px) */}
        <div className="w-72 shrink-0 border-l border-atlas-border-default bg-atlas-surface-1 p-3 text-xs overflow-y-auto">
          {selectedEvidence ? (
            <div className="space-y-3">
              <div>
                <span className="font-mono text-[10px] text-atlas-text-muted uppercase">
                  Evidence Inspector
                </span>
                <h3 className="mt-0.5 text-xs font-bold text-atlas-text-primary">
                  {selectedEvidence.source_location_reference}
                </h3>
              </div>

              <div className="space-y-1.5 rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-2.5 font-mono text-[11px]">
                <div>
                  <span className="text-atlas-text-muted">Evidence ID: </span>
                  <span className="text-atlas-text-primary">{selectedEvidence.evidence_id}</span>
                </div>
                <div>
                  <span className="text-atlas-text-muted">Source: </span>
                  <span className="text-atlas-text-primary">{selectedEvidence.source_title}</span>
                </div>
                {selectedEvidence.page_number && (
                  <div>
                    <span className="text-atlas-text-muted">Page: </span>
                    <span className="text-atlas-text-primary">{selectedEvidence.page_number}</span>
                  </div>
                )}
                <div>
                  <span className="text-atlas-text-muted">Observed: </span>
                  <span className="text-atlas-text-primary">
                    {new Date(selectedEvidence.observation_time).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {selectedEvidence.allowed_excerpt && (
                <div>
                  <span className="font-mono text-[10px] text-atlas-text-muted uppercase">
                    Quoted Excerpt
                  </span>
                  <p className="mt-1 rounded-xs bg-atlas-surface-0 p-2 text-[11px] italic text-atlas-text-secondary">
                    "{selectedEvidence.allowed_excerpt}"
                  </p>
                </div>
              )}

              {selectedEvidence.source_url && (
                <div className="pt-2">
                  <a
                    href={selectedEvidence.source_url}
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
            <div className="flex h-64 flex-col items-center justify-center text-center text-atlas-text-muted">
              <p>Select an evidence record or source document to inspect provenance details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
