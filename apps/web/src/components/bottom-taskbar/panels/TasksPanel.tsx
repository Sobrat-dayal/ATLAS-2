"use client";

import React, { useState } from "react";
import { AlertCircle, CheckSquare, Plus, RotateCcw } from "lucide-react";
import { usePersonalTasks } from "@/hooks/home/usePersonalTasks";
import { Task, TaskStatusFilter } from "@/lib/tasks/types";
import { PersonalTaskRow } from "@/components/home/PersonalTaskRow";
import { TaskEditorDialog } from "@/components/home/TaskEditorDialog";

export function TasksPanel() {
  const [statusFilter, setStatusFilter] = useState<TaskStatusFilter>("OPEN");
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const {
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
  } = usePersonalTasks(statusFilter, 15);

  const handleOpenCreate = () => {
    setEditingTask(null);
    setIsEditorOpen(true);
  };

  const handleOpenEdit = (task: Task) => {
    setEditingTask(task);
    setIsEditorOpen(true);
  };

  const filterOptions: { label: string; value: TaskStatusFilter }[] = [
    { label: "Open", value: "OPEN" },
    { label: "Completed", value: "COMPLETED" },
    { label: "Cancelled", value: "CANCELLED" },
    { label: "All", value: "ALL" },
  ];

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4 select-none">
      {/* Panel Header */}
      <div className="flex items-center justify-between mb-3 border-b border-atlas-border-subtle pb-2 shrink-0">
        <div className="flex items-center gap-2">
          <CheckSquare className="h-4 w-4 text-atlas-teal" aria-hidden="true" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            Personal Tasks
          </h4>
          <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-atlas-surface-3 text-atlas-text-secondary">
            {counts?.open_count ?? 0} open
          </span>
          {counts && counts.overdue_count > 0 && (
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-atlas-error/15 text-atlas-error border border-atlas-error/30">
              {counts.overdue_count} overdue
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Status Filters */}
          <div className="flex items-center gap-1 bg-atlas-surface-2 p-0.5 rounded border border-atlas-border-subtle">
            {filterOptions.map((opt) => {
              const isActive = statusFilter === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setStatusFilter(opt.value)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    isActive
                      ? "bg-atlas-surface-3 text-atlas-text-primary shadow-xs"
                      : "text-atlas-text-muted hover:text-atlas-text-secondary"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>

          {/* Add Task button */}
          <button
            type="button"
            onClick={handleOpenCreate}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-atlas-teal text-white text-[11px] font-medium hover:bg-atlas-teal/90 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
          >
            <Plus className="h-3 w-3" aria-hidden="true" />
            <span>Add Task</span>
          </button>
        </div>
      </div>

      {/* Task List Body */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {/* Loading */}
        {isLoading && (
          <div className="space-y-2 py-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-12 rounded border border-atlas-border-subtle bg-atlas-surface-2/40 animate-pulse"
              />
            ))}
          </div>
        )}

        {/* Error */}
        {!isLoading && isError && (
          <div className="p-3 rounded border border-atlas-error/30 bg-atlas-error/10 text-xs text-atlas-error flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
              <span>{error?.message || "Failed to load personal tasks."}</span>
            </div>
            <button
              type="button"
              onClick={refetch}
              className="inline-flex items-center gap-1 px-2 py-1 rounded bg-atlas-error/20 hover:bg-atlas-error/30 text-atlas-error text-[11px] font-medium transition-colors"
            >
              <RotateCcw className="h-3 w-3" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !isError && tasks.length === 0 && (
          <div className="py-8 px-4 text-center rounded border border-dashed border-atlas-border-subtle bg-atlas-surface-2/20 flex flex-col items-center justify-center">
            <CheckSquare className="h-6 w-6 text-atlas-text-muted mb-2 stroke-[1.5]" aria-hidden="true" />
            <p className="text-xs font-medium text-atlas-text-primary">
              {statusFilter === "OPEN" ? "No open tasks." : "No tasks found."}
            </p>
            <p className="text-[11px] text-atlas-text-muted mt-0.5 max-w-xs">
              {statusFilter === "OPEN"
                ? "Add a task to keep track of personal work you want to complete."
                : `No tasks match the ${statusFilter.toLowerCase()} filter.`}
            </p>
            {statusFilter === "OPEN" && (
              <button
                type="button"
                onClick={handleOpenCreate}
                className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-atlas-teal text-white text-xs font-medium hover:bg-atlas-teal/90 transition-colors"
              >
                <Plus className="h-3.5 w-3.5" aria-hidden="true" />
                <span>Add Task</span>
              </button>
            )}
          </div>
        )}

        {/* Real Tasks */}
        {!isLoading && !isError && tasks.length > 0 && (
          <div className="space-y-2">
            {tasks.map((task) => (
              <PersonalTaskRow
                key={task.task_id}
                task={task}
                onComplete={completeTask}
                onReopen={reopenTask}
                onCancel={cancelTask}
                onEdit={handleOpenEdit}
                isMutating={isMutating}
              />
            ))}

            {hasMore && (
              <div className="pt-2 text-center">
                <button
                  type="button"
                  onClick={loadMore}
                  disabled={isLoadingMore}
                  className="px-3 py-1 rounded text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors disabled:opacity-50"
                >
                  {isLoadingMore ? "Loading..." : "Load More Tasks"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Task Creation & Editing Dialog */}
      <TaskEditorDialog
        isOpen={isEditorOpen}
        onClose={() => setIsEditorOpen(false)}
        task={editingTask}
        onSubmitCreate={async (input) => {
          await createTask(input);
        }}
        onSubmitUpdate={async (taskId, input) => {
          await updateTask(taskId, input);
        }}
        isSubmitting={isMutating}
      />
    </div>
  );
}
