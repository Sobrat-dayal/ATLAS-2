"use client";

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../auth';

export interface RoutingPolicy {
  policy_id: string;
  scope: 'system' | 'user';
  owner_principal_id?: string | null;
  domain: string;
  enabled: boolean;
  fallback_enabled: boolean;
  candidates: RoutingCandidate[];
}

export interface RoutingCandidate {
  provider_key: string;
  priority: number;
}

export function useRoutingSettings(domain: string) {
  const { session } = useAuth();
  const [policy, setPolicy] = useState<RoutingPolicy | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchPolicy = useCallback(async () => {
    if (!session?.access_token || !domain) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch(`/api/v1/providers/routing/${domain}`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch routing policy');
      const data = await res.json();
      setPolicy(data.policy);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [session?.access_token, domain]);

  useEffect(() => {
    fetchPolicy();
  }, [fetchPolicy]);

  const updatePolicy = useCallback(async (enabled: boolean, fallback_enabled: boolean, provider_keys: string[]) => {
    if (!session?.access_token || !domain) return;
    try {
      const res = await fetch(`/api/v1/providers/routing/${domain}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ enabled, fallback_enabled, provider_keys })
      });
      if (!res.ok) throw new Error('Failed to update routing policy');
      const data = await res.json();
      setPolicy(data.policy);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      throw err;
    }
  }, [session, domain]);

  const resetPolicy = useCallback(async () => {
    if (!session?.access_token || !domain) return;
    try {
      const res = await fetch(`/api/v1/providers/routing/${domain}/reset`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${session.access_token}`
        }
      });
      if (!res.ok) throw new Error('Failed to reset routing policy');
      await fetchPolicy();
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      throw err;
    }
  }, [session, domain, fetchPolicy]);

  return {
    policy,
    isLoading,
    error,
    updatePolicy,
    resetPolicy,
    refetch: fetchPolicy
  };
}
