"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ConcentrationResponseDTO,
  fetchConcentration,
  fetchCoverage,
  fetchCustomers,
  fetchFilters,
  fetchHistory,
  fetchNetwork,
  fetchRelationshipDetail,
  fetchRelationshipEvidence,
  fetchSuppliers,
  fetchSupplyChainOverview,
  HistoricalTimelineResponseDTO,
  RelationshipEvidenceDTO,
  SupplyChainCoverageResponseDTO,
  SupplyChainFiltersDTO,
  SupplyChainNetworkResponseDTO,
  SupplyChainOverviewResponseDTO,
  SupplyChainRelationshipDTO,
} from "@/lib/companies/supply-chain";

export type SupplyChainSubTab =
  | "overview"
  | "suppliers"
  | "customers"
  | "network"
  | "concentration"
  | "history"
  | "coverage";

export interface UseCompanySupplyChainReturn {
  activeSubTab: SupplyChainSubTab;
  setActiveSubTab: (tab: SupplyChainSubTab) => void;
  overview: SupplyChainOverviewResponseDTO | null;
  suppliers: SupplyChainRelationshipDTO[];
  customers: SupplyChainRelationshipDTO[];
  network: SupplyChainNetworkResponseDTO | null;
  networkDepth: number;
  setNetworkDepth: (depth: number) => void;
  networkDirection: string;
  setNetworkDirection: (direction: string) => void;
  concentration: ConcentrationResponseDTO | null;
  history: HistoricalTimelineResponseDTO | null;
  coverage: SupplyChainCoverageResponseDTO | null;
  filters: SupplyChainFiltersDTO | null;
  tierFilter: number | null;
  setTierFilter: (tier: number | null) => void;
  relationshipTypeFilter: string | null;
  setRelationshipTypeFilter: (type: string | null) => void;
  countryFilter: string | null;
  setCountryFilter: (country: string | null) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  selectedRelationship: SupplyChainRelationshipDTO | null;
  selectedEvidence: RelationshipEvidenceDTO[];
  isEvidenceLoading: boolean;
  inspectRelationship: (relationshipId: string) => Promise<void>;
  closeInspector: () => void;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useCompanySupplyChain(companyId: string): UseCompanySupplyChainReturn {
  const [activeSubTab, setActiveSubTab] = useState<SupplyChainSubTab>("overview");
  const [overview, setOverview] = useState<SupplyChainOverviewResponseDTO | null>(null);
  const [suppliers, setSuppliers] = useState<SupplyChainRelationshipDTO[]>([]);
  const [customers, setCustomers] = useState<SupplyChainRelationshipDTO[]>([]);
  const [network, setNetwork] = useState<SupplyChainNetworkResponseDTO | null>(null);
  const [networkDepth, setNetworkDepth] = useState<number>(1);
  const [networkDirection, setNetworkDirection] = useState<string>("BOTH");
  const [concentration, setConcentration] = useState<ConcentrationResponseDTO | null>(null);
  const [history, setHistory] = useState<HistoricalTimelineResponseDTO | null>(null);
  const [coverage, setCoverage] = useState<SupplyChainCoverageResponseDTO | null>(null);
  const [filters, setFilters] = useState<SupplyChainFiltersDTO | null>(null);

  // Filter States
  const [tierFilter, setTierFilter] = useState<number | null>(null);
  const [relationshipTypeFilter, setRelationshipTypeFilter] = useState<string | null>(null);
  const [countryFilter, setCountryFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Inspector States
  const [selectedRelationship, setSelectedRelationship] = useState<SupplyChainRelationshipDTO | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<RelationshipEvidenceDTO[]>([]);
  const [isEvidenceLoading, setIsEvidenceLoading] = useState<boolean>(false);

  // Loading & Error
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);

    try {
      const [
        overviewRes,
        suppliersRes,
        customersRes,
        networkRes,
        concentrationRes,
        historyRes,
        coverageRes,
        filtersRes,
      ] = await Promise.all([
        fetchSupplyChainOverview(companyId),
        fetchSuppliers(companyId, {
          tier: tierFilter || undefined,
          relationship_type: relationshipTypeFilter || undefined,
          country: countryFilter || undefined,
        }),
        fetchCustomers(companyId, {
          tier: tierFilter || undefined,
          relationship_type: relationshipTypeFilter || undefined,
          country: countryFilter || undefined,
        }),
        fetchNetwork(companyId, {
          depth: networkDepth,
          direction: networkDirection,
          relationship_type: relationshipTypeFilter || undefined,
        }),
        fetchConcentration(companyId),
        fetchHistory(companyId),
        fetchCoverage(companyId),
        fetchFilters(companyId),
      ]);

      setOverview(overviewRes);
      setSuppliers(suppliersRes.suppliers || []);
      setCustomers(customersRes.customers || []);
      setNetwork(networkRes);
      setConcentration(concentrationRes);
      setHistory(historyRes);
      setCoverage(coverageRes);
      setFilters(filtersRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load supply chain intelligence";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [companyId, networkDepth, networkDirection, tierFilter, relationshipTypeFilter, countryFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const inspectRelationship = useCallback(
    async (relationshipId: string) => {
      setIsEvidenceLoading(true);
      try {
        const [rel, evList] = await Promise.all([
          fetchRelationshipDetail(companyId, relationshipId),
          fetchRelationshipEvidence(companyId, relationshipId),
        ]);
        setSelectedRelationship(rel);
        setSelectedEvidence(evList);
      } catch (err) {
        console.error("Failed to load relationship evidence:", err);
      } finally {
        setIsEvidenceLoading(false);
      }
    },
    [companyId]
  );

  const closeInspector = useCallback(() => {
    setSelectedRelationship(null);
    setSelectedEvidence([]);
  }, []);

  return {
    activeSubTab,
    setActiveSubTab,
    overview,
    suppliers,
    customers,
    network,
    networkDepth,
    setNetworkDepth,
    networkDirection,
    setNetworkDirection,
    concentration,
    history,
    coverage,
    filters,
    tierFilter,
    setTierFilter,
    relationshipTypeFilter,
    setRelationshipTypeFilter,
    countryFilter,
    setCountryFilter,
    searchQuery,
    setSearchQuery,
    selectedRelationship,
    selectedEvidence,
    isEvidenceLoading,
    inspectRelationship,
    closeInspector,
    isLoading,
    error,
    refresh: loadData,
  };
}
