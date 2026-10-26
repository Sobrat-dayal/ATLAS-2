"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CandidatesResponseDTO,
  CompanyPeerCandidateDTO,
  ComparableObservationDTO,
  createPeerGroup as apiCreatePeerGroup,
  deletePeerGroup as apiDeletePeerGroup,
  fetchHistoricalComparison,
  fetchMetricCatalog,
  fetchPeerCandidates,
  fetchPeerComparison,
  fetchPeerMethodology,
  fetchPeersOverview,
  fetchUserPeerGroups,
  HistoricalComparisonResponseDTO,
  OutlierPolicy,
  PeerComparisonResponseDTO,
  PeerMethodologyResponseDTO,
  PeerMetricDefinitionDTO,
  PeersOverviewResponseDTO,
  PeriodAlignmentMode,
  SubjectInclusionPolicy,
  updatePeerGroup as apiUpdatePeerGroup,
  UserPeerGroupDTO,
} from "@/lib/companies/peers";

export type PeersSubTab =
  | "overview"
  | "discovery"
  | "financial"
  | "valuation"
  | "historical"
  | "groups";

export interface UseCompanyPeersReturn {
  activeSubTab: PeersSubTab;
  setActiveSubTab: (tab: PeersSubTab) => void;
  overview: PeersOverviewResponseDTO | null;
  candidates: CompanyPeerCandidateDTO[];
  competitorsOnly: boolean;
  setCompetitorsOnly: (val: boolean) => void;
  peerGroups: UserPeerGroupDTO[];
  selectedGroupId: string | null;
  setSelectedGroupId: (id: string | null) => void;
  selectedPeerIds: string[];
  setSelectedPeerIds: (ids: string[]) => void;
  addPeerId: (companyId: string) => void;
  removePeerId: (companyId: string) => void;
  metricCatalog: PeerMetricDefinitionDTO[];
  comparison: PeerComparisonResponseDTO | null;
  historical: HistoricalComparisonResponseDTO | null;
  methodology: PeerMethodologyResponseDTO | null;
  periodAlignmentMode: PeriodAlignmentMode;
  setPeriodAlignmentMode: (mode: PeriodAlignmentMode) => void;
  fiscalPeriod: string;
  setFiscalPeriod: (period: string) => void;
  outlierPolicy: OutlierPolicy;
  setOutlierPolicy: (policy: OutlierPolicy) => void;
  subjectInclusionPolicy: SubjectInclusionPolicy;
  setSubjectInclusionPolicy: (policy: SubjectInclusionPolicy) => void;
  activeInspectorObservation: ComparableObservationDTO | null;
  setActiveInspectorObservation: (obs: ComparableObservationDTO | null) => void;
  isLoading: boolean;
  isComparing: boolean;
  isMutatingGroup: boolean;
  error: string | null;
  refreshComparison: () => Promise<void>;
  createGroup: (name: string, description?: string, peerIds?: string[]) => Promise<UserPeerGroupDTO>;
  updateGroup: (groupId: string, name?: string, peerIds?: string[], expectedRevision?: number) => Promise<UserPeerGroupDTO>;
  deleteGroup: (groupId: string) => Promise<void>;
}

export function useCompanyPeers(companyId: string): UseCompanyPeersReturn {
  const [activeSubTab, setActiveSubTab] = useState<PeersSubTab>("overview");
  const [overview, setOverview] = useState<PeersOverviewResponseDTO | null>(null);
  const [candidates, setCandidates] = useState<CompanyPeerCandidateDTO[]>([]);
  const [competitorsOnly, setCompetitorsOnly] = useState(false);
  const [peerGroups, setPeerGroups] = useState<UserPeerGroupDTO[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [selectedPeerIds, setSelectedPeerIds] = useState<string[]>([]);
  const [metricCatalog, setMetricCatalog] = useState<PeerMetricDefinitionDTO[]>([]);
  const [comparison, setComparison] = useState<PeerComparisonResponseDTO | null>(null);
  const [historical, setHistorical] = useState<HistoricalComparisonResponseDTO | null>(null);
  const [methodology, setMethodology] = useState<PeerMethodologyResponseDTO | null>(null);

  const [periodAlignmentMode, setPeriodAlignmentMode] = useState<PeriodAlignmentMode>("LATEST_COMMON_FISCAL_YEAR");
  const [fiscalPeriod, setFiscalPeriod] = useState<string>("FY2024");
  const [outlierPolicy, setOutlierPolicy] = useState<OutlierPolicy>("ALL_VALID_VALUES");
  const [subjectInclusionPolicy, setSubjectInclusionPolicy] = useState<SubjectInclusionPolicy>("PEERS_ONLY_EXCLUDE_SUBJECT");

  const [activeInspectorObservation, setActiveInspectorObservation] = useState<ComparableObservationDTO | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [isMutatingGroup, setIsMutatingGroup] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial Load: Overview, Candidates, Groups, Metrics, Methodology
  const loadInitialData = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);
    try {
      const [ov, cand, grps, catalog, meth] = await Promise.all([
        fetchPeersOverview(companyId),
        fetchPeerCandidates(companyId, 20, competitorsOnly),
        fetchUserPeerGroups(companyId),
        fetchMetricCatalog(companyId),
        fetchPeerMethodology(companyId),
      ]);

      setOverview(ov);
      setCandidates(cand.items);
      setPeerGroups(grps);
      setMetricCatalog(catalog.items);
      setMethodology(meth);

      // Default selected group
      const initialGroup = ov.default_peer_group || (grps.length > 0 ? grps[0] : null);
      if (initialGroup) {
        setSelectedGroupId(initialGroup.id);
        setSelectedPeerIds(initialGroup.peer_company_ids);
      } else {
        // Fallback to top 4 candidate IDs
        const topCandidateIds = cand.items.slice(0, 4).map((c) => c.candidate_company_id);
        setSelectedPeerIds(topCandidateIds);
      }
    } catch (err: any) {
      console.error("Failed to load company peers initial data:", err);
      setError(err.message || "Failed to load peer benchmarking data");
    } finally {
      setIsLoading(false);
    }
  }, [companyId, competitorsOnly]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Fetch Comparison whenever peer selection, group, period, or outlier policy changes
  const refreshComparison = useCallback(async () => {
    if (!companyId || selectedPeerIds.length === 0) return;
    setIsComparing(true);
    try {
      const compRes = await fetchPeerComparison(companyId, {
        peer_group_id: selectedGroupId,
        peer_company_ids: selectedPeerIds,
        period_alignment_mode: periodAlignmentMode,
        fiscal_period: fiscalPeriod,
        outlier_policy: outlierPolicy,
        subject_inclusion_policy: subjectInclusionPolicy,
      });
      setComparison(compRes);

      // Also fetch historical trend series for top metrics
      const histRes = await fetchHistoricalComparison(companyId, {
        peer_company_ids: selectedPeerIds,
        metric_ids: [
          "scale.revenue",
          "growth.revenue_growth",
          "profitability.operating_margin",
          "valuation.pe",
        ],
        max_periods: 5,
      });
      setHistorical(histRes);
    } catch (err: any) {
      console.error("Failed to refresh peer comparison:", err);
      // We don't blow up the whole screen, but record error if needed
    } finally {
      setIsComparing(false);
    }
  }, [
    companyId,
    selectedPeerIds,
    selectedGroupId,
    periodAlignmentMode,
    fiscalPeriod,
    outlierPolicy,
    subjectInclusionPolicy,
  ]);

  useEffect(() => {
    if (selectedPeerIds.length > 0) {
      refreshComparison();
    }
  }, [refreshComparison, selectedPeerIds]);

  // 3. Candidate Peer Selection Handlers
  const addPeerId = useCallback(
    (targetId: string) => {
      if (targetId === companyId) return; // Prevent self-selection
      if (!selectedPeerIds.includes(targetId)) {
        if (selectedPeerIds.length >= 25) {
          alert("Maximum 25 peer companies permitted per institutional peer group.");
          return;
        }
        setSelectedPeerIds([...selectedPeerIds, targetId]);
      }
    },
    [companyId, selectedPeerIds]
  );

  const removePeerId = useCallback(
    (targetId: string) => {
      setSelectedPeerIds(selectedPeerIds.filter((id) => id !== targetId));
    },
    [selectedPeerIds]
  );

  // 4. Peer Group Management Handlers
  const createGroup = useCallback(
    async (name: string, description?: string, peerIds?: string[]): Promise<UserPeerGroupDTO> => {
      setIsMutatingGroup(true);
      try {
        const newGroup = await apiCreatePeerGroup(companyId, {
          name,
          description,
          peer_company_ids: peerIds || selectedPeerIds,
        });
        setPeerGroups((prev) => [...prev, newGroup]);
        setSelectedGroupId(newGroup.id);
        setSelectedPeerIds(newGroup.peer_company_ids);
        return newGroup;
      } finally {
        setIsMutatingGroup(false);
      }
    },
    [companyId, selectedPeerIds]
  );

  const updateGroup = useCallback(
    async (
      groupId: string,
      name?: string,
      peerIds?: string[],
      expectedRevision?: number
    ): Promise<UserPeerGroupDTO> => {
      setIsMutatingGroup(true);
      try {
        const updated = await apiUpdatePeerGroup(companyId, groupId, {
          name,
          peer_company_ids: peerIds,
          expected_revision: expectedRevision,
        });
        setPeerGroups((prev) => prev.map((g) => (g.id === groupId ? updated : g)));
        if (selectedGroupId === groupId) {
          setSelectedPeerIds(updated.peer_company_ids);
        }
        return updated;
      } finally {
        setIsMutatingGroup(false);
      }
    },
    [companyId, selectedGroupId]
  );

  const deleteGroup = useCallback(
    async (groupId: string): Promise<void> => {
      setIsMutatingGroup(true);
      try {
        await apiDeletePeerGroup(companyId, groupId);
        setPeerGroups((prev) => prev.filter((g) => g.id !== groupId));
        if (selectedGroupId === groupId) {
          const remaining = peerGroups.filter((g) => g.id !== groupId);
          if (remaining.length > 0) {
            setSelectedGroupId(remaining[0].id);
            setSelectedPeerIds(remaining[0].peer_company_ids);
          } else {
            setSelectedGroupId(null);
          }
        }
      } finally {
        setIsMutatingGroup(false);
      }
    },
    [companyId, peerGroups, selectedGroupId]
  );

  return {
    activeSubTab,
    setActiveSubTab,
    overview,
    candidates,
    competitorsOnly,
    setCompetitorsOnly,
    peerGroups,
    selectedGroupId,
    setSelectedGroupId,
    selectedPeerIds,
    setSelectedPeerIds,
    addPeerId,
    removePeerId,
    metricCatalog,
    comparison,
    historical,
    methodology,
    periodAlignmentMode,
    setPeriodAlignmentMode,
    fiscalPeriod,
    setFiscalPeriod,
    outlierPolicy,
    setOutlierPolicy,
    subjectInclusionPolicy,
    setSubjectInclusionPolicy,
    activeInspectorObservation,
    setActiveInspectorObservation,
    isLoading,
    isComparing,
    isMutatingGroup,
    error,
    refreshComparison,
    createGroup,
    updateGroup,
    deleteGroup,
  };
}
