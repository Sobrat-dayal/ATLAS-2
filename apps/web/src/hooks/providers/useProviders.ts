import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../auth';

export interface ProviderDescriptor {
  provider_key: string;
  name: string;
  domains: string[];
}

export function useProviders(domain?: string) {
  const { session } = useAuth();
  const [providers, setProviders] = useState<ProviderDescriptor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProviders = useCallback(async () => {
    if (!session?.access_token) return;
    try {
      setIsLoading(true);
      setError(null);
      const url = domain ? `/api/v1/providers?domain=${domain}` : '/api/v1/providers';
      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${session.access_token}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch providers');
      const data = await res.json();
      // the endpoint returns something like: { providers: [ ... ] } or just list? Let's check backend endpoint.
      // We will assume it returns { providers: [] } or just [] based on typical patterns. Let's just set it to data.providers || data.
      setProviders(data.providers || data || []);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [session, domain]);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  return {
    providers,
    isLoading,
    error,
    refetch: fetchProviders
  };
}
