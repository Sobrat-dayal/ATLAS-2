"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CentralBankBalanceSheetSummaryDTO,
  CentralBankCoverageResponseDTO,
  CentralBankInstitutionDTO,
  CentralBankOverviewDTO,
  CentralBankPolicyProgramDTO,
  CommitteeVotingRecordDTO,
  getCentralBankCoverage,
  getCentralBankOverview,
  getCentralBanks,
  getMeetingVotingRecord,
  getPolicyDecisions,
  getPolicyInstruments,
  getPolicyMeetings,
  getPolicyPrograms,
  getPolicyTimeline,
  getPublications,
  getSpeeches,
  MonetaryPolicyDecisionDTO,
  MonetaryPolicyMeetingDTO,
  OfficialForwardGuidanceDTO,
  OfficialPublicationDTO,
  OfficialSpeechDTO,
  PolicyInstrumentDTO,
  PolicyTimelineEventDTO,
} from "@/lib/economics/central-banks";

export type CentralBankSectionTab =
  | "overview"
  | "rates"
  | "decisions"
  | "meetings"
  | "publications"
  | "speeches"
  | "balance-sheet"
  | "programs"
  | "timeline"
  | "coverage";

export interface UseCentralBanksReturn {
  // Navigation & Active State
  selectedBankId: string;
  selectCentralBank: (bankId: string) => void;
  activeTab: CentralBankSectionTab;
  setActiveTab: (tab: CentralBankSectionTab) => void;

  // Data
  institutions: CentralBankInstitutionDTO[];
  overview: CentralBankOverviewDTO | null;
  instruments: PolicyInstrumentDTO[];
  decisions: MonetaryPolicyDecisionDTO[];
  selectedDecisionId: string | null;
  selectDecision: (decisionId: string | null) => void;
  selectedDecision: MonetaryPolicyDecisionDTO | null;

  meetings: MonetaryPolicyMeetingDTO[];
  selectedMeetingId: string | null;
  selectMeeting: (meetingId: string | null) => void;
  selectedVotingRecord: CommitteeVotingRecordDTO | null;

  publications: OfficialPublicationDTO[];
  selectedPublicationId: string | null;
  selectPublication: (documentId: string | null) => void;
  selectedPublication: OfficialPublicationDTO | null;

  speeches: OfficialSpeechDTO[];
  guidanceList: OfficialForwardGuidanceDTO[];
  balanceSheet: CentralBankBalanceSheetSummaryDTO | null;
  programs: CentralBankPolicyProgramDTO[];
  timeline: PolicyTimelineEventDTO[];
  coverage: CentralBankCoverageResponseDTO | null;

  // Status
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useCentralBanks(initialBankId: string = "cb-fed"): UseCentralBanksReturn {
  const [selectedBankId, setSelectedBankId] = useState<string>(initialBankId);
  const [activeTab, setActiveTab] = useState<CentralBankSectionTab>("overview");

  const [institutions, setInstitutions] = useState<CentralBankInstitutionDTO[]>([]);
  const [overview, setOverview] = useState<CentralBankOverviewDTO | null>(null);
  const [instruments, setInstruments] = useState<PolicyInstrumentDTO[]>([]);
  const [decisions, setDecisions] = useState<MonetaryPolicyDecisionDTO[]>([]);
  const [selectedDecisionId, setSelectedDecisionId] = useState<string | null>(null);

  const [meetings, setMeetings] = useState<MonetaryPolicyMeetingDTO[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);
  const [selectedVotingRecord, setSelectedVotingRecord] = useState<CommitteeVotingRecordDTO | null>(null);

  const [publications, setPublications] = useState<OfficialPublicationDTO[]>([]);
  const [selectedPublicationId, setSelectedPublicationId] = useState<string | null>(null);

  const [speeches, setSpeeches] = useState<OfficialSpeechDTO[]>([]);
  const [guidanceList, setGuidanceList] = useState<OfficialForwardGuidanceDTO[]>([]);
  const [balanceSheet, setBalanceSheet] = useState<CentralBankBalanceSheetSummaryDTO | null>(null);
  const [programs, setPrograms] = useState<CentralBankPolicyProgramDTO[]>([]);
  const [timeline, setTimeline] = useState<PolicyTimelineEventDTO[]>([]);
  const [coverage, setCoverage] = useState<CentralBankCoverageResponseDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial Load: Institutions List
  useEffect(() => {
    let isMounted = true;
    async function loadInstitutions() {
      try {
        const banks = await getCentralBanks();
        if (isMounted) {
          setInstitutions(banks);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load central banks catalog.");
        }
      }
    }
    loadInstitutions();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2. Load Selected Central Bank Data
  const loadBankData = useCallback(async (bankId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [
        overviewRes,
        instrumentsRes,
        decisionsRes,
        meetingsRes,
        publicationsRes,
        speechesRes,
        programsRes,
        timelineRes,
        coverageRes,
      ] = await Promise.all([
        getCentralBankOverview(bankId),
        getPolicyInstruments(bankId),
        getPolicyDecisions(bankId),
        getPolicyMeetings(bankId),
        getPublications(bankId),
        getSpeeches(bankId),
        getPolicyPrograms(bankId),
        getPolicyTimeline(bankId),
        getCentralBankCoverage(bankId),
      ]);

      setOverview(overviewRes);
      setInstruments(instrumentsRes);
      setDecisions(decisionsRes);
      setMeetings(meetingsRes);
      setPublications(publicationsRes);
      setSpeeches(speechesRes);
      setBalanceSheet(overviewRes.latest_balance_sheet || null);
      setPrograms(programsRes);
      setTimeline(timelineRes);
      setCoverage(coverageRes);
      setGuidanceList(overviewRes.active_forward_guidance ? [overviewRes.active_forward_guidance] : []);

      // Auto-select latest decision & meeting
      if (decisionsRes.length > 0) {
        setSelectedDecisionId(decisionsRes[0].decision_id);
      } else {
        setSelectedDecisionId(null);
      }

      if (meetingsRes.length > 0) {
        setSelectedMeetingId(meetingsRes[0].meeting_id);
      } else {
        setSelectedMeetingId(null);
        setSelectedVotingRecord(null);
      }

      if (publicationsRes.length > 0) {
        setSelectedPublicationId(publicationsRes[0].document_id);
      } else {
        setSelectedPublicationId(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load central bank data.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBankData(selectedBankId);
  }, [selectedBankId, loadBankData]);

  // 3. Load Voting Record when Meeting selection changes
  useEffect(() => {
    let isMounted = true;
    async function loadVoting() {
      if (!selectedMeetingId) {
        setSelectedVotingRecord(null);
        return;
      }
      try {
        const record = await getMeetingVotingRecord(selectedBankId, selectedMeetingId);
        if (isMounted) {
          setSelectedVotingRecord(record);
        }
      } catch {
        if (isMounted) {
          setSelectedVotingRecord(null);
        }
      }
    }
    loadVoting();
    return () => {
      isMounted = false;
    };
  }, [selectedBankId, selectedMeetingId]);

  const selectCentralBank = useCallback((bankId: string) => {
    setSelectedBankId(bankId);
  }, []);

  const selectDecision = useCallback((decisionId: string | null) => {
    setSelectedDecisionId(decisionId);
  }, []);

  const selectMeeting = useCallback((meetingId: string | null) => {
    setSelectedMeetingId(meetingId);
  }, []);

  const selectPublication = useCallback((documentId: string | null) => {
    setSelectedPublicationId(documentId);
  }, []);

  const refresh = useCallback(async () => {
    await loadBankData(selectedBankId);
  }, [loadBankData, selectedBankId]);

  const selectedDecision = decisions.find((d) => d.decision_id === selectedDecisionId) || null;
  const selectedPublication = publications.find((p) => p.document_id === selectedPublicationId) || null;

  return {
    selectedBankId,
    selectCentralBank,
    activeTab,
    setActiveTab,
    institutions,
    overview,
    instruments,
    decisions,
    selectedDecisionId,
    selectDecision,
    selectedDecision,
    meetings,
    selectedMeetingId,
    selectMeeting,
    selectedVotingRecord,
    publications,
    selectedPublicationId,
    selectPublication,
    selectedPublication,
    speeches,
    guidanceList,
    balanceSheet,
    programs,
    timeline,
    coverage,
    isLoading,
    error,
    refresh,
  };
}
