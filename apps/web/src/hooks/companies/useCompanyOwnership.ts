"use client";

import { useCallback, useEffect, useState } from "react";
import {
  BeneficialOwnerDTO,
  CompanyOwnershipOverviewDTO,
  fetchBeneficialOwners,
  fetchInsiderHoldings,
  fetchInstitutionalHoldings,
  fetchOwnershipChanges,
  fetchOwnershipHistory,
  fetchOwnershipOverview,
  fetchShareholdingPatterns,
  HistoricalOwnershipSnapshotDTO,
  InsiderHoldingDTO,
  InstitutionalHoldingDTO,
  OwnershipChangeDTO,
  ShareholdingPatternDTO,
} from "@/lib/companies/ownership";

export type OwnershipSubTab =
  | "overview"
  | "institutional"
  | "insiders"
  | "beneficial"
  | "patterns"
  | "history"
  | "changes";

export interface UseCompanyOwnershipReturn {
  activeSubTab: OwnershipSubTab;
  setActiveSubTab: (tab: OwnershipSubTab) => void;
  selectedSecurityId: string | undefined;
  setSelectedSecurityId: (id: string) => void;
  selectedPeriod: string | undefined;
  setSelectedPeriod: (period: string) => void;
  overview: CompanyOwnershipOverviewDTO | null;
  institutions: InstitutionalHoldingDTO[];
  insiders: InsiderHoldingDTO[];
  beneficialOwners: BeneficialOwnerDTO[];
  patterns: ShareholdingPatternDTO | null;
  historySnapshots: HistoricalOwnershipSnapshotDTO[];
  changes: OwnershipChangeDTO[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useCompanyOwnership(companyId: string): UseCompanyOwnershipReturn {
  const [activeSubTab, setActiveSubTab] = useState<OwnershipSubTab>("overview");
  const [selectedSecurityId, setSelectedSecurityId] = useState<string | undefined>();
  const [selectedPeriod, setSelectedPeriod] = useState<string | undefined>();

  const [overview, setOverview] = useState<CompanyOwnershipOverviewDTO | null>(null);
  const [institutions, setInstitutions] = useState<InstitutionalHoldingDTO[]>([]);
  const [insiders, setInsiders] = useState<InsiderHoldingDTO[]>([]);
  const [beneficialOwners, setBeneficialOwners] = useState<BeneficialOwnerDTO[]>([]);
  const [patterns, setPatterns] = useState<ShareholdingPatternDTO | null>(null);
  const [historySnapshots, setHistorySnapshots] = useState<HistoricalOwnershipSnapshotDTO[]>([]);
  const [changes, setChanges] = useState<OwnershipChangeDTO[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);

    try {
      // 1. Always load Overview
      const ov = await fetchOwnershipOverview(companyId, selectedSecurityId, selectedPeriod);
      setOverview(ov);

      if (!selectedSecurityId && ov.selected_security?.security_id) {
        setSelectedSecurityId(ov.selected_security.security_id);
      }
      if (!selectedPeriod && ov.reporting_period) {
        setSelectedPeriod(ov.reporting_period);
      }

      // 2. Load tab-specific data concurrently
      const promises: Promise<any>[] = [];

      promises.push(
        fetchInstitutionalHoldings(companyId, {
          securityId: selectedSecurityId,
          reportingPeriod: selectedPeriod,
        })
          .then((res) => setInstitutions(res.items))
          .catch(() => setInstitutions([]))
      );

      promises.push(
        fetchInsiderHoldings(companyId, {
          securityId: selectedSecurityId,
          reportingPeriod: selectedPeriod,
        })
          .then((res) => setInsiders(res.items))
          .catch(() => setInsiders([]))
      );

      promises.push(
        fetchBeneficialOwners(companyId, {
          securityId: selectedSecurityId,
          reportingPeriod: selectedPeriod,
        })
          .then((res) => setBeneficialOwners(res.items))
          .catch(() => setBeneficialOwners([]))
      );

      promises.push(
        fetchShareholdingPatterns(companyId, selectedPeriod)
          .then((res) => setPatterns(res))
          .catch(() => setPatterns(null))
      );

      promises.push(
        fetchOwnershipHistory(companyId, selectedSecurityId)
          .then((res) => setHistorySnapshots(res.snapshots))
          .catch(() => setHistorySnapshots([]))
      );

      promises.push(
        fetchOwnershipChanges(companyId, {
          securityId: selectedSecurityId,
          currentPeriod: selectedPeriod,
        })
          .then((res) => setChanges(res.items))
          .catch(() => setChanges([]))
      );

      await Promise.all(promises);
    } catch (err: any) {
      setError(err?.message || "Failed to load ownership intelligence data.");
    } finally {
      setIsLoading(false);
    }
  }, [companyId, selectedSecurityId, selectedPeriod]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    activeSubTab,
    setActiveSubTab,
    selectedSecurityId,
    setSelectedSecurityId,
    selectedPeriod,
    setSelectedPeriod,
    overview,
    institutions,
    insiders,
    beneficialOwners,
    patterns,
    historySnapshots,
    changes,
    isLoading,
    error,
    refresh: loadData,
  };
}
