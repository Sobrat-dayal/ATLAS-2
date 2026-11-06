"use client";

import React, { useState } from "react";
import type { DepartmentDefinition, DepartmentTemplate } from "@/lib/agents/types";

interface DepartmentRegistryProps {
  initialDepartments?: DepartmentDefinition[];
  templates?: DepartmentTemplate[];
  onCreateDepartment?: (payload: { name: string; description: string; purpose: string; budget_limit_usd: number; template_id?: string }) => void;
  onActivateDepartment?: (deptId: string) => void;
  onDisableDepartment?: (deptId: string) => void;
}

export const DepartmentRegistry: React.FC<DepartmentRegistryProps> = ({
  initialDepartments = [],
  templates = [],
  onCreateDepartment,
  onActivateDepartment,
  onDisableDepartment,
}) => {
  const [departments, setDepartments] = useState<DepartmentDefinition[]>(initialDepartments);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [purpose, setPurpose] = useState("");
  const [budgetLimit, setBudgetLimit] = useState(500);

  const handleTemplateSelect = (tmplId: string) => {
    setSelectedTemplateId(tmplId);
    const tmpl = templates.find((t) => t.template_id === tmplId);
    if (tmpl) {
      setName(tmpl.name);
      setDescription(tmpl.description);
      setPurpose(tmpl.purpose);
    }
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const newDept: DepartmentDefinition = {
      department_id: `dept-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      purpose: purpose.trim(),
      status: "ACTIVE",
      knowledge_scope: "DEPARTMENT_ONLY",
      budget_limit_usd: budgetLimit,
      template_id: selectedTemplateId || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setDepartments((prev) => [newDept, ...prev]);
    onCreateDepartment?.({
      name: name.trim(),
      description: description.trim(),
      purpose: purpose.trim(),
      budget_limit_usd: budgetLimit,
      template_id: selectedTemplateId || undefined,
    });

    setName("");
    setDescription("");
    setPurpose("");
    setSelectedTemplateId("");
    setShowCreateModal(false);
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return "text-emerald-400 bg-emerald-950/40 border-emerald-800";
      case "READY":
      case "PUBLISHED":
        return "text-blue-400 bg-blue-950/40 border-blue-800";
      case "PAUSED":
        return "text-amber-400 bg-amber-950/40 border-amber-800";
      case "DISABLED":
        return "text-zinc-500 bg-zinc-900 border-zinc-700";
      default:
        return "text-zinc-400 bg-zinc-900 border-zinc-800";
    }
  };

  return (
    <div className="space-y-4 text-zinc-200">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-100">
            AI Department Registry
          </h2>
          <p className="text-xs text-zinc-400">
            Specialized organizational units governing autonomous multi-agent teams and domain policies.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition"
        >
          + New Department
        </button>
      </div>

      {/* Departments Table */}
      <div className="overflow-x-auto rounded border border-zinc-800 bg-[#0c0c0c]">
        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-zinc-800 bg-[#121212] text-zinc-400">
            <tr>
              <th className="px-3 py-2">Department Name</th>
              <th className="px-3 py-2">Purpose</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Knowledge Scope</th>
              <th className="px-3 py-2">Budget Limit</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {departments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-zinc-500">
                  No departments configured. Select &quot;+ New Department&quot; to initialize a specialized unit.
                </td>
              </tr>
            ) : (
              departments.map((dept) => (
                <tr key={dept.department_id} className="hover:bg-zinc-900/40 transition">
                  <td className="px-3 py-2 font-medium text-zinc-200">
                    <div>{dept.name}</div>
                    <div className="text-[10px] text-zinc-500 font-normal">{dept.description}</div>
                  </td>
                  <td className="px-3 py-2 text-zinc-400 max-w-xs truncate">{dept.purpose}</td>
                  <td className="px-3 py-2">
                    <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold border ${statusColor(dept.status)}`}>
                      {dept.status}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-zinc-400">{dept.knowledge_scope}</td>
                  <td className="px-3 py-2 text-zinc-300">${dept.budget_limit_usd.toFixed(2)}</td>
                  <td className="px-3 py-2 text-right space-x-1">
                    {dept.status !== "ACTIVE" && (
                      <button
                        onClick={() => onActivateDepartment?.(dept.department_id)}
                        className="rounded border border-emerald-800 bg-emerald-950/30 px-2 py-0.5 text-[10px] text-emerald-400 hover:bg-emerald-900/50"
                      >
                        Activate
                      </button>
                    )}
                    {dept.status !== "DISABLED" && (
                      <button
                        onClick={() => onDisableDepartment?.(dept.department_id)}
                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-0.5 text-[10px] text-zinc-400 hover:bg-zinc-800"
                      >
                        Disable
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded border border-zinc-800 bg-[#111] p-5 shadow-2xl font-mono text-xs">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-4">
              <h3 className="text-sm font-semibold text-zinc-100">CREATE AI DEPARTMENT</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-zinc-500 hover:text-zinc-300">
                ×
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3">
              {templates.length > 0 && (
                <div>
                  <label className="block text-zinc-400 mb-1">Starter Template (Optional)</label>
                  <select
                    value={selectedTemplateId}
                    onChange={(e) => handleTemplateSelect(e.target.value)}
                    className="w-full rounded border border-zinc-700 bg-[#0c0c0c] px-2 py-1.5 text-zinc-200"
                  >
                    <option value="">-- Custom Department --</option>
                    {templates.map((t) => (
                      <option key={t.template_id} value={t.template_id}>
                        {t.name} ({t.purpose.slice(0, 45)}...)
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-zinc-400 mb-1">Department Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded border border-zinc-700 bg-[#0c0c0c] px-2 py-1.5 text-zinc-200"
                  placeholder="e.g. Financial Research"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full rounded border border-zinc-700 bg-[#0c0c0c] px-2 py-1.5 text-zinc-200"
                  placeholder="Responsibilities and team scope"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Purpose / Mission</label>
                <textarea
                  rows={2}
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  className="w-full rounded border border-zinc-700 bg-[#0c0c0c] px-2 py-1.5 text-zinc-200"
                  placeholder="Governing objectives and output standards"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Budget Limit (USD)</label>
                <input
                  type="number"
                  min="0"
                  step="50"
                  value={budgetLimit}
                  onChange={(e) => setBudgetLimit(Number(e.target.value))}
                  className="w-full rounded border border-zinc-700 bg-[#0c0c0c] px-2 py-1.5 text-zinc-200"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="rounded border border-zinc-700 px-3 py-1 text-zinc-400 hover:bg-zinc-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded border border-emerald-700 bg-emerald-950 px-3 py-1 font-semibold text-emerald-400 hover:bg-emerald-900"
                >
                  Create Department
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
