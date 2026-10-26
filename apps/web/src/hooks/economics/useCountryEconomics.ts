"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CountryCategoryTab,
  CountryCoverageResponseDTO,
  CountryDemographicsSummaryDTO,
  CountryEconomicProfileDTO,
  CountryEconomicsOverviewDTO,
  CountryExternalSummaryDTO,
  CountryFiscalSummaryDTO,
  CountryGDPDecompositionDTO,
  CountryIndustrySummaryDTO,
  CountryInflationSummaryDTO,
  CountryLaborSummaryDTO,
  CountryMonetarySummaryDTO,
  CountryProductionDecompositionDTO,
  getCountries,
  getCountryCoverage,
  getCountryDemographics,
  getCountryExternal,
  getCountryFiscal,
  getCountryGDP,
  getCountryIndustry,
  getCountryInflation,
  getCountryLabor,
  getCountryMonetary,
  getCountryOverview,
  getCountryProduction,
  getCountryProfile,
} from "@/lib/economics/countries";

export interface UseCountryEconomicsReturn {
  countries: CountryEconomicProfileDTO[];
  selectedCountryId: string;
  setSelectedCountryId: (countryId: string) => void;
  activeCategory: CountryCategoryTab;
  setActiveCategory: (tab: CountryCategoryTab) => void;

  overview: CountryEconomicsOverviewDTO | null;
  profile: CountryEconomicProfileDTO | null;
  gdp: CountryGDPDecompositionDTO | null;
  production: CountryProductionDecompositionDTO | null;
  inflation: CountryInflationSummaryDTO | null;
  labor: CountryLaborSummaryDTO | null;
  industry: CountryIndustrySummaryDTO | null;
  monetary: CountryMonetarySummaryDTO | null;
  fiscal: CountryFiscalSummaryDTO | null;
  external: CountryExternalSummaryDTO | null;
  demographics: CountryDemographicsSummaryDTO | null;
  coverage: CountryCoverageResponseDTO | null;

  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useCountryEconomics(
  initialCountryId: string = "US"
): UseCountryEconomicsReturn {
  const [countries, setCountries] = useState<CountryEconomicProfileDTO[]>([]);
  const [selectedCountryId, setSelectedCountryId] = useState<string>(initialCountryId);
  const [activeCategory, setActiveCategory] = useState<CountryCategoryTab>("overview");

  const [overview, setOverview] = useState<CountryEconomicsOverviewDTO | null>(null);
  const [profile, setProfile] = useState<CountryEconomicProfileDTO | null>(null);
  const [gdp, setGdp] = useState<CountryGDPDecompositionDTO | null>(null);
  const [production, setProduction] = useState<CountryProductionDecompositionDTO | null>(null);
  const [inflation, setInflation] = useState<CountryInflationSummaryDTO | null>(null);
  const [labor, setLabor] = useState<CountryLaborSummaryDTO | null>(null);
  const [industry, setIndustry] = useState<CountryIndustrySummaryDTO | null>(null);
  const [monetary, setMonetary] = useState<CountryMonetarySummaryDTO | null>(null);
  const [fiscal, setFiscal] = useState<CountryFiscalSummaryDTO | null>(null);
  const [external, setExternal] = useState<CountryExternalSummaryDTO | null>(null);
  const [demographics, setDemographics] = useState<CountryDemographicsSummaryDTO | null>(null);
  const [coverage, setCoverage] = useState<CountryCoverageResponseDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial load of supported country profiles
  useEffect(() => {
    let mounted = true;
    getCountries()
      .then((data) => {
        if (mounted) {
          setCountries(data);
        }
      })
      .catch((err) => {
        if (mounted) {
          console.error("Failed to load country list:", err);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  // 2. Load country master data and active category
  const loadCountryData = useCallback(async () => {
    if (!selectedCountryId) return;

    setIsLoading(true);
    setError(null);

    try {
      // Parallel fetch for core profile, overview and coverage
      const [ovRes, profRes, covRes] = await Promise.all([
        getCountryOverview(selectedCountryId).catch(() => null),
        getCountryProfile(selectedCountryId).catch(() => null),
        getCountryCoverage(selectedCountryId).catch(() => null),
      ]);

      setOverview(ovRes);
      setProfile(profRes);
      setCoverage(covRes);

      // Category specific loader
      if (activeCategory === "gdp" || activeCategory === "overview") {
        const [gdpRes, prodRes] = await Promise.all([
          getCountryGDP(selectedCountryId).catch(() => null),
          getCountryProduction(selectedCountryId).catch(() => null),
        ]);
        setGdp(gdpRes);
        setProduction(prodRes);
      }
      if (activeCategory === "inflation" || activeCategory === "overview") {
        const infRes = await getCountryInflation(selectedCountryId).catch(() => null);
        setInflation(infRes);
      }
      if (activeCategory === "labor" || activeCategory === "overview") {
        const labRes = await getCountryLabor(selectedCountryId).catch(() => null);
        setLabor(labRes);
      }
      if (activeCategory === "industry") {
        const indRes = await getCountryIndustry(selectedCountryId).catch(() => null);
        setIndustry(indRes);
      }
      if (activeCategory === "monetary") {
        const monRes = await getCountryMonetary(selectedCountryId).catch(() => null);
        setMonetary(monRes);
      }
      if (activeCategory === "fiscal" || activeCategory === "overview") {
        const fiscRes = await getCountryFiscal(selectedCountryId).catch(() => null);
        setFiscal(fiscRes);
      }
      if (activeCategory === "external" || activeCategory === "overview") {
        const extRes = await getCountryExternal(selectedCountryId).catch(() => null);
        setExternal(extRes);
      }
      if (activeCategory === "demographics" || activeCategory === "overview") {
        const demoRes = await getCountryDemographics(selectedCountryId).catch(() => null);
        setDemographics(demoRes);
      }
    } catch (err) {
      console.error("Error loading country economics:", err);
      setError(err instanceof Error ? err.message : "Failed to load sovereign economic dataset.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedCountryId, activeCategory]);

  useEffect(() => {
    loadCountryData();
  }, [loadCountryData]);

  return {
    countries,
    selectedCountryId,
    setSelectedCountryId,
    activeCategory,
    setActiveCategory,
    overview,
    profile,
    gdp,
    production,
    inflation,
    labor,
    industry,
    monetary,
    fiscal,
    external,
    demographics,
    coverage,
    isLoading,
    error,
    refresh: loadCountryData,
  };
}
