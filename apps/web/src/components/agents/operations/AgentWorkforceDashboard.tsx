"use client";

import React from "react";
import type { ApprovalRequest, OperationsOverview } from "@/lib/agents/types";

interface AgentWorkforceDashboardProps {
  overview?: OperationsOverview;
  pendingApprovals?: ApprovalRequest[];
  onResolveApproval?: (approvalId: string, decision: "APPROVED" | "REJECTED", reason?: string) => void;
}

export const AgentWorkforceDashboard: React.FC<AgentWorkforceDashboardProps> = ({
  overview,
  pendingApprovals = [],
  onResolveApproval,
}) => {
  const defaultOverview: OperationsOverview = overview || {
    departments_count: 15,
    teams_count: 6,
    active_teams_count: 4,
    total_tasks: 28,
    running_tasks: 3,
    completed_tasks: 22,
    blocked_tasks: 1,
    pending_approvals_count: pendingApprovals.length,
    total_model_calls: 142,
    total_tokens_used: 184500,
    total_estimated_cost_usd: 0.742,
    worker_health: {
      status: "HEALTHY",
      active_workers: 4,
      queue_depth: 2,
      error_rate: 0.035,
      live_money_trading_enabled: false,
    },
  };

  return (
    <div className="space-y-6 text-zinc-200 font-mono text-xs">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Departments</div>
          <div className="text-xl font-bold text-zinc-100 mt-1">{defaultOverview.departments_count}</div>
          <div className="text-[10px] text-zinc-400 mt-0.5">Specialized units</div>
        </div>

        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Active Teams</div>
          <div className="text-xl font-bold text-emerald-400 mt-1">{defaultOverview.active_teams_count}</div>
          <div className="text-[10px] text-zinc-400 mt-0.5">of {defaultOverview.teams_count} total squads</div>
        </div>

        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Total Tasks</div>
          <div className="text-xl font-bold text-zinc-100 mt-1">{defaultOverview.total_tasks}</div>
          <div className="text-[10px] text-zinc-400 mt-0.5">{defaultOverview.completed_tasks} completed</div>
        </div>

        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Pending Approvals</div>
          <div className={`text-xl font-bold mt-1 ${defaultOverview.pending_approvals_count > 0 ? "text-amber-400" : "text-zinc-400"}`}>
            {defaultOverview.pending_approvals_count}
          </div>
          <div className="text-[10px] text-zinc-400 mt-0.5">Human gates required</div>
        </div>

        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Token Consumption</div>
          <div className="text-xl font-bold text-blue-400 mt-1">
            {defaultOverview.total_tokens_used.toLocaleString()}
          </div>
          <div className="text-[10px] text-zinc-400 mt-0.5">{defaultOverview.total_model_calls} model calls</div>
        </div>

        <div className="rounded border border-zinc-800 bg-[#0e0e0e] p-3">
          <div className="text-[10px] uppercase text-zinc-500 font-medium">Estimated Cost</div>
          <div className="text-xl font-bold text-zinc-200 mt-1">
            ${defaultOverview.total_estimated_cost_usd.toFixed(4)}
          </div>
          <div className="text-[10px] text-zinc-400 mt-0.5">USD incurred</div>
        </div>
      </div>

      {/* Safety & Execution Firewall Banner */}
      <div className="rounded border border-emerald-900/60 bg-emerald-950/20 p-3.5 flex items-center justify-between">
        <div className="space-y-0.5">
          <div className="text-xs font-semibold text-emerald-400 flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>ENTERPRISE MULTI-AGENT EXECUTION ENGINE ONLINE</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            Durable task state machine, coordinator-specialist delegation, and human governance active. Live-money broker execution: STRICTLY DISABLED.
          </div>
        </div>
        <div className="text-right">
          <span className="rounded border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-[10px] text-zinc-300">
            Mode: SANDBOX / RESEARCH
          </span>
        </div>
      </div>

      {/* Pending Human Approvals Inbox */}
      <div className="rounded border border-zinc-800 bg-[#0c0c0c] p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center space-x-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-100">
              HUMAN-IN-THE-LOOP APPROVAL INBOX
            </h3>
            {pendingApprovals.length > 0 && (
              <span className="rounded bg-amber-950 border border-amber-800 px-1.5 py-0.2 text-[10px] text-amber-400">
                {pendingApprovals.length} PENDING
              </span>
            )}
          </div>
          <div className="text-[10px] text-zinc-500">
            Protected actions cannot proceed without explicit authorized review
          </div>
        </div>

        {pendingApprovals.length === 0 ? (
          <div className="py-6 text-center text-zinc-500 text-xs">
            No pending human approvals. All high-impact actions and publication requests are cleared.
          </div>
        ) : (
          <div className="space-y-2">
            {pendingApprovals.map((appr) => (
              <div
                key={appr.approval_id}
                className="rounded border border-amber-900/50 bg-amber-950/10 p-3 flex items-center justify-between"
              >
                <div>
                  <div className="font-semibold text-zinc-200">
                    Action: {appr.action_type}
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-0.5">
                    Task ID: {appr.task_id} • Expires: {new Date(appr.expires_at).toLocaleString()}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onResolveApproval?.(appr.approval_id, "REJECTED", "Denied by authorized reviewer")}
                    className="rounded border border-red-800 bg-red-950/40 px-3 py-1 text-xs text-red-400 hover:bg-red-900/60 transition"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => onResolveApproval?.(appr.approval_id, "APPROVED", "Approved for governed dispatch")}
                    className="rounded border border-emerald-800 bg-emerald-950/40 px-3 py-1 text-xs text-emerald-400 hover:bg-emerald-900/60 transition"
                  >
                    Authorize &amp; Proceed
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
