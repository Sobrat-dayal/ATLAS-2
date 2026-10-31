'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  fetchNetworks,
  fetchNetwork,
  queryNetworkSubgraph,
  findNetworkConnection,
} from '@/lib/maps/infrastructure/api';
import { InfrastructureNetwork } from '@/lib/maps/infrastructure/types';

export function useInfrastructureNetworks(sector?: string) {
  const [networks, setNetworks] = useState<InfrastructureNetwork[]>([]);
  const [activeNetwork, setActiveNetwork] = useState<InfrastructureNetwork | null>(null);
  const [subgraph, setSubgraph] = useState<any | null>(null);
  const [pathResult, setPathResult] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadNetworks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchNetworks({ sector });
      setNetworks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load networks');
    } finally {
      setIsLoading(false);
    }
  }, [sector]);

  const selectNetwork = useCallback(async (networkId: string) => {
    setIsLoading(true);
    try {
      const net = await fetchNetwork(networkId);
      setActiveNetwork(net);
      setSubgraph(null);
      setPathResult(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch network topology');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const traverseSubgraph = useCallback(
    async (startNodeId: string, maxHops: number = 5, onlyVerified: boolean = true) => {
      if (!activeNetwork) return;
      setIsLoading(true);
      try {
        const res = await queryNetworkSubgraph(
          activeNetwork.network_id,
          startNodeId,
          maxHops,
          onlyVerified
        );
        setSubgraph(res);
      } catch (err: any) {
        setError(err.message || 'Traversal failed');
      } finally {
        setIsLoading(false);
      }
    },
    [activeNetwork]
  );

  const findPath = useCallback(
    async (startNodeId: string, targetNodeId: string) => {
      if (!activeNetwork) return;
      setIsLoading(true);
      try {
        const res = await findNetworkConnection(
          activeNetwork.network_id,
          startNodeId,
          targetNodeId,
          true
        );
        setPathResult(res);
      } catch (err: any) {
        setError(err.message || 'No verified path found');
        setPathResult(null);
      } finally {
        setIsLoading(false);
      }
    },
    [activeNetwork]
  );

  useEffect(() => {
    loadNetworks();
  }, [loadNetworks]);

  return {
    networks,
    activeNetwork,
    subgraph,
    pathResult,
    isLoading,
    error,
    selectNetwork,
    traverseSubgraph,
    findPath,
    refreshNetworks: loadNetworks,
  };
}

