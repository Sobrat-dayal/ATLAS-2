"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchCompanyFootprint } from "@/lib/maps/corporate/api";
import {
  CompanyFootprintResponse,
  CorporateFacility,
  CorporateFacilityStatus,
  CorporateFacilityType,
} from "@/lib/maps/corporate/types";

export interface UseCompanyFootprintOptions {
  initialCompanyId?: string | null;
  initialIncludeSubsidiaries?: boolean;
}

export function useCompanyFootprint(options?: UseCompanyFootprintOptions) {
  const [companyId, setCompanyId] = useState<string | null>(options?.initialCompanyId || null);
  const [includeSubsidiaries, setIncludeSubsidiaries] = useState<boolean>(
    options?.initialIncludeSubsidiaries ?? true
  );
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<CorporateFacilityType[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<CorporateFacilityStatus[]>([]);
  const [asOfDate, setAsOfDate] = useState<string | null>(null);

  const [footprint, setFootprint] = useState<CompanyFootprintResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadFootprint = useCallback(async () => {
    if (!companyId) {
      setFootprint(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await fetchCompanyFootprint(companyId, {
        includeSubsidiaries,
        country: selectedCountry || undefined,
        asOf: asOfDate || undefined,
      });
      setFootprint(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load company geographic footprint");
      setFootprint(null);
    } finally {
      setLoading(false);
    }
  }, [companyId, includeSubsidiaries, selectedCountry, asOfDate]);

  useEffect(() => {
    loadFootprint();
  }, [loadFootprint]);

  // Filter facilities client-side for dynamic multi-selection without reloading API
  const filteredFacilities = useMemo<CorporateFacility[]>(() => {
    if (!footprint) return [];
    return footprint.facilities.filter((fac) => {
      if (selectedTypes.length > 0 && !selectedTypes.includes(fac.facility_type)) {
        return false;
      }
      if (selectedStatuses.length > 0 && !selectedStatuses.includes(fac.facility_status)) {
        return false;
      }
      if (selectedCountry && fac.country_code.toUpperCase() !== selectedCountry.toUpperCase()) {
        return false;
      }
      return true;
    });
  }, [footprint, selectedTypes, selectedStatuses, selectedCountry]);

  return {
    companyId,
    setCompanyId,
    includeSubsidiaries,
    setIncludeSubsidiaries,
    selectedCountry,
    setSelectedCountry,
    selectedTypes,
    setSelectedTypes,
    selectedStatuses,
    setSelectedStatuses,
    asOfDate,
    setAsOfDate,
    footprint,
    facilities: filteredFacilities,
    rawFacilities: footprint?.facilities || [],
    summary: footprint?.summary || null,
    loading,
    error,
    refresh: loadFootprint,
  };
}

