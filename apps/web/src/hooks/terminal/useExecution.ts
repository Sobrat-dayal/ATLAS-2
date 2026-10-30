/**
 * React hook for managing terminal command execution lifecycle and output streaming.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { executionApi } from "@/lib/terminal/executionApi";
import type {
  ExecutionOutputChunk,
  ExecutionSubmitRequest,
  TerminalExecutionDetail,
} from "@/lib/terminal/executionTypes";

export function useExecution(sessionId: string) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentExecution, setCurrentExecution] = useState<TerminalExecutionDetail | null>(null);
  const [outputChunks, setOutputChunks] = useState<ExecutionOutputChunk[]>([]);
  const [error, setError] = useState<string | null>(null);

  const activeExecutionIdRef = useRef<string | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const clear = useCallback(() => {
    setCurrentExecution(null);
    setOutputChunks([]);
    setError(null);
  }, []);

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  const execute = useCallback(
    async (requestOverrides: Partial<ExecutionSubmitRequest> & { input_code: string }) => {
      setIsExecuting(true);
      setError(null);
      setOutputChunks([]);

      try {
        const payload: ExecutionSubmitRequest = {
          session_id: sessionId,
          input_code: requestOverrides.input_code,
          execution_type: requestOverrides.execution_type,
          environment_id: requestOverrides.environment_id,
          source_id: requestOverrides.source_id,
          workspace_id: requestOverrides.workspace_id,
          timeout_seconds: requestOverrides.timeout_seconds,
        };

        const exec = await executionApi.submitExecution(payload);
        setCurrentExecution(exec);
        activeExecutionIdRef.current = exec.execution_id;

        // Fetch immediate output
        const chunks = await executionApi.getExecutionOutput(exec.execution_id);
        setOutputChunks(chunks);

        if (exec.status === "COMPLETED") {
          setIsExecuting(false);
        } else if (exec.status === "FAILED") {
          setIsExecuting(false);
          setError(exec.error_message || "Execution failed.");
        } else if (
          exec.status === "TIMED_OUT" ||
          exec.status === "CANCELLED" ||
          exec.status === "SECURITY_DENIED"
        ) {
          setIsExecuting(false);
          setError(exec.error_message || `Execution ended with status ${exec.status}.`);
        } else {
          // If still running, start short status polling
          stopPolling();
          pollIntervalRef.current = setInterval(async () => {
            const execId = activeExecutionIdRef.current;
            if (!execId) {
              stopPolling();
              return;
            }

            try {
              const latest = await executionApi.getExecution(execId);
              setCurrentExecution(latest);

              const latestChunks = await executionApi.getExecutionOutput(execId);
              setOutputChunks(latestChunks);

              if (
                latest.status === "COMPLETED" ||
                latest.status === "FAILED" ||
                latest.status === "CANCELLED" ||
                latest.status === "TIMED_OUT" ||
                latest.status === "SECURITY_DENIED"
              ) {
                stopPolling();
                setIsExecuting(false);
                if (latest.status === "FAILED" || latest.status === "TIMED_OUT") {
                  setError(latest.error_message || "Execution error.");
                }
              }
            } catch {
              stopPolling();
              setIsExecuting(false);
            }
          }, 400);
        }

        return exec;
      } catch (err: any) {
        setIsExecuting(false);
        const errMsg = err?.message || "Execution failed to start.";
        setError(errMsg);
        throw err;
      }
    },
    [sessionId, stopPolling]
  );

  const cancel = useCallback(async () => {
    const execId = activeExecutionIdRef.current;
    if (!execId) return;

    try {
      const updated = await executionApi.cancelExecution(execId);
      setCurrentExecution(updated);
      setIsExecuting(false);
      stopPolling();
    } catch (err: any) {
      console.warn("Failed to cancel execution:", err);
    }
  }, [stopPolling]);

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    isExecuting,
    currentExecution,
    outputChunks,
    error,
    execute,
    cancel,
    clear,
  };
}

