'use client';

import { useState } from 'react';
import { InfrastructureSector, InfrastructureStatus } from '@/lib/maps/infrastructure/types';

export interface InfrastructureFiltersState {
  selectedSectors: Set<InfrastructureSector>;
  selectedStatus: InfrastructureStatus | 'all';
  countryFilter: string;
  searchQuery: string;
  minCapacity: number | null;
  maxCapacity: number | null;
  historicalAsOf: string;
  onlyVerifiedTopology: boolean;
}

export function useInfrastructureFilters() {
  const [filters, setFilters] = useState<InfrastructureFiltersState>({
    selectedSectors: new Set<InfrastructureSector>(),
    selectedStatus: 'all',
    countryFilter: '',
    searchQuery: '',
    minCapacity: null,
    maxCapacity: null,
    historicalAsOf: '',
    onlyVerifiedTopology: true,
  });

  const toggleSector = (sector: InfrastructureSector) => {
    setFilters((prev) => {
      const nextSectors = new Set(prev.selectedSectors);
      if (nextSectors.has(sector)) {
        nextSectors.delete(sector);
      } else {
        nextSectors.add(sector);
      }
      return { ...prev, selectedSectors: nextSectors };
    });
  };

  const selectAllSectors = () => {
    setFilters((prev) => ({
      ...prev,
      selectedSectors: new Set<InfrastructureSector>([
        'ports_maritime',
        'airports_aviation',
        'power_generation',
        'electricity_networks',
        'oil_gas',
        'mining',
        'data_centers',
        'railways',
        'logistics_industrial',
      ]),
    }));
  };

  const clearSectors = () => {
    setFilters((prev) => ({ ...prev, selectedSectors: new Set() }));
  };

  const setStatus = (status: InfrastructureStatus | 'all') => {
    setFilters((prev) => ({ ...prev, selectedStatus: status }));
  };

  const setCountry = (country: string) => {
    setFilters((prev) => ({ ...prev, countryFilter: country }));
  };

  const setSearch = (query: string) => {
    setFilters((prev) => ({ ...prev, searchQuery: query }));
  };

  const setCapacityRange = (min: number | null, max: number | null) => {
    setFilters((prev) => ({ ...prev, minCapacity: min, maxCapacity: max }));
  };

  const setHistoricalAsOf = (dateStr: string) => {
    setFilters((prev) => ({ ...prev, historicalAsOf: dateStr }));
  };

  const setOnlyVerifiedTopology = (val: boolean) => {
    setFilters((prev) => ({ ...prev, onlyVerifiedTopology: val }));
  };

  const resetFilters = () => {
    setFilters({
      selectedSectors: new Set(),
      selectedStatus: 'all',
      countryFilter: '',
      searchQuery: '',
      minCapacity: null,
      maxCapacity: null,
      historicalAsOf: '',
      onlyVerifiedTopology: true,
    });
  };

  return {
    filters,
    toggleSector,
    selectAllSectors,
    clearSectors,
    setStatus,
    setCountry,
    setSearch,
    setCapacityRange,
    setHistoricalAsOf,
    setOnlyVerifiedTopology,
    resetFilters,
  };
}

