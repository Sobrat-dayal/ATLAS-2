"use client";

import { useCallback, useEffect, useState } from "react";
import * as api from "@/lib/research/api";
import {
  AttachResearchEvidenceDTO,
  ConvertEvidenceCandidateDTO,
  CreateResearchClaimDTO,
  CreateResearchHypothesisDTO,
  CreateResearchInvestigationDTO,
  CreateResearchNoteDTO,
  CreateResearchQuestionDTO,
  DocumentComparisonMode,
  DocumentComparisonResult,
  DocumentSearchHit,
  FinancialFactsCompareResponse,
  InvestigationLifecycleStatus,
  LinkResearchSourceDTO,
  ResearchActivity,
  ResearchCitation,
  ResearchClaim,
  ResearchDocumentOutline,
  ResearchDocumentProcessingStatus,
  ResearchDocumentSection,
  ResearchDocumentTable,
  ResearchEvidence,
  ResearchEvidenceCandidate,
  ResearchHypothesis,
  ResearchInvestigation,
  ResearchNote,
  ResearchNoteRevision,
  ResearchOverviewSummary,
  ResearchQuestion,
  ResearchSearchHit,
  ResearchSourceDiscoveryQuery,
  ResearchSourceReference,
  ResearchSourceType,
  ResearchSourceTypeItem,
  ResearchType,
  UpdateResearchInvestigationDTO,
  UpdateResearchNoteDTO,
  // Stage 106 Types
  CreateResearchAnalysisDTO,
  CreateResearchAssumptionDTO,
  CreateResearchFindingDTO,
  ExecuteHypothesisEvaluationDTO,
  ResearchAnalysis,
  ResearchAnalysisResult,
  ResearchAnalysisRun,
  ResearchAnalysisSpecification,
  ResearchAnalysisType,
  ResearchAnalysisTypeDefinition,
  ResearchAssumption,
  ResearchFinding,
  ResearchHypothesisEvaluation,
  SensitivityAnalysisRequest,
  SensitivityAnalysisResponse,
  UpdateResearchAnalysisDTO,
  UpdateResearchFindingDTO,
  ValidateAnalysisSpecificationRequest,
  ValidateAnalysisSpecificationResponse,
} from "@/lib/research/types";

export type ResearchTabMode =
  | "OVERVIEW"
  | "INVESTIGATIONS"
  | "ANALYSIS"
  | "SOURCES"
  | "DISCOVERY"
  | "DOCUMENT_VIEWER"
  | "COMPARE"
  | "ACTIVITY";
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
  // Stage 105: Source Discovery State & Handlers
  // -------------------------------------------------------------------------
  const [discoveryQuery, setDiscoveryQuery] = useState<ResearchSourceDiscoveryQuery>({
    text_query: "",
    limit: 25,
  });
  const [discoveryResults, setDiscoveryResults] = useState<ResearchSearchHit[]>([]);
  const [discoveryTotal, setDiscoveryTotal] = useState<number>(0);
  const [isDiscoveryLoading, setIsDiscoveryLoading] = useState<boolean>(false);
  const [sourceTypes, setSourceTypes] = useState<ResearchSourceTypeItem[]>([]);

  const loadSourceTypes = useCallback(async () => {
    try {
      const res = await api.getSourceTypes();
      setSourceTypes(res.items);
    } catch (err: any) {
      console.error("Failed to load source types", err);
    }
  }, []);

  const searchDiscovery = useCallback(
    async (customQuery?: Partial<ResearchSourceDiscoveryQuery>) => {
      setIsDiscoveryLoading(true);
      setGlobalError(null);
      try {
        const q: ResearchSourceDiscoveryQuery = {
          ...discoveryQuery,
          ...customQuery,
        };
        setDiscoveryQuery(q);
        const res = await api.discoverSources(q);
        setDiscoveryResults(res.hits);
        setDiscoveryTotal(res.total_count);
      } catch (err: any) {
        setGlobalError(err.message || "Failed to search research sources.");
      } finally {
        setIsDiscoveryLoading(false);
      }
    },
    [discoveryQuery]
  );

  // -------------------------------------------------------------------------
  // Stage 105: Document Intelligence & Viewer State & Handlers
  // -------------------------------------------------------------------------
  const [activeDocumentId, setActiveDocumentId] = useState<string>("0000320193-24-000106");
  const [activeDocument, setActiveDocument] = useState<ResearchSourceReference | null>(null);
  const [documentProcessingStatus, setDocumentProcessingStatus] =
    useState<ResearchDocumentProcessingStatus | null>(null);
  const [documentOutline, setDocumentOutline] = useState<ResearchDocumentOutline | null>(null);
  const [activeDocumentSectionId, setActiveDocumentSectionId] = useState<string | null>(null);
  const [activeDocumentSection, setActiveDocumentSection] = useState<ResearchDocumentSection | null>(null);
  const [documentTables, setDocumentTables] = useState<ResearchDocumentTable[]>([]);
  const [documentSearchQuery, setDocumentSearchQuery] = useState<string>("");
  const [documentSearchHits, setDocumentSearchHits] = useState<DocumentSearchHit[]>([]);
  const [isDocSearchLoading, setIsDocSearchLoading] = useState<boolean>(false);
  const [candidates, setCandidates] = useState<ResearchEvidenceCandidate[]>([]);
  const [isDocumentLoading, setIsDocumentLoading] = useState<boolean>(false);

  const loadDocument = useCallback(async (docId: string) => {
    setIsDocumentLoading(true);
    setActiveDocumentId(docId);
    setGlobalError(null);
    try {
      const [docRes, statusRes, outlineRes, tablesRes, candRes] = await Promise.all([
        api.getDocument(docId).catch(() => null),
        api.getDocumentProcessingStatus(docId).catch(() => null),
        api.getDocumentOutline(docId).catch(() => null),
        api.getDocumentTables(docId).catch(() => ({ items: [], total_count: 0 })),
        api.listEvidenceCandidates(docId).catch(() => ({ items: [], total_count: 0 })),
      ]);

      if (docRes) setActiveDocument(docRes);
      if (statusRes) setDocumentProcessingStatus(statusRes);
      if (outlineRes) {
        setDocumentOutline(outlineRes);
        if (outlineRes.sections && outlineRes.sections.length > 0) {
          const firstSection = outlineRes.sections[0];
          setActiveDocumentSectionId(firstSection.section_id);
          setActiveDocumentSection(firstSection);
        }
      }
      setDocumentTables(tablesRes.items);
      setCandidates(candRes.items);
      setDocumentSearchHits([]);
      setDocumentSearchQuery("");
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load document.");
    } finally {
      setIsDocumentLoading(false);
    }
  }, []);

  const selectDocumentSection = useCallback(
    async (sectionId: string) => {
      setActiveDocumentSectionId(sectionId);
      if (!activeDocumentId) return;
      try {
        const sec = await api.getDocumentSection(activeDocumentId, sectionId);
        setActiveDocumentSection(sec);
      } catch (err: any) {
        console.error("Failed to load section", err);
      }
    },
    [activeDocumentId]
  );

  const searchInDocument = useCallback(
    async (q: string, sectionId?: string) => {
      if (!activeDocumentId || !q.trim()) {
        setDocumentSearchHits([]);
        return;
      }
      setIsDocSearchLoading(true);
      try {
        const res = await api.searchDocument(activeDocumentId, {
          query: q,
          section_id: sectionId,
        });
        setDocumentSearchHits(res.hits);
      } catch (err: any) {
        console.error("Document search failed", err);
      } finally {
        setIsDocSearchLoading(false);
      }
    },
    [activeDocumentId]
  );

  const convertCandidate = useCallback(
    async (
      candidateId: string,
      investigationId: string,
      claimId?: string,
      relationshipType: "SUPPORTS" | "CONTRADICTS" | "CONTEXT" = "SUPPORTS"
    ) => {
      try {
        const evidence = await api.convertEvidenceCandidate({
          candidate_id: candidateId,
          investigation_id: investigationId,
          claim_id: claimId,
          relationship_type: relationshipType,
        });
        if (selectedInvestigationId === investigationId) {
          setEvidenceList((prev) => [evidence, ...prev]);
        }
        setCandidates((prev) => prev.filter((c) => c.candidate_id !== candidateId));
        return evidence;
      } catch (err: any) {
        setGlobalError(err.message || "Failed to convert evidence candidate.");
        throw err;
      }
    },
    [selectedInvestigationId]
  );

  // -------------------------------------------------------------------------
  // Stage 105: Document Comparison State & Handlers
  // -------------------------------------------------------------------------
  const [compareLeftDocId, setCompareLeftDocId] = useState<string>("0000320193-23-000106");
  const [compareRightDocId, setCompareRightDocId] = useState<string>("0000320193-24-000106");
  const [compareMode, setCompareMode] = useState<DocumentComparisonMode>("SECTIONS");
  const [comparisonResult, setComparisonResult] = useState<DocumentComparisonResult | null>(null);
  const [factVariance, setFactVariance] = useState<FinancialFactsCompareResponse | null>(null);
  const [isComparing, setIsComparing] = useState<boolean>(false);

  const executeDocumentComparison = useCallback(
    async (leftId?: string, rightId?: string, mode?: DocumentComparisonMode) => {
      const lId = leftId || compareLeftDocId;
      const rId = rightId || compareRightDocId;
      const cMode = mode || compareMode;
      if (!lId || !rId) return;

      setIsComparing(true);
      setGlobalError(null);
      try {
        const res = await api.compareDocuments({
          left_document_id: lId,
          right_document_id: rId,
          comparison_mode: cMode,
        });
        setComparisonResult(res);
      } catch (err: any) {
        setGlobalError(err.message || "Failed to execute document comparison.");
      } finally {
        setIsComparing(false);
      }
    },
    [compareLeftDocId, compareRightDocId, compareMode]
  );

  const executeFactComparison = useCallback(
    async (entityId: string, leftPeriod: string, rightPeriod: string, concepts?: string[]) => {
      setIsComparing(true);
      setGlobalError(null);
      try {
        const res = await api.compareFinancialFacts({
          entity_id: entityId,
          left_period: leftPeriod,
          right_period: rightPeriod,
          concepts,
        });
        setFactVariance(res);
      } catch (err: any) {
        setGlobalError(err.message || "Failed to compare financial facts.");
      } finally {
        setIsComparing(false);
      }
    },
    []
  );

  // Convenience navigation helpers
  const openDocument = useCallback(
    (docId: string) => {
      setActiveDocumentId(docId);
      loadDocument(docId);
      setActiveTab("DOCUMENT_VIEWER");
    },
    [loadDocument]
  );

  const openComparison = useCallback(
    (leftDocId?: string, rightDocId?: string) => {
      if (leftDocId) setCompareLeftDocId(leftDocId);
      if (rightDocId) setCompareRightDocId(rightDocId);
      executeDocumentComparison(leftDocId, rightDocId);
      setActiveTab("COMPARE");
    },
    [executeDocumentComparison]
  );

  // -------------------------------------------------------------------------
  // Stage 106: Research Analysis & Workbenches State
  // -------------------------------------------------------------------------
  const [analyses, setAnalyses] = useState<ResearchAnalysis[]>([]);
  const [analysesTotal, setAnalysesTotal] = useState<number>(0);
  const [isAnalysesLoading, setIsAnalysesLoading] = useState<boolean>(false);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<ResearchAnalysis | null>(null);
  const [analysisRuns, setAnalysisRuns] = useState<ResearchAnalysisRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [currentRunResult, setCurrentRunResult] = useState<ResearchAnalysisResult | null>(null);
  const [currentRunProvenance, setCurrentRunProvenance] = useState<Record<string, any> | null>(null);
  const [isRunExecuting, setIsRunExecuting] = useState<boolean>(false);
  const [analysisFindings, setAnalysisFindings] = useState<ResearchFinding[]>([]);
  const [analysisAssumptions, setAnalysisAssumptions] = useState<ResearchAssumption[]>([]);
  const [sensitivityResult, setSensitivityResult] = useState<SensitivityAnalysisResponse | null>(null);
  const [isSensitivityLoading, setIsSensitivityLoading] = useState<boolean>(false);
  const [hypothesisEvaluations, setHypothesisEvaluations] = useState<ResearchHypothesisEvaluation[]>([]);
  const [isHypothesisEvaluating, setIsHypothesisEvaluating] = useState<boolean>(false);
  const [analysisTypeCatalog, setAnalysisTypeCatalog] = useState<ResearchAnalysisTypeDefinition[]>([]);
  const [analysisTypeFilter, setAnalysisTypeFilter] = useState<ResearchAnalysisType | undefined>(undefined);
  const [analysisEntityFilter, setAnalysisEntityFilter] = useState<string>("");
  const [analysisSearchQuery, setAnalysisSearchQuery] = useState<string>("");

  const loadAnalysisTypes = useCallback(async () => {
    try {
      const res = await api.listAnalysisTypes();
      setAnalysisTypeCatalog(res.analysis_types);
    } catch (err: any) {
      console.error("Failed to load analysis types catalog", err);
    }
  }, []);

  const loadAnalyses = useCallback(async () => {
    setIsAnalysesLoading(true);
    setGlobalError(null);
    try {
      const res = await api.listAnalyses({
        analysisType: analysisTypeFilter,
        entityId: analysisEntityFilter || undefined,
        search: analysisSearchQuery || undefined,
      });
      setAnalyses(res.analyses);
      setAnalysesTotal(res.total_count);
      if (res.analyses.length > 0 && !selectedAnalysisId) {
        setSelectedAnalysisId(res.analyses[0].analysis_id);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load research analyses.");
    } finally {
      setIsAnalysesLoading(false);
    }
  }, [analysisTypeFilter, analysisEntityFilter, analysisSearchQuery, selectedAnalysisId]);

  const loadAnalysisDetail = useCallback(async (analysisId: string) => {
    setGlobalError(null);
    try {
      const [an, runsRes, findingsRes, assumptionsRes] = await Promise.all([
        api.getAnalysis(analysisId),
        api.listAnalysisRuns(analysisId),
        api.listAnalysisFindings(analysisId),
        api.listAnalysisAssumptions(analysisId),
      ]);
      setCurrentAnalysis(an);
      setAnalysisRuns(runsRes.runs);
      setAnalysisFindings(findingsRes.findings);
      setAnalysisAssumptions(assumptionsRes.assumptions);

      const activeRunId = an.latest_run_id || (runsRes.runs.length > 0 ? runsRes.runs[0].run_id : null);
      if (activeRunId) {
        setSelectedRunId(activeRunId);
        try {
          const [result, prov] = await Promise.all([
            api.getAnalysisRunResults(activeRunId),
            api.getAnalysisRunProvenance(activeRunId),
          ]);
          setCurrentRunResult(result);
          setCurrentRunProvenance(prov);
        } catch (runErr) {
          console.warn("Could not load run results/provenance", runErr);
        }
      } else {
        setSelectedRunId(null);
        setCurrentRunResult(null);
        setCurrentRunProvenance(null);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load analysis detail.");
    }
  }, []);

  const selectRun = useCallback(async (runId: string) => {
    setSelectedRunId(runId);
    try {
      const [result, prov] = await Promise.all([
        api.getAnalysisRunResults(runId),
        api.getAnalysisRunProvenance(runId),
      ]);
      setCurrentRunResult(result);
      setCurrentRunProvenance(prov);
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load run result.");
    }
  }, []);

  const selectAnalysis = useCallback((id: string | null) => {
    setSelectedAnalysisId(id);
    if (!id) {
      setCurrentAnalysis(null);
      setAnalysisRuns([]);
      setSelectedRunId(null);
      setCurrentRunResult(null);
      setCurrentRunProvenance(null);
      setAnalysisFindings([]);
      setAnalysisAssumptions([]);
      setSensitivityResult(null);
    }
  }, []);

  useEffect(() => {
    if (selectedAnalysisId) {
      loadAnalysisDetail(selectedAnalysisId);
    }
  }, [selectedAnalysisId, loadAnalysisDetail]);

  const createAnalysis = async (data: CreateResearchAnalysisDTO) => {
    try {
      const an = await api.createAnalysis(data);
      await loadAnalyses();
      setSelectedAnalysisId(an.analysis_id);
      return an;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create analysis.");
      throw err;
    }
  };

  const updateAnalysis = async (analysisId: string, data: UpdateResearchAnalysisDTO) => {
    try {
      const updated = await api.updateAnalysis(analysisId, data);
      setCurrentAnalysis(updated);
      await loadAnalyses();
      return updated;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update analysis.");
      throw err;
    }
  };

  const duplicateAnalysis = async (analysisId: string) => {
    try {
      const copy = await api.duplicateAnalysis(analysisId);
      await loadAnalyses();
      setSelectedAnalysisId(copy.analysis_id);
      return copy;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to duplicate analysis.");
      throw err;
    }
  };

  const deleteAnalysis = async (analysisId: string) => {
    try {
      await api.deleteAnalysis(analysisId);
      if (selectedAnalysisId === analysisId) {
        setSelectedAnalysisId(null);
      }
      await loadAnalyses();
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete analysis.");
      throw err;
    }
  };

  const executeAnalysisRun = async (analysisId: string, inputPolicy: string = "PINNED_SOURCE_VERSION") => {
    setIsRunExecuting(true);
    setGlobalError(null);
    try {
      const run = await api.executeAnalysisRun(analysisId, inputPolicy);
      const [res, prov, runsRes, an] = await Promise.all([
        api.getAnalysisRunResults(run.run_id),
        api.getAnalysisRunProvenance(run.run_id),
        api.listAnalysisRuns(analysisId),
        api.getAnalysis(analysisId),
      ]);
      setSelectedRunId(run.run_id);
      setCurrentRunResult(res);
      setCurrentRunProvenance(prov);
      setAnalysisRuns(runsRes.runs);
      setCurrentAnalysis(an);
      return run;
    } catch (err: any) {
      setGlobalError(err.message || "Analysis execution failed.");
      throw err;
    } finally {
      setIsRunExecuting(false);
    }
  };

  const createFinding = async (analysisId: string, data: CreateResearchFindingDTO) => {
    try {
      const f = await api.createAnalysisFinding(analysisId, data);
      setAnalysisFindings((prev) => [f, ...prev]);
      return f;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create finding.");
      throw err;
    }
  };

  const updateFinding = async (findingId: string, data: UpdateResearchFindingDTO) => {
    try {
      const updated = await api.updateFinding(findingId, data);
      setAnalysisFindings((prev) => prev.map((f) => (f.finding_id === findingId ? updated : f)));
      return updated;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update finding.");
      throw err;
    }
  };

  const deleteFinding = async (findingId: string) => {
    try {
      await api.deleteFinding(findingId);
      setAnalysisFindings((prev) => prev.filter((f) => f.finding_id !== findingId));
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete finding.");
      throw err;
    }
  };

  const createAssumption = async (analysisId: string, data: CreateResearchAssumptionDTO) => {
    try {
      const as = await api.createAnalysisAssumption(analysisId, data);
      setAnalysisAssumptions((prev) => [...prev, as]);
      return as;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create assumption.");
      throw err;
    }
  };

  const deleteAssumption = async (assumptionId: string) => {
    try {
      await api.deleteAssumption(assumptionId);
      setAnalysisAssumptions((prev) => prev.filter((a) => a.assumption_id !== assumptionId));
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete assumption.");
      throw err;
    }
  };

  const executeSensitivity = async (analysisId: string, data: SensitivityAnalysisRequest) => {
    setIsSensitivityLoading(true);
    setGlobalError(null);
    try {
      const res = await api.executeSensitivityAnalysis(analysisId, data);
      setSensitivityResult(res);
      return res;
    } catch (err: any) {
      setGlobalError(err.message || "Sensitivity analysis failed.");
      throw err;
    } finally {
      setIsSensitivityLoading(false);
    }
  };

  const evaluateHypothesis = async (hypothesisId: string, data: ExecuteHypothesisEvaluationDTO) => {
    setIsHypothesisEvaluating(true);
    setGlobalError(null);
    try {
      const ev = await api.executeHypothesisEvaluation(hypothesisId, data);
      setHypothesisEvaluations((prev) => [ev, ...prev]);
      return ev;
    } catch (err: any) {
      setGlobalError(err.message || "Hypothesis evaluation failed.");
      throw err;
    } finally {
      setIsHypothesisEvaluating(false);
    }
  };

  // -------------------------------------------------------------------------
  // Navigation & Triggers
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (activeTab === "OVERVIEW") {
      loadOverview();
    } else if (activeTab === "INVESTIGATIONS") {
      loadInvestigations();
    } else if (activeTab === "ANALYSIS") {
      loadAnalysisTypes();
      loadAnalyses();
    } else if (activeTab === "DISCOVERY") {
      loadSourceTypes();
      if (discoveryResults.length === 0) {
        searchDiscovery({ text_query: "" });
      }
    } else if (activeTab === "DOCUMENT_VIEWER") {
      if (!activeDocument) {
        loadDocument(activeDocumentId || "0000320193-24-000106");
      }
    } else if (activeTab === "COMPARE") {
      if (!comparisonResult) {
        executeDocumentComparison();
      }
    }
  }, [
    activeTab,
    loadOverview,
    loadInvestigations,
    loadAnalysisTypes,
    loadAnalyses,
    loadSourceTypes,
    discoveryResults.length,
    searchDiscovery,
    activeDocument,
    activeDocumentId,
    loadDocument,
    comparisonResult,
    executeDocumentComparison,
  ]);

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

    // Stage 105: Source Discovery
    discoveryQuery,
    setDiscoveryQuery,
    discoveryResults,
    discoveryTotal,
    isDiscoveryLoading,
    sourceTypes,
    loadSourceTypes,
    searchDiscovery,

    // Stage 105: Document Intelligence & Viewer
    activeDocumentId,
    setActiveDocumentId,
    activeDocument,
    documentProcessingStatus,
    documentOutline,
    activeDocumentSectionId,
    setActiveDocumentSectionId,
    activeDocumentSection,
    documentTables,
    documentSearchQuery,
    setDocumentSearchQuery,
    documentSearchHits,
    isDocSearchLoading,
    candidates,
    isDocumentLoading,
    loadDocument,
    selectDocumentSection,
    searchInDocument,
    convertCandidate,

    // Stage 105: Document Comparison
    compareLeftDocId,
    setCompareLeftDocId,
    compareRightDocId,
    setCompareRightDocId,
    compareMode,
    setCompareMode,
    comparisonResult,
    factVariance,
    isComparing,
    executeDocumentComparison,
    executeFactComparison,

    // Navigation Shortcuts
    openDocument,
    openComparison,

    // Stage 106: Research Analysis & Workbenches
    analyses,
    analysesTotal,
    isAnalysesLoading,
    selectedAnalysisId,
    setSelectedAnalysisId,
    selectAnalysis,
    currentAnalysis,
    analysisRuns,
    selectedRunId,
    selectRun,
    currentRunResult,
    currentRunProvenance,
    isRunExecuting,
    analysisFindings,
    analysisAssumptions,
    sensitivityResult,
    isSensitivityLoading,
    hypothesisEvaluations,
    isHypothesisEvaluating,
    analysisTypeCatalog,
    analysisTypeFilter,
    setAnalysisTypeFilter,
    analysisEntityFilter,
    setAnalysisEntityFilter,
    analysisSearchQuery,
    setAnalysisSearchQuery,
    loadAnalyses,
    createAnalysis,
    updateAnalysis,
    duplicateAnalysis,
    deleteAnalysis,
    executeAnalysisRun,
    createFinding,
    updateFinding,
    deleteFinding,
    createAssumption,
    deleteAssumption,
    executeSensitivity,
    evaluateHypothesis,

    // Error
    globalError,
    clearError: () => setGlobalError(null),
  };
}
