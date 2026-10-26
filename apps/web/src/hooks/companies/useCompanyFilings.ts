"use client";

import { useCallback, useEffect, useState } from "react";
import {
  compareFilings,
  fetchFilingCatalog,
  fetchFilingContent,
  fetchFilingCoverage,
  fetchFilingDetail,
  fetchFilingFacts,
  fetchFilingSources,
  fetchFilingsOverview,
  FilingComparisonResponseDTO,
  FilingContentDTO,
  FilingCoverageDTO,
  FilingDetailDTO,
  FilingSearchHitDTO,
  FilingSourceReferenceDTO,
  FilingSummaryDTO,
  FilingsOverviewSummaryDTO,
  searchFilings,
  XBRLFactDTO,
} from "@/lib/companies/filings";

export type FilingsSubTab =
  | "overview"
  | "all"
  | "annual"
  | "quarterly"
  | "events"
  | "ownership"
  | "search"
  | "compare";

export interface UseCompanyFilingsReturn {
  activeSubTab: FilingsSubTab;
  setActiveSubTab: (tab: FilingsSubTab) => void;
  selectedFilingId: string | null;
  setSelectedFilingId: (id: string | null) => void;
  overview: FilingsOverviewSummaryDTO | null;
  coverage: FilingCoverageDTO | null;
  filings: FilingSummaryDTO[];
  totalFilings: number;
  selectedFilingDetail: FilingDetailDTO | null;
  selectedFilingContent: FilingContentDTO | null;
  selectedFilingFacts: XBRLFactDTO[];
  selectedFilingSources: FilingSourceReferenceDTO | null;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  searchHits: FilingSearchHitDTO[];
  comparison: FilingComparisonResponseDTO | null;
  comparisonLeftId: string | null;
  comparisonRightId: string | null;
  setComparisonLeftId: (id: string | null) => void;
  setComparisonRightId: (id: string | null) => void;
  isLoading: boolean;
  isDetailLoading: boolean;
  isSearching: boolean;
  isComparing: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  selectFiling: (filingId: string) => Promise<void>;
  performSearch: (query: string) => Promise<void>;
  runComparison: (leftId?: string, rightId?: string) => Promise<void>;
}

export function useCompanyFilings(companyId: string): UseCompanyFilingsReturn {
  const [activeSubTab, setActiveSubTab] = useState<FilingsSubTab>("overview");
  const [selectedFilingId, setSelectedFilingId] = useState<string | null>(null);

  const [overview, setOverview] = useState<FilingsOverviewSummaryDTO | null>(null);
  const [coverage, setCoverage] = useState<FilingCoverageDTO | null>(null);
  const [filings, setFilings] = useState<FilingSummaryDTO[]>([]);
  const [totalFilings, setTotalFilings] = useState<number>(0);

  const [selectedFilingDetail, setSelectedFilingDetail] = useState<FilingDetailDTO | null>(null);
  const [selectedFilingContent, setSelectedFilingContent] = useState<FilingContentDTO | null>(null);
  const [selectedFilingFacts, setSelectedFilingFacts] = useState<XBRLFactDTO[]>([]);
  const [selectedFilingSources, setSelectedFilingSources] = useState<FilingSourceReferenceDTO | null>(null);

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchHits, setSearchHits] = useState<FilingSearchHitDTO[]>([]);

  const [comparisonLeftId, setComparisonLeftId] = useState<string | null>(null);
  const [comparisonRightId, setComparisonRightId] = useState<string | null>(null);
  const [comparison, setComparison] = useState<FilingComparisonResponseDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadBaseData = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);

    try {
      const [overviewData, coverageData, catalogData] = await Promise.all([
        fetchFilingsOverview(companyId).catch(() => null),
        fetchFilingCoverage(companyId).catch(() => null),
        fetchFilingCatalog(companyId, { limit: 50 }).catch(() => ({
          company_id: companyId,
          total_count: 0,
          limit: 50,
          offset: 0,
          items: [],
        })),
      ]);

      setOverview(overviewData);
      setCoverage(coverageData);
      setFilings(catalogData.items);
      setTotalFilings(catalogData.total_count);

      // Default comparison IDs to the 10-K and 10-K/A if available
      const kOrig = catalogData.items.find((f) => f.form_type === "10-K" && !f.is_amendment);
      const kAmend = catalogData.items.find((f) => f.form_type === "10-K/A" || f.is_amendment);
      if (kOrig && kAmend) {
        setComparisonLeftId(kOrig.filing_id);
        setComparisonRightId(kAmend.filing_id);
      } else if (catalogData.items.length >= 2) {
        setComparisonLeftId(catalogData.items[0].filing_id);
        setComparisonRightId(catalogData.items[1].filing_id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load company filings");
    } finally {
      setIsLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    loadBaseData();
  }, [loadBaseData]);

  // Load detailed filing data when selectedFilingId changes
  const selectFiling = useCallback(
    async (filingId: string) => {
      setSelectedFilingId(filingId);
      setIsDetailLoading(true);
      setError(null);

      try {
        const [detailData, contentData, factsData, sourcesData] = await Promise.all([
          fetchFilingDetail(companyId, filingId),
          fetchFilingContent(companyId, filingId).catch(() => null),
          fetchFilingFacts(companyId, filingId).catch(() => ({
            filing_id: filingId,
            accession_number: "",
            total_count: 0,
            items: [],
          })),
          fetchFilingSources(companyId, filingId).catch(() => null),
        ]);

        setSelectedFilingDetail(detailData);
        setSelectedFilingContent(contentData);
        setSelectedFilingFacts(factsData.items);
        setSelectedFilingSources(sourcesData);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load filing details");
      } finally {
        setIsDetailLoading(false);
      }
    },
    [companyId]
  );

  const performSearch = useCallback(
    async (query: string) => {
      if (!companyId || !query.trim()) {
        setSearchHits([]);
        return;
      }
      setIsSearching(true);
      setError(null);

      try {
        const res = await searchFilings(companyId, query.trim());
        setSearchHits(res.hits);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Search failed");
      } finally {
        setIsSearching(false);
      }
    },
    [companyId]
  );

  const runComparison = useCallback(
    async (leftIdOverride?: string, rightIdOverride?: string) => {
      const left = leftIdOverride || comparisonLeftId;
      const right = rightIdOverride || comparisonRightId;
      if (!companyId || !left || !right) return;

      setIsComparing(true);
      setError(null);

      try {
        const result = await compareFilings(companyId, left, right);
        setComparison(result);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Filing comparison failed");
      } finally {
        setIsComparing(false);
      }
    },
    [companyId, comparisonLeftId, comparisonRightId]
  );

  return {
    activeSubTab,
    setActiveSubTab,
    selectedFilingId,
    setSelectedFilingId,
    overview,
    coverage,
    filings,
    totalFilings,
    selectedFilingDetail,
    selectedFilingContent,
    selectedFilingFacts,
    selectedFilingSources,
    searchQuery,
    setSearchQuery,
    searchHits,
    comparison,
    comparisonLeftId,
    comparisonRightId,
    setComparisonLeftId,
    setComparisonRightId,
    isLoading,
    isDetailLoading,
    isSearching,
    isComparing,
    error,
    refresh: loadBaseData,
    selectFiling,
    performSearch,
    runComparison,
  };
}
