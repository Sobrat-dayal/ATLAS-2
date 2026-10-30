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
  // Stage 107 Types
  ResearchReport,
  ResearchReportSection,
  ResearchReportContentBlock,
  ResearchReportTemplate,
  ResearchReportRevision,
  ResearchReportVerification,
  ResearchReportExport,
  ResearchInvestmentThesis,
  ResearchThesisArgument,
  CreateResearchReportDTO,
  UpdateResearchReportDTO,
  FinalizeResearchReportDTO,
  CreateReportSectionDTO,
  UpdateReportSectionDTO,
  ReorderReportSectionsDTO,
  VerifyReportDTO,
  CreateReportExportDTO,
  CreateThesisDTO,
  UpdateThesisDTO,
  CreateThesisArgumentDTO,
  ResearchReportType,
  ReportLifecycleStatus,
  ThesisLifecycleStatus,
  ThesisArgumentType,
  ExportFormat,
  // Stage 108 Types
  ResearchRole,
  ResearchResourceType,
  ReviewStatus,
  ReviewDecisionType,
  CommentThreadStatus,
  ResearchAccessGrantResponse,
  CreateAccessGrantRequest,
  UpdateAccessGrantRequest,
  ResearchReviewRequestResponse,
  CreateReviewRequest,
  CreateReviewDecisionRequest,
  ResearchCommentThreadResponse,
  CreateCommentThreadRequest,
  QualityGateResultResponse,
  ResearchInternalCirculationResponse,
  CreateCirculationRequest,
  ResearchApprovalStatusResponse,
  // Stage 109 Types
  CreateRevalidationRequest,
  CreateResearchUpdateItemRequest,
  ResearchDependencyLineageResponse,
  ResearchImpactAssessmentResponse,
  ResearchKnowledgeEntryResponse,
  ResearchKnowledgeSearchQuery,
  ResearchOverviewSummaryResponse,
  ResearchRevalidationResultResponse,
  ResearchSourceChangeEventResponse,
  ResearchUpdateItemResponse,
  ResolveUpdateItemRequest,
} from "@/lib/research/types";

export type ResearchTabMode =
  | "OVERVIEW"
  | "KNOWLEDGE"
  | "UPDATES"
  | "REVIEWS"
  | "REPORTS"
  | "THESES"
  | "INVESTIGATIONS"
  | "ANALYSIS"
  | "SOURCES"
  | "DISCOVERY"
  | "DOCUMENT_VIEWER"
  | "COMPARE"
  | "ACTIVITY"
  | "AI_RESEARCH";
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
  // Stage 107: Reports & Theses State
  // -------------------------------------------------------------------------
  const [reports, setReports] = useState<ResearchReport[]>([]);
  const [reportsTotal, setReportsTotal] = useState<number>(0);
  const [isReportsLoading, setIsReportsLoading] = useState<boolean>(false);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [currentReport, setCurrentReport] = useState<ResearchReport | null>(null);
  const [reportSections, setReportSections] = useState<ResearchReportSection[]>([]);
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
  const [reportTemplates, setReportTemplates] = useState<ResearchReportTemplate[]>([]);
  const [reportRevisions, setReportRevisions] = useState<ResearchReportRevision[]>([]);
  const [selectedRevisionId, setSelectedRevisionId] = useState<string | null>(null);
  const [revisionDiff, setRevisionDiff] = useState<any | null>(null);
  const [verificationResult, setVerificationResult] = useState<ResearchReportVerification | null>(null);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [reportExports, setReportExports] = useState<ResearchReportExport[]>([]);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const [theses, setTheses] = useState<ResearchInvestmentThesis[]>([]);
  const [selectedThesisId, setSelectedThesisId] = useState<string | null>(null);
  const [currentThesis, setCurrentThesis] = useState<ResearchInvestmentThesis | null>(null);
  const [thesisArguments, setThesisArguments] = useState<ResearchThesisArgument[]>([]);
  const [isThesesLoading, setIsThesesLoading] = useState<boolean>(false);

  const [reportStatusFilter, setReportStatusFilter] = useState<ReportLifecycleStatus | undefined>(undefined);
  const [reportTypeFilter, setReportTypeFilter] = useState<ResearchReportType | undefined>(undefined);
  const [reportSearchQuery, setReportSearchQuery] = useState<string>("");

  // Stage 108 Reviews & Governance State
  const [reviews, setReviews] = useState<ResearchReviewRequestResponse[]>([]);
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [currentReview, setCurrentReview] = useState<ResearchReviewRequestResponse | null>(null);
  const [isReviewsLoading, setIsReviewsLoading] = useState<boolean>(false);
  const [reviewStatusFilter, setReviewStatusFilter] = useState<ReviewStatus | undefined>(undefined);
  const [participants, setParticipants] = useState<ResearchAccessGrantResponse[]>([]);
  const [isParticipantsLoading, setIsParticipantsLoading] = useState<boolean>(false);
  const [comments, setComments] = useState<ResearchCommentThreadResponse[]>([]);
  const [isCommentsLoading, setIsCommentsLoading] = useState<boolean>(false);
  const [qualityGateResult, setQualityGateResult] = useState<QualityGateResultResponse | null>(null);
  const [isQualityGateRunning, setIsQualityGateRunning] = useState<boolean>(false);
  const [circulations, setCirculations] = useState<ResearchInternalCirculationResponse[]>([]);
  const [isCirculationsLoading, setIsCirculationsLoading] = useState<boolean>(false);
  const [approvalStatus, setApprovalStatus] = useState<ResearchApprovalStatusResponse | null>(null);

  // Stage 109 State: Knowledge Library, Dependency Lineage, Monitoring & Lifecycle
  const [knowledgeEntries, setKnowledgeEntries] = useState<ResearchKnowledgeEntryResponse[]>([]);
  const [knowledgeTotal, setKnowledgeTotal] = useState<number>(0);
  const [isKnowledgeLoading, setIsKnowledgeLoading] = useState<boolean>(false);
  const [knowledgeSearchQuery, setKnowledgeSearchQuery] = useState<string>("");
  const [selectedKnowledgeEntryId, setSelectedKnowledgeEntryId] = useState<string | null>(null);
  const [selectedKnowledgeEntry, setSelectedKnowledgeEntry] = useState<ResearchKnowledgeEntryResponse | null>(null);

  const [dependencyLineage, setDependencyLineage] = useState<ResearchDependencyLineageResponse | null>(null);
  const [isLineageLoading, setIsLineageLoading] = useState<boolean>(false);

  const [sourceChangeEvents, setSourceChangeEvents] = useState<ResearchSourceChangeEventResponse[]>([]);
  const [isSourceChangesLoading, setIsSourceChangesLoading] = useState<boolean>(false);
  const [selectedSourceChangeEvent, setSelectedSourceChangeEvent] = useState<ResearchSourceChangeEventResponse | null>(null);
  const [impactAssessments, setImpactAssessments] = useState<ResearchImpactAssessmentResponse[]>([]);
  const [isImpactsLoading, setIsImpactsLoading] = useState<boolean>(false);

  const [updateItems, setUpdateItems] = useState<ResearchUpdateItemResponse[]>([]);
  const [updateItemsTotal, setUpdateItemsTotal] = useState<number>(0);
  const [isUpdateItemsLoading, setIsUpdateItemsLoading] = useState<boolean>(false);
  const [selectedUpdateItemId, setSelectedUpdateItemId] = useState<string | null>(null);

  const [institutionalOverview, setInstitutionalOverview] = useState<ResearchOverviewSummaryResponse | null>(null);
  const [isInstitutionalOverviewLoading, setIsInstitutionalOverviewLoading] = useState<boolean>(false);
  const [revalidations, setRevalidations] = useState<ResearchRevalidationResultResponse[]>([]);
  const [isRevalidating, setIsRevalidating] = useState<boolean>(false);

  const loadReportTemplates = useCallback(async () => {
    try {
      const res = await api.listReportTemplates();
      setReportTemplates(res.templates);
    } catch (err: any) {
      console.error("Failed to load report templates", err);
    }
  }, []);

  const loadReports = useCallback(async () => {
    setIsReportsLoading(true);
    setGlobalError(null);
    try {
      const res = await api.listReports({
        report_type: reportTypeFilter,
        status: reportStatusFilter,
      });
      let filteredReports = res.reports;
      if (reportSearchQuery) {
        const q = reportSearchQuery.toLowerCase();
        filteredReports = filteredReports.filter(
          (r) =>
            r.title.toLowerCase().includes(q) ||
            r.target_entity_name?.toLowerCase().includes(q) ||
            r.primary_author?.toLowerCase().includes(q)
        );
      }
      setReports(filteredReports);
      setReportsTotal(filteredReports.length);
      if (filteredReports.length > 0 && !selectedReportId) {
        setSelectedReportId(filteredReports[0].report_id);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load research reports.");
    } finally {
      setIsReportsLoading(false);
    }
  }, [reportTypeFilter, reportStatusFilter, reportSearchQuery, selectedReportId]);

  const loadReportDetail = useCallback(async (reportId: string) => {
    setGlobalError(null);
    try {
      const [rep, secs, revsRes] = await Promise.all([
        api.getReport(reportId),
        api.listReportSections(reportId),
        api.listReportRevisions(reportId),
      ]);
      setCurrentReport(rep);
      setReportSections(secs);
      setReportRevisions(revsRes.revisions);
      if (secs.length > 0 && !selectedSectionId) {
        setSelectedSectionId(secs[0].section_id);
      }
      try {
        const ver = await api.getLatestVerification(reportId);
        setVerificationResult(ver);
      } catch {
        setVerificationResult(null);
      }
      try {
        const exps = await api.listReportExports(reportId);
        setReportExports(exps.exports);
      } catch {
        setReportExports([]);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load report details.");
    }
  }, [selectedSectionId]);

  const selectReport = (id: string | null) => {
    setSelectedReportId(id);
    setSelectedSectionId(null);
    setRevisionDiff(null);
    setVerificationResult(null);
  };

  const createReport = async (data: CreateResearchReportDTO) => {
    try {
      const rep = await api.createReport(data);
      await loadReports();
      setSelectedReportId(rep.report_id);
      return rep;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create report.");
      throw err;
    }
  };

  const updateReport = async (reportId: string, data: UpdateResearchReportDTO) => {
    try {
      const updated = await api.updateReport(reportId, data);
      setCurrentReport(updated);
      setReports((prev) => prev.map((r) => (r.report_id === reportId ? updated : r)));
      return updated;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update report.");
      throw err;
    }
  };

  const finalizeReport = async (reportId: string, data: FinalizeResearchReportDTO) => {
    try {
      const fin = await api.finalizeReport(reportId, {
        expected_revision: data.expected_revision,
        change_summary: data.publication_notes,
      });
      setCurrentReport(fin);
      setReports((prev) => prev.map((r) => (r.report_id === reportId ? fin : r)));
      return fin;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to finalize report.");
      throw err;
    }
  };

  const deleteReport = async (reportId: string) => {
    try {
      await api.deleteReport(reportId);
      setReports((prev) => prev.filter((r) => r.report_id !== reportId));
      if (selectedReportId === reportId) {
        setSelectedReportId(null);
        setCurrentReport(null);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete report.");
      throw err;
    }
  };

  const createReportSection = async (reportId: string, data: CreateReportSectionDTO) => {
    try {
      const sec = await api.createReportSection(reportId, data);
      setReportSections((prev) => [...prev, sec]);
      setSelectedSectionId(sec.section_id);
      return sec;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create section.");
      throw err;
    }
  };

  const updateReportSection = async (sectionId: string, data: UpdateReportSectionDTO) => {
    try {
      const repId = selectedReportId || "";
      const sec = await api.updateReportSection(repId, sectionId, data);
      setReportSections((prev) => prev.map((s) => (s.section_id === sectionId ? sec : s)));
      return sec;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update section.");
      throw err;
    }
  };

  const deleteReportSection = async (sectionId: string) => {
    try {
      const repId = selectedReportId || "";
      await api.deleteReportSection(repId, sectionId);
      setReportSections((prev) => prev.filter((s) => s.section_id !== sectionId));
      if (selectedSectionId === sectionId) {
        setSelectedSectionId(null);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete section.");
      throw err;
    }
  };

  const reorderReportSections = async (reportId: string, data: ReorderReportSectionsDTO) => {
    try {
      const ordered = await api.reorderReportSections(reportId, data.ordered_section_ids);
      setReportSections(ordered);
      return ordered;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to reorder sections.");
      throw err;
    }
  };

  const compareReportRevisions = async (reportId: string, baseRev: number, targetRev: number) => {
    try {
      const diff = await api.compareReportRevisions(reportId, baseRev, targetRev);
      setRevisionDiff(diff);
      return diff;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to compare revisions.");
      throw err;
    }
  };

  const verifyReport = async (reportId: string, data: VerifyReportDTO = {}) => {
    setIsVerifying(true);
    setGlobalError(null);
    try {
      const ver = await api.verifyReport(reportId, data.expected_revision);
      setVerificationResult(ver);
      return ver;
    } catch (err: any) {
      setGlobalError(err.message || "Report verification failed.");
      throw err;
    } finally {
      setIsVerifying(false);
    }
  };

  const createReportExport = async (reportId: string, data: CreateReportExportDTO) => {
    setIsExporting(true);
    setGlobalError(null);
    try {
      const exp = await api.createReportExport(reportId, data);
      setReportExports((prev) => [exp, ...prev]);
      return exp;
    } catch (err: any) {
      setGlobalError(err.message || "Export generation failed.");
      throw err;
    } finally {
      setIsExporting(false);
    }
  };

  const loadTheses = useCallback(async () => {
    setIsThesesLoading(true);
    try {
      const res = await api.listTheses();
      setTheses(res);
      if (res.length > 0 && !selectedThesisId) {
        setSelectedThesisId(res[0].thesis_id);
      }
    } catch (err: any) {
      console.error("Failed to load investment theses", err);
    } finally {
      setIsThesesLoading(false);
    }
  }, [selectedThesisId]);

  const loadThesisDetail = useCallback(async (thesisId: string) => {
    try {
      const th = await api.getThesis(thesisId);
      setCurrentThesis(th);
      setThesisArguments(th.arguments || []);
    } catch (err: any) {
      setGlobalError(err.message || "Failed to load thesis details.");
    }
  }, []);

  const selectThesis = (id: string | null) => {
    setSelectedThesisId(id);
  };

  const createThesis = async (data: CreateThesisDTO) => {
    try {
      const th = await api.createThesis({
        thesis_statement: data.thesis_statement || data.title,
        time_horizon: `${data.horizon_months || 12}M`,
        primary_subject_id: data.target_entity_id,
        investigation_id: data.investigation_id,
        bull_case_summary: data.summary,
      });
      await loadTheses();
      setSelectedThesisId(th.thesis_id);
      return th;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create thesis.");
      throw err;
    }
  };

  const updateThesis = async (thesisId: string, data: UpdateThesisDTO) => {
    try {
      const th = await api.updateThesis(thesisId, {
        expected_revision: data.expected_revision ?? currentThesis?.current_revision ?? 1,
        thesis_statement: data.title || currentThesis?.thesis_statement,
        status: data.status,
      });
      setCurrentThesis(th);
      setTheses((prev) => prev.map((t) => (t.thesis_id === thesisId ? th : t)));
      return th;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to update thesis.");
      throw err;
    }
  };

  const deleteThesis = async (thesisId: string) => {
    try {
      await api.deleteThesis(thesisId);
      setTheses((prev) => prev.filter((t) => t.thesis_id !== thesisId));
      if (selectedThesisId === thesisId) {
        setSelectedThesisId(null);
        setCurrentThesis(null);
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete thesis.");
      throw err;
    }
  };

  const createThesisArgument = async (thesisId: string, data: CreateThesisArgumentDTO) => {
    try {
      const arg = await api.createThesisArgument(thesisId, data);
      setThesisArguments((prev) => [...prev, arg]);
      if (currentThesis) {
        setCurrentThesis({
          ...currentThesis,
          arguments: [...(currentThesis.arguments || []), arg],
        });
      }
      return arg;
    } catch (err: any) {
      setGlobalError(err.message || "Failed to create thesis argument.");
      throw err;
    }
  };

  const deleteThesisArgument = async (argumentId: string) => {
    try {
      const thId = selectedThesisId || "";
      await api.deleteThesisArgument(thId, argumentId);
      setThesisArguments((prev) => prev.filter((a) => a.argument_id !== argumentId));
      if (currentThesis && currentThesis.arguments) {
        setCurrentThesis({
          ...currentThesis,
          arguments: currentThesis.arguments.filter((a: ResearchThesisArgument) => a.argument_id !== argumentId),
        });
      }
    } catch (err: any) {
      setGlobalError(err.message || "Failed to delete thesis argument.");
      throw err;
    }
  };

  // -------------------------------------------------------------------------
  // Stage 108 Review, Quality Gates, Comments & Circulation Actions
  // -------------------------------------------------------------------------
  const loadReviews = useCallback(async (targetId?: string) => {
    setIsReviewsLoading(true);
    setGlobalError(null);
    try {
      const res = await api.listReviewRequests({
        targetId: targetId || (selectedReportId ?? undefined),
        status: reviewStatusFilter,
      });
      setReviews(res.reviews);
      if (res.reviews.length > 0 && !selectedReviewId) {
        setSelectedReviewId(res.reviews[0].review_request_id);
        setCurrentReview(res.reviews[0]);
      }
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to load review requests.");
    } finally {
      setIsReviewsLoading(false);
    }
  }, [selectedReportId, reviewStatusFilter, selectedReviewId]);

  const selectReview = useCallback(async (reviewId: string) => {
    setSelectedReviewId(reviewId);
    try {
      const rev = await api.getReviewRequest(reviewId);
      setCurrentReview(rev);
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to load review details.");
    }
  }, []);

  const submitReview = useCallback(async (data: CreateReviewRequest) => {
    try {
      const newRev = await api.createReviewRequest(data);
      setReviews((prev) => [newRev, ...prev]);
      setSelectedReviewId(newRev.review_request_id);
      setCurrentReview(newRev);
      return newRev;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to submit review request.");
      throw err;
    }
  }, []);

  const decideReview = useCallback(async (reviewId: string, data: CreateReviewDecisionRequest) => {
    try {
      const dec = await api.decideReview(reviewId, data);
      await selectReview(reviewId);
      await loadReviews();
      return dec;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to record review decision.");
      throw err;
    }
  }, [selectReview, loadReviews]);

  const cancelReview = useCallback(async (reviewId: string) => {
    try {
      const res = await api.cancelReviewRequest(reviewId);
      await selectReview(reviewId);
      await loadReviews();
      return res;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to cancel review request.");
      throw err;
    }
  }, [selectReview, loadReviews]);

  const loadParticipants = useCallback(async (resourceType: ResearchResourceType, resourceId: string) => {
    setIsParticipantsLoading(true);
    try {
      const res = await api.listResourceParticipants(resourceType, resourceId);
      setParticipants(res.grants);
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to load participants.");
    } finally {
      setIsParticipantsLoading(false);
    }
  }, []);

  const grantParticipant = useCallback(
    async (resourceType: ResearchResourceType, resourceId: string, data: CreateAccessGrantRequest) => {
      try {
        const grant = await api.createResourceParticipant(resourceType, resourceId, data);
        setParticipants((prev) => [grant, ...prev]);
        return grant;
      } catch (err: unknown) {
        setGlobalError(err instanceof Error ? err.message : "Failed to grant access.");
        throw err;
      }
    },
    []
  );

  const updateParticipant = useCallback(async (grantId: string, roleOrData: ResearchRole | UpdateAccessGrantRequest) => {
    try {
      const data: UpdateAccessGrantRequest = typeof roleOrData === "string" ? { role: roleOrData } : roleOrData;
      const updated = await api.updateParticipantGrant(grantId, data);
      setParticipants((prev) => prev.map((g) => (g.grant_id === grantId ? updated : g)));
      return updated;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to update participant role.");
      throw err;
    }
  }, []);

  const revokeParticipant = useCallback(async (grantId: string) => {
    try {
      const revoked = await api.revokeParticipantGrant(grantId);
      setParticipants((prev) => prev.map((g) => (g.grant_id === grantId ? revoked : g)));
      return revoked;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to revoke participant access.");
      throw err;
    }
  }, []);

  const loadComments = useCallback(async (resourceType: string, resourceId: string, revisionNumber?: number) => {
    setIsCommentsLoading(true);
    try {
      const res = await api.listComments(resourceType, resourceId, revisionNumber);
      setComments(res.threads);
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to load comment threads.");
    } finally {
      setIsCommentsLoading(false);
    }
  }, []);

  const createCommentThread = useCallback(
    async (resourceType: string, resourceId: string, data: CreateCommentThreadRequest) => {
      try {
        const thread = await api.createCommentThread(resourceType, resourceId, data);
        setComments((prev) => [thread, ...prev]);
        return thread;
      } catch (err: unknown) {
        setGlobalError(err instanceof Error ? err.message : "Failed to post comment thread.");
        throw err;
      }
    },
    []
  );

  const addCommentReply = useCallback(async (threadId: string, body: string) => {
    try {
      const reply = await api.addCommentReply(threadId, { body });
      setComments((prev) =>
        prev.map((t) => (t.thread_id === threadId ? { ...t, comments: [...t.comments, reply] } : t))
      );
      return reply;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to reply to comment.");
      throw err;
    }
  }, []);

  const resolveCommentThread = useCallback(async (threadId: string) => {
    try {
      const updated = await api.resolveCommentThread(threadId);
      setComments((prev) => prev.map((t) => (t.thread_id === threadId ? updated : t)));
      return updated;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to resolve comment thread.");
      throw err;
    }
  }, []);

  const reopenCommentThread = useCallback(async (threadId: string) => {
    try {
      const updated = await api.reopenCommentThread(threadId);
      setComments((prev) => prev.map((t) => (t.thread_id === threadId ? updated : t)));
      return updated;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to reopen comment thread.");
      throw err;
    }
  }, []);

  const runQualityGate = useCallback(async (reportId: string, revisionNumber?: number) => {
    setIsQualityGateRunning(true);
    try {
      const res = await api.runQualityGate(reportId, { revision_number: revisionNumber });
      setQualityGateResult(res);
      return res;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to evaluate quality gates.");
      throw err;
    } finally {
      setIsQualityGateRunning(false);
    }
  }, []);

  const loadCirculations = useCallback(async (reportId: string) => {
    setIsCirculationsLoading(true);
    try {
      const res = await api.listCirculations(reportId);
      setCirculations(res.circulations);
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to load circulation records.");
    } finally {
      setIsCirculationsLoading(false);
    }
  }, []);

  const circulateReport = useCallback(async (reportId: string, data: CreateCirculationRequest) => {
    try {
      const circ = await api.createCirculation(reportId, data);
      setCirculations((prev) => [circ, ...prev]);
      return circ;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to circulate report.");
      throw err;
    }
  }, []);

  const revokeCirculation = useCallback(async (circulationId: string) => {
    try {
      const revoked = await api.revokeCirculation(circulationId);
      setCirculations((prev) => prev.map((c) => (c.circulation_id === circulationId ? revoked : c)));
      return revoked;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to revoke circulation.");
      throw err;
    }
  }, []);

  const loadApprovalStatus = useCallback(async (reportId: string, revisionNumber?: number) => {
    try {
      const status = await api.getReportApprovalStatus(reportId, revisionNumber);
      setApprovalStatus(status);
      return status;
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : "Failed to check approval status.");
      throw err;
    }
  }, []);

  // -------------------------------------------------------------------------
  // Stage 109 Knowledge, Monitoring & Lifecycle Handlers
  // -------------------------------------------------------------------------
  const loadInstitutionalOverview = useCallback(async () => {
    setIsInstitutionalOverviewLoading(true);
    try {
      const res = await api.getOverviewSummary();
      setInstitutionalOverview(res);
      return res;
    } catch (err: unknown) {
      console.error("Failed to load institutional research overview", err);
    } finally {
      setIsInstitutionalOverviewLoading(false);
    }
  }, []);

  const loadDependencyLineage = useCallback(
    async (resourceType: string, resourceId: string, maxDepth: number = 5) => {
      setIsLineageLoading(true);
      try {
        const res = await api.getDependencyLineage(resourceType, resourceId, maxDepth);
        setDependencyLineage(res);
        return res;
      } catch (err: unknown) {
        console.error("Failed to load dependency lineage", err);
      } finally {
        setIsLineageLoading(false);
      }
    },
    []
  );

  const searchKnowledge = useCallback(
    async (queryParam?: ResearchKnowledgeSearchQuery) => {
      setIsKnowledgeLoading(true);
      try {
        const q = queryParam ?? { query: knowledgeSearchQuery || undefined, limit: 50 };
        const res = await api.searchKnowledge(q);
        setKnowledgeEntries(res.entries);
        setKnowledgeTotal(res.total_count);
        return res;
      } catch (err: unknown) {
        console.error("Failed to search knowledge library", err);
      } finally {
        setIsKnowledgeLoading(false);
      }
    },
    [knowledgeSearchQuery]
  );

  const selectKnowledgeEntry = useCallback(
    async (entryId: string) => {
      setSelectedKnowledgeEntryId(entryId);
      try {
        const res = await api.getKnowledgeEntry(entryId);
        setSelectedKnowledgeEntry(res);
        if (res.referenced_resource_type && res.referenced_resource_id) {
          loadDependencyLineage(res.referenced_resource_type, res.referenced_resource_id);
        }
        return res;
      } catch (err: unknown) {
        console.error("Failed to load knowledge entry", err);
      }
    },
    [loadDependencyLineage]
  );

  const loadSourceChanges = useCallback(async (sourceType?: string) => {
    setIsSourceChangesLoading(true);
    try {
      const res = await api.listSourceChanges({ source_type: sourceType, limit: 50 });
      setSourceChangeEvents(res.events);
      return res;
    } catch (err: unknown) {
      console.error("Failed to load source changes", err);
    } finally {
      setIsSourceChangesLoading(false);
    }
  }, []);

  const selectSourceChangeEvent = useCallback(async (eventId: string) => {
    try {
      const ev = await api.getSourceChange(eventId);
      setSelectedSourceChangeEvent(ev);
      setIsImpactsLoading(true);
      const impRes = await api.listImpacts(eventId);
      setImpactAssessments(impRes.impacts);
      return { event: ev, impacts: impRes.impacts };
    } catch (err: unknown) {
      console.error("Failed to load source change or impacts", err);
    } finally {
      setIsImpactsLoading(false);
    }
  }, []);

  const loadUpdateItems = useCallback(async (params?: { status?: string; priority?: string }) => {
    setIsUpdateItemsLoading(true);
    try {
      const res = await api.listUpdateItems({ ...params, limit: 50 });
      setUpdateItems(res.items);
      setUpdateItemsTotal(res.total_count);
      return res;
    } catch (err: unknown) {
      console.error("Failed to load update items", err);
    } finally {
      setIsUpdateItemsLoading(false);
    }
  }, []);

  const acknowledgeUpdate = useCallback(
    async (updateId: string) => {
      try {
        const res = await api.acknowledgeUpdateItem(updateId);
        await loadUpdateItems();
        await loadInstitutionalOverview();
        return res;
      } catch (err: unknown) {
        console.error("Failed to acknowledge update item", err);
        throw err;
      }
    },
    [loadUpdateItems, loadInstitutionalOverview]
  );

  const resolveUpdate = useCallback(
    async (updateId: string, note: string) => {
      try {
        const res = await api.resolveUpdateItem(updateId, { resolution_note: note });
        await loadUpdateItems();
        await loadInstitutionalOverview();
        return res;
      } catch (err: unknown) {
        console.error("Failed to resolve update item", err);
        throw err;
      }
    },
    [loadUpdateItems, loadInstitutionalOverview]
  );

  const dismissUpdate = useCallback(
    async (updateId: string) => {
      try {
        const res = await api.dismissUpdateItem(updateId);
        await loadUpdateItems();
        await loadInstitutionalOverview();
        return res;
      } catch (err: unknown) {
        console.error("Failed to dismiss update item", err);
        throw err;
      }
    },
    [loadUpdateItems, loadInstitutionalOverview]
  );

  const reopenUpdate = useCallback(
    async (updateId: string) => {
      try {
        const res = await api.reopenUpdateItem(updateId);
        await loadUpdateItems();
        await loadInstitutionalOverview();
        return res;
      } catch (err: unknown) {
        console.error("Failed to reopen update item", err);
        throw err;
      }
    },
    [loadUpdateItems, loadInstitutionalOverview]
  );

  const executeRevalidation = useCallback(
    async (request: CreateRevalidationRequest) => {
      setIsRevalidating(true);
      try {
        const res = await api.runRevalidation(request);
        setRevalidations((prev) => [res, ...prev]);
        await loadUpdateItems();
        await loadInstitutionalOverview();
        return res;
      } catch (err: unknown) {
        console.error("Failed to run automated revalidation", err);
        throw err;
      } finally {
        setIsRevalidating(false);
      }
    },
    [loadUpdateItems, loadInstitutionalOverview]
  );

  // Selection detail hooks
  useEffect(() => {
    if (selectedReportId) {
      loadReportDetail(selectedReportId);
    } else {
      setCurrentReport(null);
      setReportSections([]);
      setReportRevisions([]);
    }
  }, [selectedReportId, loadReportDetail]);

  useEffect(() => {
    if (selectedThesisId) {
      loadThesisDetail(selectedThesisId);
    } else {
      setCurrentThesis(null);
      setThesisArguments([]);
    }
  }, [selectedThesisId, loadThesisDetail]);

  // -------------------------------------------------------------------------
  // Navigation & Triggers
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (activeTab === "OVERVIEW") {
      loadOverview();
      loadInstitutionalOverview();
    } else if (activeTab === "KNOWLEDGE") {
      searchKnowledge();
    } else if (activeTab === "UPDATES") {
      loadUpdateItems();
      loadSourceChanges();
    } else if (activeTab === "REVIEWS") {
      loadReviews();
    } else if (activeTab === "REPORTS") {
      loadReportTemplates();
      loadReports();
      loadTheses();
    } else if (activeTab === "THESES") {
      loadTheses();
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
    loadInstitutionalOverview,
    searchKnowledge,
    loadUpdateItems,
    loadSourceChanges,
    loadReportTemplates,
    loadReports,
    loadTheses,
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

    // Stage 107: Reports & Theses
    reports,
    reportsTotal,
    isReportsLoading,
    selectedReportId,
    setSelectedReportId,
    selectReport,
    currentReport,
    reportSections,
    selectedSectionId,
    setSelectedSectionId,
    reportTemplates,
    reportRevisions,
    selectedRevisionId,
    setSelectedRevisionId,
    revisionDiff,
    verificationResult,
    isVerifying,
    reportExports,
    isExporting,
    theses,
    selectedThesisId,
    setSelectedThesisId,
    selectThesis,
    currentThesis,
    thesisArguments,
    isThesesLoading,
    reportStatusFilter,
    setReportStatusFilter,
    reportTypeFilter,
    setReportTypeFilter,
    reportSearchQuery,
    setReportSearchQuery,
    loadReportTemplates,
    loadReports,
    loadReportDetail,
    createReport,
    updateReport,
    finalizeReport,
    deleteReport,
    createReportSection,
    updateReportSection,
    deleteReportSection,
    reorderReportSections,
    compareReportRevisions,
    verifyReport,
    createReportExport,
    loadTheses,
    loadThesisDetail,
    createThesis,
    updateThesis,
    deleteThesis,
    createThesisArgument,
    deleteThesisArgument,

    // Stage 108 Reviews, Governance & Circulation
    reviews,
    selectedReviewId,
    setSelectedReviewId,
    selectReview,
    currentReview,
    isReviewsLoading,
    reviewStatusFilter,
    setReviewStatusFilter,
    loadReviews,
    submitReview,
    decideReview,
    cancelReview,
    participants,
    isParticipantsLoading,
    loadParticipants,
    grantParticipant,
    updateParticipant,
    revokeParticipant,
    comments,
    isCommentsLoading,
    loadComments,
    createCommentThread,
    addCommentReply,
    resolveCommentThread,
    reopenCommentThread,
    qualityGateResult,
    isQualityGateRunning,
    runQualityGate,
    circulations,
    isCirculationsLoading,
    loadCirculations,
    circulateReport,
    revokeCirculation,
    approvalStatus,
    loadApprovalStatus,

    // Stage 109 Knowledge, Monitoring & Lifecycle
    knowledgeEntries,
    knowledgeTotal,
    isKnowledgeLoading,
    knowledgeSearchQuery,
    setKnowledgeSearchQuery,
    selectedKnowledgeEntryId,
    setSelectedKnowledgeEntryId,
    selectedKnowledgeEntry,
    dependencyLineage,
    isLineageLoading,
    sourceChangeEvents,
    isSourceChangesLoading,
    selectedSourceChangeEvent,
    impactAssessments,
    isImpactsLoading,
    updateItems,
    updateItemsTotal,
    isUpdateItemsLoading,
    selectedUpdateItemId,
    setSelectedUpdateItemId,
    institutionalOverview,
    isInstitutionalOverviewLoading,
    revalidations,
    isRevalidating,
    loadInstitutionalOverview,
    searchKnowledge,
    selectKnowledgeEntry,
    loadDependencyLineage,
    loadSourceChanges,
    selectSourceChangeEvent,
    loadUpdateItems,
    acknowledgeUpdate,
    resolveUpdate,
    dismissUpdate,
    reopenUpdate,
    executeRevalidation,

    // Error
    globalError,
    clearError: () => setGlobalError(null),
  };
}
