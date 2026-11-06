"use client";

import React, { useState } from "react";
import type { AgentTask, TaskPriority, TaskStatus } from "@/lib/agents/types";

interface TaskRegistryProps {
  initialTasks?: AgentTask[];
  onSelectTask?: (task: AgentTask) => void;
  onPlanTask?: (taskId: string) => void;
  onRunTask?: (taskId: string) => void;
  onCancelTask?: (taskId: string) => void;
  onCreateTaskClick?: () => void;
}

export const TaskRegistry: React.FC<TaskRegistryProps> = ({
  initialTasks = [],
  onSelectTask,
  onPlanTask,
  onRunTask,
  onCancelTask,
  onCreateTaskClick,
}) => {
  const [tasks, setTasks] = useState<AgentTask[]>(initialTasks);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const statusColor = (status: TaskStatus) => {
    switch (status) {
      case "COMPLETED":
        return "text-emerald-400 bg-emerald-950/40 border-emerald-800";
      case "RUNNING":
        return "text-blue-400 bg-blue-950/40 border-blue-800 animate-pulse";
      case "PLANNED":
      case "ASSIGNED":
        return "text-indigo-400 bg-indigo-950/40 border-indigo-800";
      case "APPROVAL_REQUIRED":
        return "text-amber-400 bg-amber-950/40 border-amber-800";
      case "BLOCKED":
        return "text-red-400 bg-red-950/40 border-red-800";
      case "CANCELLED":
        return "text-zinc-500 bg-zinc-900 border-zinc-700";
      default:
        return "text-zinc-400 bg-zinc-900 border-zinc-800";
    }
  };

  const priorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case "CRITICAL":
        return "text-red-400 font-bold";
      case "HIGH":
        return "text-amber-400 font-semibold";
      case "NORMAL":
        return "text-zinc-300";
      case "LOW":
        return "text-zinc-500";
    }
  };

  const filteredTasks = tasks.filter((t) => (statusFilter === "ALL" ? true : t.status === statusFilter));

  return (
    <div className="space-y-4 text-zinc-200">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-100">
            DURABLE TASK REGISTRY
          </h2>
          <p className="text-xs text-zinc-400">
            Durable task lifecycle management, decomposition graphs, dependency tracking, and execution runs.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded border border-zinc-700 bg-[#121212] px-2.5 py-1 text-xs text-zinc-300 font-mono"
          >
            <option value="ALL">All Statuses</option>
            <option value="CREATED">Created</option>
            <option value="PLANNED">Planned</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="RUNNING">Running</option>
            <option value="APPROVAL_REQUIRED">Approval Required</option>
            <option value="COMPLETED">Completed</option>
            <option value="BLOCKED">Blocked</option>
          </select>

          {onCreateTaskClick && (
            <button
              onClick={onCreateTaskClick}
              className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition"
            >
              + Create Task
            </button>
          )}
        </div>
      </div>

      <div className="overflow-x-auto rounded border border-zinc-800 bg-[#0c0c0c]">
        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-zinc-800 bg-[#121212] text-zinc-400">
            <tr>
              <th className="px-3 py-2">Task Title</th>
              <th className="px-3 py-2">Priority</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Assigned Agent</th>
              <th className="px-3 py-2">Dependencies</th>
              <th className="px-3 py-2">Tokens / Cost</th>
              <th className="px-3 py-2">Artifacts</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {filteredTasks.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-3 py-6 text-center text-zinc-500">
                  No tasks found matching filter.
                </td>
              </tr>
            ) : (
              filteredTasks.map((t) => (
                <tr
                  key={t.task_id}
                  onClick={() => onSelectTask?.(t)}
                  className="hover:bg-zinc-900/40 cursor-pointer transition"
                >
                  <td className="px-3 py-2 font-medium text-zinc-200">
                    <div className="flex items-center space-x-1.5">
                      {t.parent_task_id && <span className="text-zinc-600">↳</span>}
                      <span>{t.title}</span>
                    </div>
                    {t.error_message && (
                      <div className="text-[10px] text-red-400 mt-0.5 truncate max-w-sm">
                        {t.error_message}
                      </div>
                    )}
                  </td>
                  <td className={`px-3 py-2 ${priorityColor(t.priority)}`}>{t.priority}</td>
                  <td className="px-3 py-2">
                    <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold border ${statusColor(t.status)}`}>
                      {t.status}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-zinc-400">
                    {t.assigned_agent_id ? `${t.assigned_agent_id.slice(0, 10)}...` : "Unassigned"}
                  </td>
                  <td className="px-3 py-2 text-zinc-500">{t.dependencies.length} deps</td>
                  <td className="px-3 py-2 text-zinc-300">
                    {t.tokens_used.toLocaleString()} tok / ${t.cost_estimate_usd.toFixed(4)}
                  </td>
                  <td className="px-3 py-2 text-indigo-400">{t.artifacts.length} verified</td>
                  <td className="px-3 py-2 text-right space-x-1" onClick={(e) => e.stopPropagation()}>
                    {t.status === "CREATED" && (
                      <button
                        onClick={() => onPlanTask?.(t.task_id)}
                        className="rounded border border-indigo-800 bg-indigo-950/30 px-2 py-0.5 text-[10px] text-indigo-400 hover:bg-indigo-900/50"
                      >
                        Plan
                      </button>
                    )}
                    {["ASSIGNED", "PLANNED", "APPROVAL_REQUIRED"].includes(t.status) && (
                      <button
                        onClick={() => onRunTask?.(t.task_id)}
                        className="rounded border border-emerald-800 bg-emerald-950/30 px-2 py-0.5 text-[10px] text-emerald-400 hover:bg-emerald-900/50"
                      >
                        Run
                      </button>
                    )}
                    {!["COMPLETED", "CANCELLED"].includes(t.status) && (
                      <button
                        onClick={() => onCancelTask?.(t.task_id)}
                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-0.5 text-[10px] text-zinc-400 hover:bg-zinc-800"
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

