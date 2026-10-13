"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  Calendar,
  Check,
  Clock,
  ExternalLink,
  MoreVertical,
  RotateCcw,
  Square,
  Trash2,
  X,
} from "lucide-react";
import { Task } from "@/lib/tasks/types";
import { ATLAS_MODULES, AtlasModuleId } from "@/config/atlas-modules";
import { useSelectedEntity } from "@/hooks/entity";
import { useAuthorization } from "@/hooks/authorization";

interface PersonalTaskRowProps {
  task: Task;
  onComplete: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onReopen: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onCancel: (taskId: string, expectedVersion: number) => Promise<unknown>;
  onEdit: (task: Task) => void;
  isMutating?: boolean;
}

export function PersonalTaskRow({
  task,
  onComplete,
  onReopen,
  onCancel,
  onEdit,
  isMutating = false,
}: PersonalTaskRowProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();
  const { canViewModule } = useAuthorization();

  const [menuOpen, setMenuOpen] = useState(false);
  const [actionPending, setActionPending] = useState(false);

  const isCompleted = task.status === "COMPLETED";
  const isCancelled = task.status === "CANCELLED";
  const isOpen = task.status === "OPEN";

  const moduleConfig = task.module_id
    ? ATLAS_MODULES[task.module_id as AtlasModuleId]
    : undefined;

  const handleToggleStatus = async () => {
    if (actionPending || isMutating) return;
    setActionPending(true);
    try {
      if (isOpen) {
        await onComplete(task.task_id, task.version);
      } else if (isCompleted) {
        await onReopen(task.task_id, task.version);
      }
    } finally {
      setActionPending(false);
    }
  };

  const handleCancel = async () => {
    if (actionPending || isMutating) return;
    setMenuOpen(false);
    setActionPending(true);
    try {
      await onCancel(task.task_id, task.version);
    } finally {
      setActionPending(false);
    }
  };

  const handleOpenContext = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (task.entity_id) {
      selectEntity(task.entity_id);
    }
    if (task.module_id) {
      const targetModule = task.module_id as AtlasModuleId;
      if (canViewModule(targetModule)) {
        router.push(`/${task.module_id}`);
      }
    }
  };

  // Format due date cleanly
  const formatDueDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div
      className={`group relative flex items-start gap-2.5 p-2.5 rounded border transition-colors ${
        isCompleted
          ? "border-atlas-border-subtle bg-atlas-surface-2/30 opacity-70"
          : isCancelled
          ? "border-atlas-border-subtle bg-atlas-surface-2/20 opacity-50 line-through"
          : "border-atlas-border-subtle bg-atlas-surface-card hover:border-atlas-border-strong hover:bg-atlas-surface-hover"
      }`}
    >
      {/* Status Checkbox */}
      <button
        type="button"
        onClick={handleToggleStatus}
        disabled={isCancelled || actionPending || isMutating}
        aria-label={
          isOpen
            ? `Mark task "${task.title}" as complete`
            : isCompleted
            ? `Reopen task "${task.title}"`
            : `Task "${task.title}" cancelled`
        }
        className={`mt-0.5 h-4 w-4 rounded flex items-center justify-center shrink-0 border transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal ${
          isCompleted
            ? "border-atlas-teal bg-atlas-teal text-white"
            : isCancelled
            ? "border-atlas-border-subtle bg-atlas-surface-3 text-atlas-text-muted cursor-not-allowed"
            : "border-atlas-border-strong bg-atlas-surface-2 text-transparent hover:border-atlas-teal"
        }`}
      >
        {isCompleted && <Check className="h-3 w-3 stroke-[3]" aria-hidden="true" />}
      </button>

      {/* Main Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <span
            className={`text-xs font-medium leading-snug break-words ${
              isCompleted
                ? "line-through text-atlas-text-muted"
                : isCancelled
                ? "text-atlas-text-muted"
                : "text-atlas-text-primary"
            }`}
          >
            {task.title}
          </span>

          {/* Action Menu button */}
          <div className="relative shrink-0">
            <button
              type="button"
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-3 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal opacity-0 group-hover:opacity-100 focus-visible:opacity-100"
              aria-label={`Options for task "${task.title}"`}
            >
              <MoreVertical className="h-3.5 w-3.5" aria-hidden="true" />
            </button>

            {menuOpen && (
              <div
                className="absolute right-0 top-6 z-20 w-32 rounded border border-atlas-border-strong bg-atlas-surface-1 py-1 shadow-lg text-xs"
                onMouseLeave={() => setMenuOpen(false)}
              >
                {isOpen && (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(false);
                        onEdit(task);
                      }}
                      className="w-full text-left px-2.5 py-1 text-atlas-text-primary hover:bg-atlas-surface-2"
                    >
                      Edit Task
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="w-full text-left px-2.5 py-1 text-atlas-error hover:bg-atlas-error/10"
                    >
                      Cancel Task
                    </button>
                  </>
                )}
                {isCompleted && (
                  <button
                    type="button"
                    onClick={() => {
                      setMenuOpen(false);
                      handleToggleStatus();
                    }}
                    className="w-full text-left px-2.5 py-1 text-atlas-text-primary hover:bg-atlas-surface-2 flex items-center gap-1.5"
                  >
                    <RotateCcw className="h-3 w-3" />
                    <span>Reopen</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Task Description (if any) */}
        {task.description && (
          <p className="text-[11px] text-atlas-text-secondary mt-0.5 line-clamp-2 break-words">
            {task.description}
          </p>
        )}

        {/* Badges / Metadata */}
        <div className="flex flex-wrap items-center gap-2 mt-2 text-[10px]">
          {/* Due date badge */}
          {task.due_at && (
            <div
              className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded font-mono font-medium ${
                task.is_overdue
                  ? "bg-atlas-error/15 text-atlas-error border border-atlas-error/30"
                  : task.is_due_soon
                  ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                  : "bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle"
              }`}
              title={
                task.is_overdue
                  ? "Task is overdue"
                  : task.is_due_soon
                  ? "Task is due within 24 hours"
                  : "Deadline"
              }
            >
              {task.is_overdue ? (
                <AlertCircle className="h-2.5 w-2.5 shrink-0" aria-hidden="true" />
              ) : (
                <Clock className="h-2.5 w-2.5 shrink-0" aria-hidden="true" />
              )}
              <span>{formatDueDate(task.due_at)}</span>
              {task.is_overdue && <span>(Overdue)</span>}
              {task.is_due_soon && !task.is_overdue && <span>(Due Soon)</span>}
            </div>
          )}

          {/* Module badge */}
          {task.module_id && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle">
              {moduleConfig?.label || task.module_id}
            </span>
          )}

          {/* Entity badge */}
          {task.entity_id && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-atlas-surface-3 text-atlas-text-primary border border-atlas-border-subtle font-mono">
              {task.entity_ticker || task.entity_name || task.entity_id.slice(0, 8)}
            </span>
          )}

          {/* Open Context button */}
          {(task.module_id || task.entity_id) && isOpen && (
            <button
              type="button"
              onClick={handleOpenContext}
              className="inline-flex items-center gap-1 text-atlas-teal hover:underline focus-visible:outline-none"
              title="Navigate to related module or entity"
            >
              <span>Open Context</span>
              <ExternalLink className="h-2.5 w-2.5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
