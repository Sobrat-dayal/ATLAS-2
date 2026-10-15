"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  CryptoAssetDirectoryResponse,
  getCryptoAssets,
} from "@/lib/markets/crypto";

export interface UseCryptoAssetsOptions {
  initialQuery?: string;
  initialAssetKind?: string;
  initialNetwork?: string;
  limit?: number;
}

export function useCryptoAssets(options?: UseCryptoAssetsOptions) {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [assetKind, setAssetKind] = useState<string>(
    options?.initialAssetKind || "all"
  );
  const [network, setNetwork] = useState<string>(
    options?.initialNetwork || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<CryptoAssetDirectoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const limit = options?.limit || 25;

  const fetchAssets = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const res = await getCryptoAssets({
        token,
        query,
        asset_kind: assetKind,
        network,
        limit,
        cursor: cursor || undefined,
      });
      setData(res);
    } catch (err) {
      setIsError(true);
      setError(
        err instanceof Error
          ? err
          : new Error("Failed to load digital assets")
      );
    } finally {
      setIsLoading(false);
    }
  }, [token, query, assetKind, network, limit, cursor]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchAssets();
  }, [fetchAssets]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchAssets,
    query,
    setQuery,
    assetKind,
    setAssetKind,
    network,
    setNetwork,
    cursor,
    setCursor,
  };
}
