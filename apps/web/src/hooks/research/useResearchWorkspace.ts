"use client";

import { useCallback, useEffect, useState } from "react";
import * as api from "@/lib/research/api";
import {
  AttachResearchEvidenceDTO,
  CreateResearchClaimDTO,
  CreateResearchHypothesisDTO,
  CreateResearchInvestigationDTO,
  CreateResearchNoteDTO,
  CreateResearchQuestionDTO,
  InvestigationLifecycleStatus,
  LinkResearchSourceDTO,
  ResearchActivity,
  ResearchCitation,
  ResearchClaim,
  ResearchEvidence,
  ResearchHypothesis,
  ResearchInvestigation,
  ResearchNote,
  ResearchNoteRevision,
  ResearchOverviewSummary,
  ResearchQuestion,
  ResearchSourceReference,
  ResearchSourceType,
  ResearchType,
  UpdateResearchInvestigationDTO,
  UpdateResearchNoteDTO,
} from "@/lib/research/types";

export type ResearchTabMode = "OVERVIEW" | "INVESTIGATIONS" | "SOURCES" | "ACTIVITY";
export type InvestigationWorkspaceSection =
  | "NOTES"
  | "QUESTIONS"
  | "HYPOTHESES"
  | "CLAIMS"
  | "SOURCES"
  | "EVIDENCE"
  | "ACTIVITY";

export function useResearchWorkspace() {
  // Navigation State
  const [activeTab, setActiveTab] = useState<ResearchTabMode>("OVERVIEW");
  const [selectedInvestigationId, setSelectedInvestigationId] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<InvestigationWorkspaceSection>("NOTES");

  // Overview Data
  const [overview, setOverview] = useState<ResearchOverviewSummary | null>(null);
  const [isOverviewLoading, setIsOverviewLoading] = useState<boolean>(false);

  // Investigations List State
  const [investigations, setInvestigations] = useState<ResearchInvestigation[]>([]);
  const [investigationsTotal, setInvestigationsTotal] = useState<number>(0);
  const [isInvestigationsLoading, setIsInvestigationsLoading] = useState<boolean>(false);
  const [statusFilter, setStatusFilter] = useState<InvestigationLifecycleStatus | undefined>(undefined);
  const [typeFilter, setTypeFilter] = useState<ResearchType | undefined>(undefined);
  const [entityFilter, setEntityFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Current Active Investigation Data
  const [currentInvestigation, setCurrentInvestigation] = useState<ResearchInvestigation | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);
  const [notes, setNotes] = useState<ResearchNote[]>([]);
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [hypotheses, setHypotheses] = useState<ResearchHypothesis[]>([]);
  const [claims, setClaims] = useState<ResearchClaim[]>([]);
  const [linkedSources, setLinkedSources] = useState<ResearchSourceReference[]>([]);
  const [evidenceList, setEvidenceList] = useState<ResearchEvidence[]>([]);
  const [citationsList, setCitationsList] = useState<ResearchCitation[]>([]);
  const [activityTimeline, setActivityTimeline] = useState<ResearchActivity[]>([]);

  // Active Note Editing
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [selectedNoteRevisions, setSelectedNoteRevisions] = useState<ResearchNoteRevision[]>([]);
  const [isNoteSaving, setIsNoteSaving] = useState<boolean>(false);
  const [noteSaveStatus, setNoteSaveStatus] = useState<"SAVED" | "SAVING" | "UNSAVED" | "ERROR">("SAVED");
  const [noteSaveError, setNoteSaveError] = useState<string | null>(null);

  // Inspecting Elements
  const [selectedEvidence, setSelectedEvidence] = useState<ResearchEvidence | null>(null);
  const [selectedSource, setSelectedSource] = useState<ResearchSourceReference | null>(null);

  // Global Error state
  const [globalError, setGlobalError] = useState<string | null>(null);

  // -------------------------------------------------------------------------
  // Fetch Overview
  // -------------------------------------------------------------------------
  const loadOverview = useCallback(async () => {
    setIsOverviewLoading(true);
    setGlobalError(null);
    try {
      const data = await api.getResearchOverview();
      setOverview(data);
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load research overview.");
    } finally {
      setIsOverviewLoading(false);
    }
  }, []);

  // -------------------------------------------------------------------------
  // Fetch Investigations List
  // -------------------------------------------------------------------------
  const loadInvestigations = useCallback(async () => {
    setIsInvestigationsLoading(true);
    setGlobalError(null);
    try {
      const res = await api.listInvestigations({
        entity_id: entityFilter || undefined,
        status: statusFilter,
        research_type: typeFilter,
        q: searchQuery || undefined,
      });
      setInvestigations(res.items);
      setInvestigationsTotal(res.total_count);
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load investigations.");
    } finally {
      setIsInvestigationsLoading(false);
    }
  }, [entityFilter, statusFilter, typeFilter, searchQuery]);

  // -------------------------------------------------------------------------
  // Fetch Full Investigation Workspace Detail
  // -------------------------------------------------------------------------
  const loadInvestigationDetail = useCallback(async (id: string) => {
    setIsDetailLoading(true);
    setGlobalError(null);
    try {
      const [inv, noteRes, qRes, hRes, cRes, srcRes, evRes, citRes, actRes] = await Promise.all([
        api.getInvestigation(id),
        api.listNotes(id),
        api.listQuestions(id),
        api.listHypotheses(id),
        api.listClaims(id),
        api.listInvestigationSources(id),
        api.listEvidence(id),
        api.listCitations(id),
        api.listActivity(id),
      ]);

      setCurrentInvestigation(inv);
      setNotes(noteRes.items);
      setQuestions(qRes.items);
      setHypotheses(hRes.items);
      setClaims(cRes.items);
      setLinkedSources(srcRes.items);
      setEvidenceList(evRes.items);
      setCitationsList(citRes.items);
      setActivityTimeline(actRes.items);

      if (noteRes.items.length > 0 && !selectedNoteId) {
        setSelectedNoteId(noteRes.items[0].note_id);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load investigation details.");
    } finally {
      setIsDetailLoading(false);
    }
  }, [selectedNoteId]);

  // -------------------------------------------------------------------------
  // Navigation & Triggers
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (activeTab === "OVERVIEW") {
      loadOverview();
    } else if (activeTab === "INVESTIGATIONS") {
      loadInvestigations();
    }
  }, [activeTab, loadOverview, loadInvestigations]);

  useEffect(() => {
    if (selectedInvestigationId) {
      loadInvestigationDetail(selectedInvestigationId);
    } else {
      setCurrentInvestigation(null);
    }
  }, [selectedInvestigationId, loadInvestigationDetail]);

  const selectInvestigation = (id: string | null) => {
    setSelectedInvestigationId(id);
    setSelectedNoteId(null);
    setSelectedEvidence(null);
    setSelectedSource(null);
  };

  // -------------------------------------------------------------------------
  // Investigation Actions
  // -------------------------------------------------------------------------
  const createInvestigation = async (data: CreateResearchInvestigationDTO) => {
    try {
      const inv = await api.createInvestigation(data);
      await loadInvestigations();
      setSelectedInvestigationId(inv.investigation_id);
      return inv;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create investigation.");
      throw err;
    }
  };

  const updateInvestigation = async (data: UpdateResearchInvestigationDTO) => {
    if (!currentInvestigation) return;
    try {
      const updated = await api.updateInvestigation(currentInvestigation.investigation_id, data);
      setCurrentInvestigation(updated);
      await loadInvestigations();
      return updated;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update investigation.");
      throw err;
    }
  };

  const archiveInvestigation = async (id: string) => {
    try {
      const updated = await api.archiveInvestigation(id);
      if (selectedInvestigationId === id) {
        setCurrentInvestigation(updated);
      }
      await loadInvestigations();
    } catch (err: any) {
      setGlobalError(err.message || "Failed to archive investigation.");
    }
  };

  // -------------------------------------------------------------------------
  // Note Actions
  // -------------------------------------------------------------------------
  const createNote = async (data: CreateResearchNoteDTO) => {
    if (!selectedInvestigationId) return;
    try {
      const newNote = await api.createNote(selectedInvestigationId, data);
      setNotes((prev) => [newNote, ...prev]);
      setSelectedNoteId(newNote.note_id);
      return newNote;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create note.");
      throw err;
    }
  };

  const saveNote = async (noteId: string, data: UpdateResearchNoteDTO) => {
    setIsNoteSaving(true);
    setNoteSaveStatus("SAVING");
    setNoteSaveError(null);
    try {
      const updated = await api.updateNote(noteId, data);
      setNotes((prev) => prev.map((n) => (n.note_id === noteId ? updated : n)));
      setNoteSaveStatus("SAVED");
      return updated;
    } catch (err: any) {
      setNoteSaveStatus("ERROR");
      setNoteSaveError(err.message || "Failed to save note.");
      throw err;
    } finally {
      setIsNoteSaving(false);
    }
  };

  const loadNoteRevisions = async (noteId: string) => {
    try {
      const revs = await api.getNoteRevisions(noteId);
      setSelectedNoteRevisions(revs);
    } catch (err: any) {
      console.error("Failed to load note revisions:", err);
    }
  };

  // -------------------------------------------------------------------------
  // Question & Hypothesis Actions
  // -------------------------------------------------------------------------
  const addQuestion = async (data: CreateResearchQuestionDTO) => {
    if (!selectedInvestigationId) return;
    const q = await api.addQuestion(selectedInvestigationId, data);
    setQuestions((prev) => [...prev, q]);
    return q;
  };

  const updateQuestionStatus = async (questionId: string, status: any) => {
    const updated = await api.updateQuestion(questionId, { status });
    setQuestions((prev) => prev.map((q) => (q.question_id === questionId ? updated : q)));
  };

  const addHypothesis = async (data: CreateResearchHypothesisDTO) => {
    if (!selectedInvestigationId) return;
    const h = await api.addHypothesis(selectedInvestigationId, data);
    setHypotheses((prev) => [...prev, h]);
    return h;
  };

  const updateHypothesisStatus = async (hypothesisId: string, status: any) => {
    const updated = await api.updateHypothesis(hypothesisId, { status });
    setHypotheses((prev) => prev.map((h) => (h.hypothesis_id === hypothesisId ? updated : h)));
  };

  // -------------------------------------------------------------------------
  // Claim Actions
  // -------------------------------------------------------------------------
  const createClaim = async (data: CreateResearchClaimDTO) => {
    if (!selectedInvestigationId) return;
    const c = await api.createClaim(selectedInvestigationId, data);
    setClaims((prev) => [...prev, c]);
    return c;
  };

  // -------------------------------------------------------------------------
  // Source & Evidence Linking
  // -------------------------------------------------------------------------
  const linkSource = async (data: LinkResearchSourceDTO) => {
    if (!selectedInvestigationId) return;
    const src = await api.linkSource(selectedInvestigationId, data);
    setLinkedSources((prev) => {
      if (prev.some((s) => s.source_reference_id === src.source_reference_id)) return prev;
      return [src, ...prev];
    });
    return src;
  };

  const attachEvidence = async (data: AttachResearchEvidenceDTO) => {
    if (!selectedInvestigationId) return;
    const ev = await api.attachEvidence(selectedInvestigationId, data);
    setEvidenceList((prev) => [...prev, ev]);
    // Refresh citations
    const cits = await api.listCitations(selectedInvestigationId);
    setCitationsList(cits.items);
    return ev;
  };

  return {
    // Navigation
    activeTab,
    setActiveTab,
    selectedInvestigationId,
    selectInvestigation,
    activeSection,
    setActiveSection,

    // Overview
    overview,
    isOverviewLoading,
    loadOverview,

    // List
    investigations,
    investigationsTotal,
    isInvestigationsLoading,
    statusFilter,
    setStatusFilter,
    typeFilter,
    setTypeFilter,
    entityFilter,
    setEntityFilter,
    searchQuery,
    setSearchQuery,
    loadInvestigations,

    // Detail
    currentInvestigation,
    isDetailLoading,
    notes,
    questions,
    hypotheses,
    claims,
    linkedSources,
    evidenceList,
    citationsList,
    activityTimeline,

    // Note Editor
    selectedNoteId,
    setSelectedNoteId,
    selectedNoteRevisions,
    loadNoteRevisions,
    isNoteSaving,
    noteSaveStatus,
    noteSaveError,
    createNote,
    saveNote,

    // Actions
    createInvestigation,
    updateInvestigation,
    archiveInvestigation,
    addQuestion,
    updateQuestionStatus,
    addHypothesis,
    updateHypothesisStatus,
    createClaim,
    linkSource,
    attachEvidence,

    // Inspectors
    selectedEvidence,
    setSelectedEvidence,
    selectedSource,
    setSelectedSource,

    // Error
    globalError,
    clearError: () => setGlobalError(null),
  };
}
