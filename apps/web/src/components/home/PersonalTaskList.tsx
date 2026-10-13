"use client";

import React, { useState } from "react";
import { AlertCircle, CheckSquare, Plus, RotateCcw } from "lucide-react";
import { Task, TaskStatusFilter } from "@/lib/tasks/types";
import { PersonalTaskRow } from "./PersonalTaskRow";

interface PersonalTaskListProps {
  tasks: Task[];
  statusFilter: TaskStatusFilter;
  onFilterChange: (filter: TaskStatusFilter) => void;
  isLoading: boolean;
  isLoadingMore: boolean;
  isError: boolean;
  error: Error | null;
  hasMore: boolean;
  isMutating: boolean;
  onRetry: () => void;
  onLoadMore: () => void;
  onOpenCreateDialog: () => void;
  onComplete: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onReopen: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onCancel: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onEdit: (task: Task) => void;
}

export function PersonalTaskList({
  tasks,
  statusFilter,
  onFilterChange,
  isLoading,
  isLoadingMore,
  isError,
  error,
  hasMore,
  isMutating,
  onRetry,
  onLoadMore,
  onOpenCreateDialog,
  onComplete,
  onReopen,
  onCancel,
  onEdit,
}: PersonalTaskListProps) {
  const filterOptions: { label: string; value: TaskStatusFilter }[] = [
    { label: "Open", value: "OPEN" },
    { label: "Completed", value: "COMPLETED" },
    { label: "Cancelled", value: "CANCELLED" },
    { label: "All", value: "ALL" },
  ];

  return (
    <div className="flex flex-col gap-3">
      {/* Sub-header Filter Tabs */}
      <div className="flex items-center justify-between gap-2 border-b border-atlas-border-subtle pb-2">
        <div className="flex items-center gap-1" role="tablist" aria-label="Task status filters">
          {filterOptions.map((opt) => {
            const isActive = statusFilter === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                role="tab"
                aria-selected={isActive}
                onClick={() => onFilterChange(opt.value)}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  isActive
                    ? "bg-atlas-surface-3 text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-secondary hover:bg-atlas-surface-2"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={onOpenCreateDialog}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-atlas-teal/10 hover:bg-atlas-teal/20 text-atlas-teal text-[11px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
        >
          <Plus className="h-3 w-3" aria-hidden="true" />
          <span>Add Task</span>
        </button>
      </div>

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="space-y-2 py-2" aria-label="Loading personal tasks">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-14 rounded border border-atlas-border-subtle bg-atlas-surface-2/40 animate-pulse"
            />
          ))}
        </div>
      )}

      {/* Error State */}
      {!isLoading && isError && (
        <div className="p-3 rounded border border-atlas-error/30 bg-atlas-error/10 text-xs text-atlas-error flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{error?.message || "Failed to load tasks."}</span>
          </div>
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1 px-2 py-1 rounded bg-atlas-error/20 hover:bg-atlas-error/30 text-atlas-error text-[11px] font-medium transition-colors"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && tasks.length === 0 && (
        <div className="py-6 px-4 text-center rounded border border-dashed border-atlas-border-subtle bg-atlas-surface-2/20 flex flex-col items-center justify-center">
          <CheckSquare className="h-6 w-6 text-atlas-text-muted mb-2 stroke-[1.5]" aria-hidden="true" />
          <p className="text-xs font-medium text-atlas-text-primary">
            {statusFilter === "OPEN" ? "No open tasks." : "No tasks found."}
          </p>
          <p className="text-[11px] text-atlas-text-muted mt-0.5 max-w-xs">
            {statusFilter === "OPEN"
              ? "Add a task to keep track of work you want to complete."
              : `No tasks match the ${statusFilter.toLowerCase()} filter.`}
          </p>
          {statusFilter === "OPEN" && (
            <button
              type="button"
              onClick={onOpenCreateDialog}
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-atlas-teal text-white text-xs font-medium hover:bg-atlas-teal/90 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
            >
              <Plus className="h-3.5 w-3.5" aria-hidden="true" />
              <span>Add Task</span>
            </button>
          )}
        </div>
      )}

      {/* Task Rows */}
      {!isLoading && !isError && tasks.length > 0 && (
        <div className="space-y-2">
          {tasks.map((task) => (
            <PersonalTaskRow
              key={task.task_id}
              task={task}
              onComplete={onComplete}
              onReopen={onReopen}
              onCancel={onCancel}
              onEdit={onEdit}
              isMutating={isMutating}
            />
          ))}

          {/* Load More Button */}
          {hasMore && (
            <div className="pt-2 text-center">
              <button
                type="button"
                onClick={onLoadMore}
                disabled={isLoadingMore}
                className="px-3 py-1 rounded text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none disabled:opacity-50"
              >
                {isLoadingMore ? "Loading..." : "Load More Tasks"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
