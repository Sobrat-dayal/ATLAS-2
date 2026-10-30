"use client";

import { useEffect, useState } from "react";
import { approveAiToolCall, denyAiToolCall, fetchAiToolApproval } from "@/lib/ai/tools/api";
import { AiToolApprovalRequest } from "@/lib/ai/tools/types";

export function useAiToolApproval(approvalId?: string | null) {
  const [approval, setApproval] = useState<AiToolApprovalRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    if (!approvalId) {
      setApproval(null);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAiToolApproval(approvalId);
      setApproval(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [approvalId]);

  const approve = async (reason?: string) => {
    if (!approvalId) return;
    try {
      setActionLoading(true);
      const updated = await approveAiToolCall(approvalId, reason);
      setApproval(updated);
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      throw err;
    } finally {
      setActionLoading(false);
    }
  };

  const deny = async (reason?: string) => {
    if (!approvalId) return;
    try {
      setActionLoading(true);
      const updated = await denyAiToolCall(approvalId, reason);
      setApproval(updated);
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      throw err;
    } finally {
      setActionLoading(false);
    }
  };

  return { approval, loading, actionLoading, error, approve, deny, refetch: load };
}

