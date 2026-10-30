/**
 * ATLAS Portfolios V1 — React Hook for Portfolio Allocation & Exposure Analytics (Stage 112).
 */

import { useCallback, useEffect, useState } from 'react';
import { portfolioExposureApi } from '@/lib/portfolios/exposure/api';
import {
  AllocationChangeResponse,
  ExposureBasis,
  ExposureDimension,
  GeographyPolicy,
  PortfolioExposureRunResponse,
} from '@/lib/portfolios/exposure/types';

export function usePortfolioExposures(portfolioId: string | null | undefined) {
  const [run, setRun] = useState<PortfolioExposureRunResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [exposureBasis, setExposureBasis] = useState<ExposureBasis>('NET_ASSET_VALUE');
  const [geographyPolicy, setGeographyPolicy] = useState<GeographyPolicy>('ISSUER_DOMICILE');
  const [enableLookThrough, setEnableLookThrough] = useState<boolean>(true);
  const [selectedDimension, setSelectedDimension] = useState<ExposureDimension>('ASSET_CLASS');

  const [historicalChanges, setHistoricalChanges] = useState<AllocationChangeResponse[]>([]);
  const [historicalLoading, setHistoricalLoading] = useState<boolean>(false);

  const fetchExposures = useCallback(
    async (force = false) => {
      if (!portfolioId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await portfolioExposureApi.getLatestExposure(portfolioId, {
          exposure_basis: exposureBasis,
          geography_policy: geographyPolicy,
          enable_look_through: enableLookThrough,
          force_recalculate: force,
        });
        setRun(data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to load portfolio exposures.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [portfolioId, exposureBasis, geographyPolicy, enableLookThrough]
  );

  const recalculate = useCallback(async () => {
    if (!portfolioId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await portfolioExposureApi.calculateExposure(portfolioId, {
        exposure_basis: exposureBasis,
        geography_policy: geographyPolicy,
        enable_look_through: enableLookThrough,
        force_recalculate: true,
      });
      setRun(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Recalculation failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [portfolioId, exposureBasis, geographyPolicy, enableLookThrough]);

  const fetchHistoricalChanges = useCallback(
    async (start: string, end: string, dim: ExposureDimension = selectedDimension) => {
      if (!portfolioId) return;
      setHistoricalLoading(true);
      try {
        const changes = await portfolioExposureApi.getAllocationChanges(portfolioId, start, end, dim);
        setHistoricalChanges(changes);
      } catch (err: unknown) {
        console.error('Failed to load historical allocation changes', err);
      } finally {
        setHistoricalLoading(false);
      }
    },
    [portfolioId, selectedDimension]
  );

  useEffect(() => {
    fetchExposures(false);
  }, [fetchExposures]);

  return {
    run,
    loading,
    error,
    exposureBasis,
    setExposureBasis,
    geographyPolicy,
    setGeographyPolicy,
    enableLookThrough,
    setEnableLookThrough,
    selectedDimension,
    setSelectedDimension,
    historicalChanges,
    historicalLoading,
    fetchHistoricalChanges,
    refetch: () => fetchExposures(true),
    recalculate,
  };
}

