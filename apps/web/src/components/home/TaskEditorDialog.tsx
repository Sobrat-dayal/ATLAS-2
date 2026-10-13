"use client";

import React, { useEffect, useRef, useState } from "react";
import { AlertCircle, Calendar, CheckSquare, X } from "lucide-react";
import { CreateTaskInput, Task, UpdateTaskInput } from "@/lib/tasks/types";
import { ATLAS_MODULES_LIST } from "@/config/atlas-modules";

interface TaskEditorDialogProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task | null; // If provided, edit mode; else create mode
  onSubmitCreate: (input: CreateTaskInput) => Promise<void>;
  onSubmitUpdate: (taskId: string, input: UpdateTaskInput) => Promise<void>;
  isSubmitting?: boolean;
}

export function TaskEditorDialog({
  isOpen,
  onClose,
  task,
  onSubmitCreate,
  onSubmitUpdate,
  isSubmitting = false,
}: TaskEditorDialogProps) {
  const isEdit = Boolean(task);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueAt, setDueAt] = useState("");
  const [moduleId, setModuleId] = useState("");
  const [entityId, setEntityId] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const dialogRef = useRef<HTMLDivElement>(null);

  // Initialize form fields when task changes or dialog opens
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || "");
      setDueAt(task.due_at ? task.due_at.slice(0, 16) : "");
      setModuleId(task.module_id || "");
      setEntityId(task.entity_id || "");
    } else {
      setTitle("");
      setDescription("");
      setDueAt("");
      setModuleId("");
      setEntityId("");
    }
    setErrorMsg(null);
  }, [task, isOpen]);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanTitle = title.trim();
    if (!cleanTitle) {
      setErrorMsg("Task title is required.");
      return;
    }
    if (cleanTitle.length > 160) {
      setErrorMsg("Title cannot exceed 160 characters.");
      return;
    }
    if (description.length > 2000) {
      setErrorMsg("Description cannot exceed 2,000 characters.");
      return;
    }

    let parsedDueAt: string | null = null;
    if (dueAt) {
      const d = new Date(dueAt);
      if (isNaN(d.getTime())) {
        setErrorMsg("Invalid due date.");
        return;
      }
      parsedDueAt = d.toISOString();
    }

    setErrorMsg(null);

    try {
      if (isEdit && task) {
        await onSubmitUpdate(task.task_id, {
          title: cleanTitle,
          description: description.trim() || null,
          due_at: parsedDueAt,
          module_id: moduleId || null,
          entity_id: entityId.trim() || null,
          expected_version: task.version,
        });
      } else {
        await onSubmitCreate({
          title: cleanTitle,
          description: description.trim() || null,
          due_at: parsedDueAt,
          module_id: moduleId || null,
          entity_id: entityId.trim() || null,
        });
      }
      onClose();
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="task-editor-dialog-title"
    >
      <div
        ref={dialogRef}
        className="relative w-full max-w-lg p-5 rounded-lg border border-atlas-border-strong bg-atlas-surface-1 shadow-2xl animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <CheckSquare className="h-4 w-4 text-atlas-teal" aria-hidden="true" />
            <h2
              id="task-editor-dialog-title"
              className="text-sm font-semibold text-atlas-text-primary"
            >
              {isEdit ? "Edit Task" : "Create Personal Task"}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Error Banner */}
        {errorMsg && (
          <div className="mt-3 p-2.5 rounded bg-atlas-error/10 border border-atlas-error/30 text-atlas-error text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5 text-xs">
          {/* Title input */}
          <div>
            <label htmlFor="task-title-input" className="block font-medium text-atlas-text-secondary mb-1">
              Title <span className="text-atlas-error">*</span>
            </label>
            <input
              id="task-title-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={160}
              placeholder="e.g. Review Q3 10-Q filing"
              required
              className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:outline-none focus:border-atlas-teal transition-colors"
            />
            <div className="text-[10px] text-atlas-text-muted text-right mt-0.5">
              {title.length}/160
            </div>
          </div>

          {/* Description input */}
          <div>
            <label htmlFor="task-desc-input" className="block font-medium text-atlas-text-secondary mb-1">
              Description (optional)
            </label>
            <textarea
              id="task-desc-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={2000}
              rows={3}
              placeholder="Add personal notes or research context..."
              className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:outline-none focus:border-atlas-teal transition-colors resize-none"
            />
            <div className="text-[10px] text-atlas-text-muted text-right mt-0.5">
              {description.length}/2000
            </div>
          </div>

          {/* Due date input */}
          <div>
            <label htmlFor="task-due-input" className="block font-medium text-atlas-text-secondary mb-1">
              Due Date & Time (optional)
            </label>
            <input
              id="task-due-input"
              type="datetime-local"
              value={dueAt}
              onChange={(e) => setDueAt(e.target.value)}
              className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary focus:outline-none focus:border-atlas-teal transition-colors"
            />
          </div>

          {/* Module & Entity Context Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label htmlFor="task-module-select" className="block font-medium text-atlas-text-secondary mb-1">
                Canonical Module (optional)
              </label>
              <select
                id="task-module-select"
                value={moduleId}
                onChange={(e) => setModuleId(e.target.value)}
                className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary focus:outline-none focus:border-atlas-teal transition-colors"
              >
                <option value="">None</option>
                {ATLAS_MODULES_LIST.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label} ({m.id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="task-entity-input" className="block font-medium text-atlas-text-secondary mb-1">
                Universal Entity UUID (optional)
              </label>
              <input
                id="task-entity-input"
                type="text"
                value={entityId}
                onChange={(e) => setEntityId(e.target.value)}
                placeholder="00000000-0000-..."
                className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:outline-none focus:border-atlas-teal transition-colors font-mono text-[11px]"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-atlas-border-subtle mt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-3 py-1.5 rounded text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim()}
              className="px-4 py-1.5 rounded bg-atlas-teal text-white font-medium hover:bg-atlas-teal/90 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal disabled:opacity-50"
            >
              {isSubmitting ? "Saving..." : isEdit ? "Save Changes" : "Create Task"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
