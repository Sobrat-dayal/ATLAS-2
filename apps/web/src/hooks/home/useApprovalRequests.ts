"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  decideApproval as apiDecideApproval,
  getApprovalCounts as apiGetApprovalCounts,
  getApprovalDetail as apiGetApprovalDetail,
  listApprovals as apiListApprovals,
} from "@/lib/approvals/api";
import {
  ApprovalCountsResponse,
  ApprovalDecisionInput,
  ApprovalDecisionResponse,
  ApprovalDetail,
  ApprovalItem,
  ApprovalStatusFilter,
} from "@/lib/approvals/types";

export interface UseApprovalRequestsResult {
  approvals: ApprovalItem[];
  counts: ApprovalCountsResponse | null;
  isLoading: boolean;
  isLoadingMore: boolean;
  isError: boolean;
  error: Error | null;
  hasMore: boolean;
  isDeciding: boolean;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  getDetail: (approvalId: string) => Promise<ApprovalDetail>;
  decideApproval: (
    approvalId: string,
    input: ApprovalDecisionInput
  ) => Promise<ApprovalDecisionResponse>;
}

export function useApprovalRequests(
  statusFilter: ApprovalStatusFilter = "PENDING",
  limit: number = 10
): UseApprovalRequestsResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [counts, setCounts] = useState<ApprovalCountsResponse | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isDeciding, setIsDeciding] = useState<boolean>(false);

  const isMountedRef = useRef<boolean>(true);
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const fetchInitialData = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const [listRes, countsRes] = await Promise.all([
        apiListApprovals({ status: statusFilter, limit }, { token }),
        apiGetApprovalCounts({ token }),
      ]);

      if (isMountedRef.current) {
        setApprovals(listRes.items);
        setNextCursor(listRes.next_cursor);
        setHasMore(listRes.has_more);
        setCounts(countsRes);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setIsError(true);
        setError(err instanceof Error ? err : new Error(String(err)));
        setIsLoading(false);
      }
    }
  }, [statusFilter, limit, token]);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const refetch = useCallback(async () => {
    await fetchInitialData();
  }, [fetchInitialData]);

  const loadMore = useCallback(async () => {
    if (!hasMore || !nextCursor || isLoadingMore) return;
    setIsLoadingMore(true);

    try {
      const res = await apiListApprovals(
        { status: statusFilter, limit, cursor: nextCursor },
        { token }
      );
      if (isMountedRef.current) {
        setApprovals((prev) => [...prev, ...res.items]);
        setNextCursor(res.next_cursor);
        setHasMore(res.has_more);
        setIsLoadingMore(false);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err instanceof Error ? err : new Error(String(err)));
        setIsLoadingMore(false);
      }
    }
  }, [hasMore, nextCursor, isLoadingMore, statusFilter, limit, token]);

  const getDetail = useCallback(
    async (approvalId: string): Promise<ApprovalDetail> => {
      return apiGetApprovalDetail(approvalId, { token });
    },
    [token]
  );

  const decideApproval = useCallback(
    async (
      approvalId: string,
      input: ApprovalDecisionInput
    ): Promise<ApprovalDecisionResponse> => {
      setIsDeciding(true);
      try {
        const response = await apiDecideApproval(approvalId, input, { token });
        if (isMountedRef.current) {
          // Remove from pending list or update state
          if (statusFilter === "PENDING") {
            setApprovals((prev) => prev.filter((a) => a.approval_id !== approvalId));
          } else {
            setApprovals((prev) =>
              prev.map((a) =>
                a.approval_id === approvalId
                  ? {
                      ...a,
                      status: response.status,
                      display_status: response.status,
                      decided_at: response.decided_at,
                      version: response.version,
                    }
                  : a
              )
            );
          }
          // Refresh authoritative counts
          apiGetApprovalCounts({ token }).then((c) => {
            if (isMountedRef.current) setCounts(c);
          });
        }
        return response;
      } finally {
        if (isMountedRef.current) {
          setIsDeciding(false);
        }
      }
    },
    [statusFilter, token]
  );

  return {
    approvals,
    counts,
    isLoading,
    isLoadingMore,
    isError,
    error,
    hasMore,
    isDeciding,
    refetch,
    loadMore,
    getDetail,
    decideApproval,
  };
}
