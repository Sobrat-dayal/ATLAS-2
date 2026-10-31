'use client';

import { useCallback, useEffect, useState } from 'react';
import { fetchInfrastructureAssets, fetchInfrastructureAsset } from '@/lib/maps/infrastructure/api';
import { InfrastructureAsset } from '@/lib/maps/infrastructure/types';

export function useInfrastructureAssets(initialFilters?: {
  sector?: string;
  country?: string;
  company_id?: string;
  status?: string;
}) {
  const [assets, setAssets] = useState<InfrastructureAsset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<InfrastructureAsset | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadAssets = useCallback(
    async (params?: {
      sector?: string;
      country?: string;
      company_id?: string;
      status?: string;
      min_capacity?: number;
      max_capacity?: number;
      capacity_metric?: string;
      historical_as_of?: string;
    }) => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetchInfrastructureAssets(params || initialFilters);
        setAssets(res.assets || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load assets');
      } finally {
        setIsLoading(false);
      }
    },
    [initialFilters]
  );

  const selectAsset = useCallback(async (assetId: string | null) => {
    if (!assetId) {
      setSelectedAsset(null);
      return;
    }
    try {
      const asset = await fetchInfrastructureAsset(assetId);
      setSelectedAsset(asset);
    } catch (err: any) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    loadAssets();
  }, [loadAssets]);

  return {
    assets,
    selectedAsset,
    isLoading,
    error,
    refreshAssets: loadAssets,
    selectAsset,
    setSelectedAsset,
  };
}

