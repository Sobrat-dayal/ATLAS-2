"use client";

import { useCallback, useEffect, useState } from "react";
import {
  DateRangePreset,
  EconomicCoverageResponseDTO,
  EconomicGeographyDTO,
  EconomicIndicatorDTO,
  EconomicSeriesDTO,
  EconomicSeriesObservationsResponseDTO,
  EconomicVintageDTO,
  getEconomicCoverage,
  getEconomicGeographies,
  getEconomicIndicators,
  getEconomicObservations,
  getEconomicSeries,
  getEconomicVintages,
  getGlobalMacroOverview,
  getIndicatorCategories,
  getTransformations,
  GlobalMacroOverviewResponseDTO,
  IndicatorCategory,
  TransformationDefinitionDTO,
  TransformationType,
} from "@/lib/economics";

export type EconomicsSubTab = "overview" | "country" | "explorer" | "series";
export type { DateRangePreset };

export interface UseEconomicsReturn {
  activeTab: EconomicsSubTab;
  setActiveTab: (tab: EconomicsSubTab) => void;

  // Selected Country in Country Economics Workspace
  selectedCountryEconomicsId: string;
  setSelectedCountryEconomicsId: (id: string) => void;
  navigateToCountry: (countryId: string) => void;

  // Global Overview Data
  overview: GlobalMacroOverviewResponseDTO | null;
  geographies: EconomicGeographyDTO[];
  categories: IndicatorCategory[];
  coverage: EconomicCoverageResponseDTO | null;
  transformationsList: TransformationDefinitionDTO[];

  // Explorer Data
  indicators: EconomicIndicatorDTO[];
  seriesList: EconomicSeriesDTO[];

  // Filter States
  selectedGeographyId: string | null;
  setSelectedGeographyId: (geoId: string | null) => void;
  selectedCategoryId: IndicatorCategory | null;
  setSelectedCategoryId: (cat: IndicatorCategory | null) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;

  // Selected Series & Chart View
  selectedSeriesId: string | null;
  selectedSeriesData: EconomicSeriesObservationsResponseDTO | null;
  selectedVintages: EconomicVintageDTO[];
  activeTransformation: TransformationType;
  setActiveTransformation: (t: TransformationType) => void;
  activeDateRange: DateRangePreset;
  setActiveDateRange: (range: DateRangePreset) => void;

  // Loading & Error States
  isLoading: boolean;
  isSeriesLoading: boolean;
  error: string | null;

  // Action methods
  selectSeries: (seriesId: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useEconomics(): UseEconomicsReturn {
  const [activeTab, setActiveTab] = useState<EconomicsSubTab>("overview");

  // Overview & Catalogs
  const [overview, setOverview] = useState<GlobalMacroOverviewResponseDTO | null>(null);
  const [geographies, setGeographies] = useState<EconomicGeographyDTO[]>([]);
  const [categories, setCategories] = useState<IndicatorCategory[]>([]);
  const [coverage, setCoverage] = useState<EconomicCoverageResponseDTO | null>(null);
  const [transformationsList, setTransformationsList] = useState<TransformationDefinitionDTO[]>([]);

  // Explorer
  const [indicators, setIndicators] = useState<EconomicIndicatorDTO[]>([]);
  const [seriesList, setSeriesList] = useState<EconomicSeriesDTO[]>([]);

  // Filter selection
  const [selectedGeographyId, setSelectedGeographyId] = useState<string | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<IndicatorCategory | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Series details
  const [selectedSeriesId, setSelectedSeriesId] = useState<string | null>("ser-us-gdp-growth");
  const [selectedSeriesData, setSelectedSeriesData] = useState<EconomicSeriesObservationsResponseDTO | null>(null);
  const [selectedVintages, setSelectedVintages] = useState<EconomicVintageDTO[]>([]);
  const [activeTransformation, setActiveTransformation] = useState<TransformationType>("SOURCE_REPORTED");
  const [activeDateRange, setActiveDateRange] = useState<DateRangePreset>("5Y");

  // Loading states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeriesLoading, setIsSeriesLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial catalog, overview, geographies, categories, transformations
  const loadInitialData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [
        overviewRes,
        geosRes,
        catsRes,
        indicatorsRes,
        seriesRes,
        coverageRes,
        transformsRes,
      ] = await Promise.all([
        getGlobalMacroOverview(),
        getEconomicGeographies(),
        getIndicatorCategories(),
        getEconomicIndicators(),
        getEconomicSeries(),
        getEconomicCoverage(),
        getTransformations(),
      ]);

      setOverview(overviewRes);
      setGeographies(geosRes);
      setCategories(catsRes);
      setIndicators(indicatorsRes);
      setSeriesList(seriesRes);
      setCoverage(coverageRes);
      setTransformationsList(transformsRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load macroeconomic overview.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch observations & vintages for selected series
  const loadSeriesDetails = useCallback(
    async (seriesId: string, transform: TransformationType = activeTransformation) => {
      setIsSeriesLoading(true);
      try {
        const [obsRes, vintagesRes] = await Promise.all([
          getEconomicObservations(seriesId, { transformation: transform }),
          getEconomicVintages(seriesId),
        ]);
        setSelectedSeriesData(obsRes);
        setSelectedVintages(vintagesRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load series observations.";
        console.error("Series load error:", msg);
      } finally {
        setIsSeriesLoading(false);
      }
    },
    [activeTransformation]
  );

  // Initial load
  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Load default or selected series when id changes
  useEffect(() => {
    if (selectedSeriesId) {
      loadSeriesDetails(selectedSeriesId, activeTransformation);
    }
  }, [selectedSeriesId, activeTransformation, loadSeriesDetails]);

  // Action to select a series and switch to series view tab
  const [selectedCountryEconomicsId, setSelectedCountryEconomicsId] = useState<string>("US");

  const navigateToCountry = useCallback((countryId: string) => {
    setSelectedCountryEconomicsId(countryId);
    setActiveTab("country");
  }, []);

  const selectSeries = useCallback(
    async (seriesId: string) => {
      setSelectedSeriesId(seriesId);
      setActiveTab("series");
      await loadSeriesDetails(seriesId, activeTransformation);
    },
    [activeTransformation, loadSeriesDetails]
  );

  return {
    activeTab,
    setActiveTab,
    selectedCountryEconomicsId,
    setSelectedCountryEconomicsId,
    navigateToCountry,
    overview,
    geographies,
    categories,
    coverage,
    transformationsList,
    indicators,
    seriesList,
    selectedGeographyId,
    setSelectedGeographyId,
    selectedCategoryId,
    setSelectedCategoryId,
    searchQuery,
    setSearchQuery,
    selectedSeriesId,
    selectedSeriesData,
    selectedVintages,
    activeTransformation,
    setActiveTransformation,
    activeDateRange,
    setActiveDateRange,
    isLoading,
    isSeriesLoading,
    error,
    selectSeries,
    refresh: loadInitialData,
  };
}
