"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  cancelTask as apiCancelTask,
  completeTask as apiCompleteTask,
  createTask as apiCreateTask,
  getTaskCounts as apiGetTaskCounts,
  listTasks as apiListTasks,
  reopenTask as apiReopenTask,
  updateTask as apiUpdateTask,
} from "@/lib/tasks/api";
import {
  CreateTaskInput,
  Task,
  TaskCountsResponse,
  TaskStatusFilter,
  UpdateTaskInput,
} from "@/lib/tasks/types";

export interface UsePersonalTasksResult {
  tasks: Task[];
  counts: TaskCountsResponse | null;
  isLoading: boolean;
  isLoadingMore: boolean;
  isError: boolean;
  error: Error | null;
  hasMore: boolean;
  isMutating: boolean;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  createTask: (input: CreateTaskInput) => Promise<Task>;
  updateTask: (taskId: string, input: UpdateTaskInput) => Promise<Task>;
  completeTask: (taskId: string, expectedVersion?: number) => Promise<Task>;
  reopenTask: (taskId: string, expectedVersion?: number) => Promise<Task>;
  cancelTask: (taskId: string, expectedVersion?: number) => Promise<Task>;
}

export function usePersonalTasks(
  statusFilter: TaskStatusFilter = "OPEN",
  limit: number = 10
): UsePersonalTasksResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [tasks, setTasks] = useState<Task[]>([]);
  const [counts, setCounts] = useState<TaskCountsResponse | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isMutating, setIsMutating] = useState<boolean>(false);

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
        apiListTasks({ status: statusFilter, limit }, { token }),
        apiGetTaskCounts({ token }),
      ]);

      if (isMountedRef.current) {
        setTasks(listRes.items);
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
      const res = await apiListTasks(
        { status: statusFilter, limit, cursor: nextCursor },
        { token }
      );
      if (isMountedRef.current) {
        setTasks((prev) => [...prev, ...res.items]);
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

  const createTask = useCallback(
    async (input: CreateTaskInput): Promise<Task> => {
      setIsMutating(true);
      try {
        const created = await apiCreateTask(input, { token });
        if (isMountedRef.current) {
          if (statusFilter === "OPEN" || statusFilter === "ALL") {
            setTasks((prev) => [created, ...prev]);
          }
          setCounts((prev) =>
            prev
              ? {
                  ...prev,
                  open_count: prev.open_count + 1,
                  overdue_count: created.is_overdue ? prev.overdue_count + 1 : prev.overdue_count,
                }
              : null
          );
        }
        return created;
      } finally {
        if (isMountedRef.current) {
          setIsMutating(false);
        }
      }
    },
    [statusFilter, token]
  );

  const updateTask = useCallback(
    async (taskId: string, input: UpdateTaskInput): Promise<Task> => {
      setIsMutating(true);
      try {
        const updated = await apiUpdateTask(taskId, input, { token });
        if (isMountedRef.current) {
          setTasks((prev) => prev.map((t) => (t.task_id === taskId ? updated : t)));
        }
        return updated;
      } finally {
        if (isMountedRef.current) {
          setIsMutating(false);
        }
      }
    },
    [token]
  );

  const completeTask = useCallback(
    async (taskId: string, expectedVersion?: number): Promise<Task> => {
      setIsMutating(true);
      // Optimistic update
      const previousTasks = [...tasks];
      const previousCounts = counts ? { ...counts } : null;

      if (statusFilter === "OPEN") {
        setTasks((prev) => prev.filter((t) => t.task_id !== taskId));
      } else {
        setTasks((prev) =>
          prev.map((t) =>
            t.task_id === taskId
              ? { ...t, status: "COMPLETED", completed_at: new Date().toISOString() }
              : t
          )
        );
      }
      setCounts((prev) =>
        prev
          ? {
              ...prev,
              open_count: Math.max(0, prev.open_count - 1),
            }
          : null
      );

      try {
        const updated = await apiCompleteTask(taskId, expectedVersion, { token });
        if (isMountedRef.current) {
          if (statusFilter !== "OPEN") {
            setTasks((prev) => prev.map((t) => (t.task_id === taskId ? updated : t)));
          }
          // Refresh counts in background
          apiGetTaskCounts({ token }).then((c) => {
            if (isMountedRef.current) setCounts(c);
          });
        }
        return updated;
      } catch (err) {
        // Rollback on error
        if (isMountedRef.current) {
          setTasks(previousTasks);
          setCounts(previousCounts);
        }
        throw err;
      } finally {
        if (isMountedRef.current) {
          setIsMutating(false);
        }
      }
    },
    [tasks, counts, statusFilter, token]
  );

  const reopenTask = useCallback(
    async (taskId: string, expectedVersion?: number): Promise<Task> => {
      setIsMutating(true);
      const previousTasks = [...tasks];
      const previousCounts = counts ? { ...counts } : null;

      if (statusFilter === "COMPLETED") {
        setTasks((prev) => prev.filter((t) => t.task_id !== taskId));
      } else {
        setTasks((prev) =>
          prev.map((t) =>
            t.task_id === taskId
              ? { ...t, status: "OPEN", completed_at: null }
              : t
          )
        );
      }
      setCounts((prev) =>
        prev
          ? {
              ...prev,
              open_count: prev.open_count + 1,
            }
          : null
      );

      try {
        const updated = await apiReopenTask(taskId, expectedVersion, { token });
        if (isMountedRef.current) {
          if (statusFilter !== "COMPLETED") {
            setTasks((prev) => prev.map((t) => (t.task_id === taskId ? updated : t)));
          }
          apiGetTaskCounts({ token }).then((c) => {
            if (isMountedRef.current) setCounts(c);
          });
        }
        return updated;
      } catch (err) {
        if (isMountedRef.current) {
          setTasks(previousTasks);
          setCounts(previousCounts);
        }
        throw err;
      } finally {
        if (isMountedRef.current) {
          setIsMutating(false);
        }
      }
    },
    [tasks, counts, statusFilter, token]
  );

  const cancelTask = useCallback(
    async (taskId: string, expectedVersion?: number): Promise<Task> => {
      setIsMutating(true);
      const previousTasks = [...tasks];
      const previousCounts = counts ? { ...counts } : null;

      if (statusFilter === "OPEN") {
        setTasks((prev) => prev.filter((t) => t.task_id !== taskId));
      } else {
        setTasks((prev) =>
          prev.map((t) =>
            t.task_id === taskId
              ? { ...t, status: "CANCELLED", cancelled_at: new Date().toISOString() }
              : t
          )
        );
      }
      setCounts((prev) =>
        prev
          ? {
              ...prev,
              open_count: Math.max(0, prev.open_count - 1),
            }
          : null
      );

      try {
        const updated = await apiCancelTask(taskId, expectedVersion, { token });
        if (isMountedRef.current) {
          if (statusFilter !== "OPEN") {
            setTasks((prev) => prev.map((t) => (t.task_id === taskId ? updated : t)));
          }
          apiGetTaskCounts({ token }).then((c) => {
            if (isMountedRef.current) setCounts(c);
          });
        }
        return updated;
      } catch (err) {
        if (isMountedRef.current) {
          setTasks(previousTasks);
          setCounts(previousCounts);
        }
        throw err;
      } finally {
        if (isMountedRef.current) {
          setIsMutating(false);
        }
      }
    },
    [tasks, counts, statusFilter, token]
  );

  return {
    tasks,
    counts,
    isLoading,
    isLoadingMore,
    isError,
    error,
    hasMore,
    isMutating,
    refetch,
    loadMore,
    createTask,
    updateTask,
    completeTask,
    reopenTask,
    cancelTask,
  };
}
