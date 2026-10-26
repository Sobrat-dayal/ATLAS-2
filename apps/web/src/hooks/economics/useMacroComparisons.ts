"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ComparableIndicatorDTO,
  ComparisonMatrixRequestDTO,
  ComparisonMatrixResponseDTO,
  CorrelationAnalysisResponseDTO,
  CorrelationMethod,
  DistributionSummaryDTO,
  DivergenceAnalysisResponseDTO,
  EconomicRankingsResponseDTO,
  GeographicCohortDTO,
  HistoricalTrendsResponseDTO,
  MacroCoverageSummaryDTO,
  MatrixCellDTO,
  PeriodAlignmentPolicy,
  RankingDirection,
  TieBreakerPolicy,
  WeightingPolicy,
  getComparableIndicators,
  getComparisonGeographies,
  getComparisonMatrix,
  getCorrelationAnalysis,
  getDistributionStatistics,
  getDivergenceAnalysis,
  getEconomicRankings,
  getGeographicCohorts,
  getHistoricalTrends,
  getMacroCoverageSummary,
  ComparisonMetricKind,
} from "@/lib/economics/comparisons";

export type MacroComparisonView =
  | "matrix"
  | "rankings"
  | "distributions"
  | "trends"
  | "divergence"
  | "correlations"
  | "coverage";

export interface GeographyOption {
  geography_id: string;
  name: string;
  iso_code: string;
  is_economic_area: boolean;
}

export function useMacroComparisons() {
  const [activeView, setActiveView] = useState<MacroComparisonView>("matrix");

  // Selection states
  const [selectedGeographyIds, setSelectedGeographyIds] = useState<string[]>([
    "geo-us",
    "geo-ea",
    "geo-cn",
    "geo-jp",
    "geo-gb",
    "geo-in",
  ]);
  const [selectedCohortId, setSelectedCohortId] = useState<string | null>(null);
  const [selectedMetricKind, setSelectedMetricKind] = useState<ComparisonMetricKind>("gdp_real_growth_yoy");
  const [periodPolicy, setPeriodPolicy] = useState<PeriodAlignmentPolicy>("latest_per_country");
  const [rankingDirection, setRankingDirection] = useState<RankingDirection>("descending");
  const [tiePolicy, setTiePolicy] = useState<TieBreakerPolicy>("standard_competition");
  const [weightingPolicy, setWeightingPolicy] = useState<WeightingPolicy>("equal_weight");
  const [basePeriod, setBasePeriod] = useState<string | null>(null);

  // Divergence pair
  const [divergenceCountryA, setDivergenceCountryA] = useState<string>("geo-us");
  const [divergenceCountryB, setDivergenceCountryB] = useState<string>("geo-ea");

  // Correlation settings
  const [correlationMethod, setCorrelationMethod] = useState<CorrelationMethod>("pearson");

  // Inspected items
  const [inspectedCell, setInspectedCell] = useState<MatrixCellDTO | null>(null);

  // Data states
  const [indicators, setIndicators] = useState<ComparableIndicatorDTO[]>([]);
  const [geographies, setGeographies] = useState<GeographyOption[]>([]);
  const [cohorts, setCohorts] = useState<GeographicCohortDTO[]>([]);
  const [matrixData, setMatrixData] = useState<ComparisonMatrixResponseDTO | null>(null);
  const [rankingsData, setRankingsData] = useState<EconomicRankingsResponseDTO | null>(null);
  const [distributionData, setDistributionData] = useState<DistributionSummaryDTO | null>(null);
  const [trendsData, setTrendsData] = useState<HistoricalTrendsResponseDTO | null>(null);
  const [divergenceData, setDivergenceData] = useState<DivergenceAnalysisResponseDTO | null>(null);
  const [correlationData, setCorrelationData] = useState<CorrelationAnalysisResponseDTO | null>(null);
  const [coverageData, setCoverageData] = useState<MacroCoverageSummaryDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initial metadata fetch
  useEffect(() => {
    let isMounted = true;
    async function loadMetadata() {
      try {
        const [indList, geoList, cohortList, cov] = await Promise.all([
          getComparableIndicators(),
          getComparisonGeographies(),
          getGeographicCohorts(),
          getMacroCoverageSummary(),
        ]);
        if (isMounted) {
          setIndicators(indList);
          setGeographies(geoList);
          setCohorts(cohortList);
          setCoverageData(cov);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load comparison metadata");
        }
      }
    }
    loadMetadata();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch Matrix
  const fetchMatrix = useCallback(async () => {
    if (selectedGeographyIds.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      const req: ComparisonMatrixRequestDTO = {
        geography_ids: selectedGeographyIds,
        period_policy: periodPolicy,
      };
      const res = await getComparisonMatrix(req);
      setMatrixData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load matrix data");
    } finally {
      setIsLoading(false);
    }
  }, [selectedGeographyIds, periodPolicy]);

  // Fetch Rankings
  const fetchRankings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getEconomicRankings({
        metric_kind: selectedMetricKind,
        geography_ids: selectedGeographyIds,
        cohort_id: selectedCohortId,
        direction: rankingDirection,
        tie_policy: tiePolicy,
      });
      setRankingsData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load rankings data");
    } finally {
      setIsLoading(false);
    }
  }, [selectedMetricKind, selectedGeographyIds, selectedCohortId, rankingDirection, tiePolicy]);

  // Fetch Distributions
  const fetchDistributions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getDistributionStatistics({
        metric_kind: selectedMetricKind,
        geography_ids: selectedGeographyIds,
        cohort_id: selectedCohortId,
        weighting_policy: weightingPolicy,
      });
      setDistributionData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load distribution statistics");
    } finally {
      setIsLoading(false);
    }
  }, [selectedMetricKind, selectedGeographyIds, selectedCohortId, weightingPolicy]);

  // Fetch Historical Trends
  const fetchTrends = useCallback(async () => {
    if (selectedGeographyIds.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await getHistoricalTrends({
        metric_kind: selectedMetricKind,
        geography_ids: selectedGeographyIds,
        base_period: basePeriod,
      });
      setTrendsData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load historical trend data");
    } finally {
      setIsLoading(false);
    }
  }, [selectedMetricKind, selectedGeographyIds, basePeriod]);

  // Fetch Divergence
  const fetchDivergence = useCallback(async () => {
    if (!divergenceCountryA || !divergenceCountryB) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await getDivergenceAnalysis({
        metric_kind: selectedMetricKind,
        geography_a_id: divergenceCountryA,
        geography_b_id: divergenceCountryB,
      });
      setDivergenceData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load divergence analysis");
    } finally {
      setIsLoading(false);
    }
  }, [selectedMetricKind, divergenceCountryA, divergenceCountryB]);

  // Fetch Correlations
  const fetchCorrelations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Build pairwise series across selected countries for headline indicators
      const pairs: Array<{ geo_a: string; metric_a: string; geo_b: string; metric_b: string }> = [];
      const geos = selectedGeographyIds.slice(0, 4);
      for (let i = 0; i < geos.length; i++) {
        for (let j = i + 1; j < geos.length; j++) {
          pairs.push({
            geo_a: geos[i],
            metric_a: selectedMetricKind,
            geo_b: geos[j],
            metric_b: selectedMetricKind,
          });
        }
      }
      if (pairs.length === 0) {
        setIsLoading(false);
        return;
      }
      const res = await getCorrelationAnalysis({
        series_pairs: pairs,
        method: correlationMethod,
      });
      setCorrelationData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to calculate correlation analysis");
    } finally {
      setIsLoading(false);
    }
  }, [selectedGeographyIds, selectedMetricKind, correlationMethod]);

  // View-dependent refresh trigger
  useEffect(() => {
    if (activeView === "matrix") {
      fetchMatrix();
    } else if (activeView === "rankings") {
      fetchRankings();
    } else if (activeView === "distributions") {
      fetchDistributions();
    } else if (activeView === "trends") {
      fetchTrends();
    } else if (activeView === "divergence") {
      fetchDivergence();
    } else if (activeView === "correlations") {
      fetchCorrelations();
    }
  }, [
    activeView,
    fetchMatrix,
    fetchRankings,
    fetchDistributions,
    fetchTrends,
    fetchDivergence,
    fetchCorrelations,
  ]);

  // Cohort selection helper
  const handleSelectCohort = (cohortId: string | null) => {
    setSelectedCohortId(cohortId);
    if (!cohortId) {
      setSelectedGeographyIds(["geo-us", "geo-ea", "geo-cn", "geo-jp", "geo-gb", "geo-in"]);
      return;
    }
    const found = cohorts.find((c) => c.cohort_id === cohortId);
    if (found) {
      setSelectedGeographyIds(found.member_geography_ids);
    }
  };

  // Toggle individual country
  const handleToggleCountry = (geoId: string) => {
    setSelectedCohortId(null);
    if (selectedGeographyIds.includes(geoId)) {
      if (selectedGeographyIds.length > 2) {
        setSelectedGeographyIds(selectedGeographyIds.filter((id) => id !== geoId));
      }
    } else {
      setSelectedGeographyIds([...selectedGeographyIds, geoId]);
    }
  };

  const handleSelectAllCountries = () => {
    setSelectedCohortId(null);
    setSelectedGeographyIds(geographies.map((g) => g.geography_id));
  };

  const refreshCurrentView = () => {
    if (activeView === "matrix") fetchMatrix();
    else if (activeView === "rankings") fetchRankings();
    else if (activeView === "distributions") fetchDistributions();
    else if (activeView === "trends") fetchTrends();
    else if (activeView === "divergence") fetchDivergence();
    else if (activeView === "correlations") fetchCorrelations();
  };

  return {
    activeView,
    setActiveView,
    selectedGeographyIds,
    setSelectedGeographyIds,
    selectedCohortId,
    handleSelectCohort,
    handleToggleCountry,
    handleSelectAllCountries,
    selectedMetricKind,
    setSelectedMetricKind,
    periodPolicy,
    setPeriodPolicy,
    rankingDirection,
    setRankingDirection,
    tiePolicy,
    setTiePolicy,
    weightingPolicy,
    setWeightingPolicy,
    basePeriod,
    setBasePeriod,
    divergenceCountryA,
    setDivergenceCountryA,
    divergenceCountryB,
    setDivergenceCountryB,
    correlationMethod,
    setCorrelationMethod,
    inspectedCell,
    setInspectedCell,
    indicators,
    geographies,
    cohorts,
    matrixData,
    rankingsData,
    distributionData,
    trendsData,
    divergenceData,
    correlationData,
    coverageData,
    isLoading,
    error,
    refreshCurrentView,
  };
}
