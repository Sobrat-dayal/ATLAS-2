"use client";

import { useCallback, useState } from "react";
import {
  approveAction,
  createActionPlan,
  denyAction,
  executeActionPlan,
  undoAction,
} from "@/lib/ai/actions/api";
import { formatActionError } from "@/lib/ai/actions/errors";
import {
  ActionPlanResponse,
  ExecutionReceiptDTO,
} from "@/lib/ai/actions/types";

export function useAiActionPlan() {
  const [plan, setPlan] = useState<ActionPlanResponse | null>(null);
  const [receipts, setReceipts] = useState<ExecutionReceiptDTO[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);

  const generatePlan = useCallback(
    async (intent: string, contextHints?: Record<string, any>) => {
      setIsLoading(true);
      setError(null);
      setErrorCode(null);
      setReceipts([]);
      try {
        const resp = await createActionPlan(intent, undefined, contextHints);
        setPlan(resp);
        return resp;
      } catch (err: any) {
        setErrorCode(err.code || "AI_ACTION_PLAN_ERROR");
        setError(formatActionError(err.code, err.message));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const approve = useCallback(
    async (actionId: string) => {
      if (!plan) return false;
      const targetAction = plan.actions.find((a) => a.action_id === actionId);
      if (!targetAction || !targetAction.preview) return false;

      setIsLoading(true);
      setError(null);
      try {
        await approveAction(
          plan.plan_id,
          actionId,
          targetAction.preview.preview_hash,
          targetAction.expected_resource_revision
        );
        // Update local plan state
        setPlan((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            actions: prev.actions.map((a) =>
              a.action_id === actionId ? { ...a, action_status: "APPROVED" } : a
            ),
          };
        });
        return true;
      } catch (err: any) {
        setErrorCode(err.code || "APPROVAL_ERROR");
        setError(formatActionError(err.code, err.message));
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [plan]
  );

  const deny = useCallback(
    async (actionId: string, reason?: string) => {
      if (!plan) return false;
      setIsLoading(true);
      setError(null);
      try {
        await denyAction(plan.plan_id, actionId, reason);
        setPlan((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            actions: prev.actions.map((a) =>
              a.action_id === actionId ? { ...a, action_status: "DENIED" } : a
            ),
          };
        });
        return true;
      } catch (err: any) {
        setErrorCode(err.code || "DENIAL_ERROR");
        setError(formatActionError(err.code, err.message));
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [plan]
  );

  const execute = useCallback(async () => {
    if (!plan) return null;
    setIsExecuting(true);
    setError(null);
    try {
      const idempotencyKey = `idem_${plan.plan_id}_${Date.now()}`;
      const resp = await executeActionPlan(plan.plan_id, idempotencyKey);
      setReceipts(resp.receipts);
      setPlan((prev) => (prev ? { ...prev, status: resp.status } : null));
      return resp;
    } catch (err: any) {
      setErrorCode(err.code || "EXECUTION_ERROR");
      setError(formatActionError(err.code, err.message));
      return null;
    } finally {
      setIsExecuting(false);
    }
  }, [plan]);

  const undo = useCallback(
    async (actionId: string, receiptId: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const resp = await undoAction(actionId, receiptId);
        // Clear receipts
        setReceipts((prev) => prev.filter((r) => r.receipt_id !== receiptId));
        return resp;
      } catch (err: any) {
        setErrorCode(err.code || "UNDO_ERROR");
        setError(formatActionError(err.code, err.message));
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clear = useCallback(() => {
    setPlan(null);
    setReceipts([]);
    setError(null);
    setErrorCode(null);
  }, []);

  return {
    plan,
    receipts,
    isLoading,
    isExecuting,
    error,
    errorCode,
    generatePlan,
    approve,
    deny,
    execute,
    undo,
    clear,
  };
}

