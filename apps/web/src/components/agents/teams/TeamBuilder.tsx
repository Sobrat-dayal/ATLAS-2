"use client";

import React, { useState } from "react";
import type { AgentDefinition, DepartmentDefinition, TeamMember, TeamRole } from "@/lib/agents/types";

interface TeamBuilderProps {
  availableAgents: AgentDefinition[];
  departments: DepartmentDefinition[];
  onSaveTeam: (payload: {
    name: string;
    description: string;
    objective: string;
    department_id?: string;
    budget_limit_usd: number;
    max_concurrency: number;
    review_required: boolean;
    members: TeamMember[];
  }) => void;
  onCancel?: () => void;
}

const AVAILABLE_ROLES: TeamRole[] = [
  "COORDINATOR",
  "RESEARCHER",
  "ANALYST",
  "DEVELOPER",
  "TESTER",
  "REVIEWER",
  "DESIGNER",
  "WRITER",
  "SECURITY_REVIEWER",
  "PROJECT_MANAGER",
  "DATA_SPECIALIST",
  "FINANCIAL_ANALYST",
  "GENERAL_SPECIALIST",
];

export const TeamBuilder: React.FC<TeamBuilderProps> = ({
  availableAgents = [],
  departments = [],
  onSaveTeam,
  onCancel,
}) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [objective, setObjective] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [budgetLimit, setBudgetLimit] = useState(150);
  const [maxConcurrency, setMaxConcurrency] = useState(5);
  const [reviewRequired, setReviewRequired] = useState(true);
  const [members, setMembers] = useState<TeamMember[]>([]);

  const handleAddMember = (agentId: string, role: TeamRole) => {
    if (members.some((m) => m.agent_id === agentId)) return;
    setMembers((prev) => [...prev, { agent_id: agentId, role, max_concurrency: 1 }]);
  };

  const handleRemoveMember = (agentId: string) => {
    setMembers((prev) => prev.filter((m) => m.agent_id !== agentId));
  };

  const handleChangeRole = (agentId: string, newRole: TeamRole) => {
    setMembers((prev) =>
      prev.map((m) => (m.agent_id === agentId ? { ...m, role: newRole } : m))
    );
  };

  const coordinatorCount = members.filter((m) => m.role === "COORDINATOR").length;
  const isValid = name.trim().length > 0 && objective.trim().length > 0 && coordinatorCount === 1;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;

    onSaveTeam({
      name: name.trim(),
      description: description.trim(),
      objective: objective.trim(),
      department_id: departmentId || undefined,
      budget_limit_usd: budgetLimit,
      max_concurrency: maxConcurrency,
      review_required: reviewRequired,
      members,
    });
  };

  return (
    <div className="rounded border border-zinc-800 bg-[#0c0c0c] p-5 font-mono text-xs text-zinc-200">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-4">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-100">
            TEAM BUILDER &amp; COMPOSITION COCKPIT
          </h2>
          <p className="text-[11px] text-zinc-400">
            Assign agents to specialized operational roles. Exactly one COORDINATOR is required.
          </p>
        </div>
        {onCancel && (
          <button
            onClick={onCancel}
            className="rounded border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-zinc-400 hover:bg-zinc-800"
          >
            Cancel
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-zinc-400 mb-1">Team Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded border border-zinc-700 bg-[#121212] px-2.5 py-1.5 text-zinc-200"
              placeholder="e.g. Statistical Arbitrage Squad"
            />
          </div>

          <div>
            <label className="block text-zinc-400 mb-1">Governing Department</label>
            <select
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              className="w-full rounded border border-zinc-700 bg-[#121212] px-2.5 py-1.5 text-zinc-200"
            >
              <option value="">-- Unassigned (Direct Tenant Scope) --</option>
              {departments.map((d) => (
                <option key={d.department_id} value={d.department_id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-zinc-400 mb-1">Team Mission &amp; Objective *</label>
          <textarea
            required
            rows={2}
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            className="w-full rounded border border-zinc-700 bg-[#121212] px-2.5 py-1.5 text-zinc-200"
            placeholder="Bounded operational mission and deliverable expectations"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-zinc-400 mb-1">Budget Limit (USD)</label>
            <input
              type="number"
              min="0"
              value={budgetLimit}
              onChange={(e) => setBudgetLimit(Number(e.target.value))}
              className="w-full rounded border border-zinc-700 bg-[#121212] px-2.5 py-1.5 text-zinc-200"
            />
          </div>
          <div>
            <label className="block text-zinc-400 mb-1">Max Concurrency</label>
            <input
              type="number"
              min="1"
              max="20"
              value={maxConcurrency}
              onChange={(e) => setMaxConcurrency(Number(e.target.value))}
              className="w-full rounded border border-zinc-700 bg-[#121212] px-2.5 py-1.5 text-zinc-200"
            />
          </div>
          <div className="flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              id="reviewRequired"
              checked={reviewRequired}
              onChange={(e) => setReviewRequired(e.target.checked)}
              className="rounded border-zinc-700"
            />
            <label htmlFor="reviewRequired" className="text-zinc-300">
              Mandatory Reviewer Verification
            </label>
          </div>
        </div>

        {/* Team Members Section */}
        <div className="border border-zinc-800 rounded bg-[#111] p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-zinc-200 text-xs">TEAM MEMBERSHIP ({members.length} Agents)</h3>
            <span
              className={`text-[10px] px-2 py-0.5 rounded border ${
                coordinatorCount === 1
                  ? "text-emerald-400 border-emerald-800 bg-emerald-950/40"
                  : "text-amber-400 border-amber-800 bg-amber-950/40"
              }`}
            >
              {coordinatorCount === 1 ? "1 Coordinator Selected (Valid)" : "Exactly 1 Coordinator Required"}
            </span>
          </div>

          {/* Members Table */}
          {members.length > 0 && (
            <div className="overflow-x-auto rounded border border-zinc-800 bg-[#0c0c0c]">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-zinc-800 text-zinc-500 bg-[#161616]">
                  <tr>
                    <th className="px-3 py-1.5">Agent</th>
                    <th className="px-3 py-1.5">Operational Role</th>
                    <th className="px-3 py-1.5">Max Concurrency</th>
                    <th className="px-3 py-1.5 text-right">Remove</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {members.map((m) => {
                    const agent = availableAgents.find((a) => a.agent_id === m.agent_id);
                    return (
                      <tr key={m.agent_id}>
                        <td className="px-3 py-1.5 text-zinc-200">
                          {agent ? agent.name : m.agent_id}
                        </td>
                        <td className="px-3 py-1.5">
                          <select
                            value={m.role}
                            onChange={(e) => handleChangeRole(m.agent_id, e.target.value as TeamRole)}
                            className="rounded border border-zinc-700 bg-[#121212] px-2 py-1 text-zinc-200 text-[11px]"
                          >
                            {AVAILABLE_ROLES.map((r) => (
                              <option key={r} value={r}>
                                {r}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="px-3 py-1.5 text-zinc-400">{m.max_concurrency}</td>
                        <td className="px-3 py-1.5 text-right">
                          <button
                            type="button"
                            onClick={() => handleRemoveMember(m.agent_id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            ×
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Add Available Agents */}
          <div className="pt-2">
            <label className="block text-zinc-400 mb-1 text-[11px]">Select Agent to Add to Squad:</label>
            <div className="flex flex-wrap gap-2">
              {availableAgents
                .filter((a) => !members.some((m) => m.agent_id === a.agent_id))
                .slice(0, 10)
                .map((a) => (
                  <button
                    key={a.agent_id}
                    type="button"
                    onClick={() => handleAddMember(a.agent_id, members.length === 0 ? "COORDINATOR" : "SPECIALIST")}
                    className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-[11px] text-zinc-300 hover:bg-zinc-800 hover:border-zinc-500"
                  >
                    + {a.name} ({a.role})
                  </button>
                ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="rounded border border-zinc-700 px-3 py-1.5 text-zinc-400 hover:bg-zinc-800"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={!isValid}
            className={`rounded px-4 py-1.5 font-semibold text-xs border ${
              isValid
                ? "bg-emerald-950 border-emerald-700 text-emerald-400 hover:bg-emerald-900"
                : "bg-zinc-900 border-zinc-800 text-zinc-600 cursor-not-allowed"
            }`}
          >
            Save &amp; Register Team
          </button>
        </div>
      </form>
    </div>
  );
};
