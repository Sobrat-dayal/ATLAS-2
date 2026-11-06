"use client";

import React, { useState } from "react";
import { DepartmentRegistry } from "./departments/DepartmentRegistry";
import { TeamRegistry } from "./teams/TeamRegistry";
import { TeamBuilder } from "./teams/TeamBuilder";
import { TaskRegistry } from "./tasks/TaskRegistry";
import { AgentWorkforceDashboard } from "./operations/AgentWorkforceDashboard";
import type {
  AgentDefinition,
  ApprovalRequest,
  DepartmentDefinition,
  DepartmentTemplate,
  OperationsOverview,
  AgentTask,
  TeamDefinition,
} from "@/lib/agents/types";

interface AgentsHubProps {
  initialDepartments?: DepartmentDefinition[];
  initialTeams?: TeamDefinition[];
  initialTasks?: AgentTask[];
  availableAgents?: AgentDefinition[];
  templates?: DepartmentTemplate[];
  overview?: OperationsOverview;
  pendingApprovals?: ApprovalRequest[];
}

export const AgentsHub: React.FC<AgentsHubProps> = ({
  initialDepartments = [],
  initialTeams = [],
  initialTasks = [],
  availableAgents = [],
  templates = [],
  overview,
  pendingApprovals = [],
}) => {
  const [activeTab, setActiveTab] = useState<"overview" | "departments" | "teams" | "tasks">("overview");
  const [isBuildingTeam, setIsBuildingTeam] = useState(false);

  return (
    <div className="space-y-4 p-4 min-h-[calc(100vh-4rem)] bg-[#070707] text-zinc-200 font-mono">
      {/* Cockpit Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-3 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold uppercase tracking-wider text-zinc-100">
              ATLAS AGENTS V3 — ENTERPRISE ORCHESTRATION COCKPIT
            </h1>
            <span className="rounded bg-emerald-950 border border-emerald-800 px-1.5 py-0.5 text-[10px] text-emerald-400 font-semibold">
              STAGE 148
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Autonomous multi-agent teams, specialized AI departments, collaborative task DAGs, and governed human approvals.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex rounded border border-zinc-800 bg-[#111] p-0.5 text-xs">
          <button
            onClick={() => {
              setActiveTab("overview");
              setIsBuildingTeam(false);
            }}
            className={`rounded px-3 py-1 font-medium transition ${
              activeTab === "overview"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Workforce Overview
          </button>
          <button
            onClick={() => {
              setActiveTab("departments");
              setIsBuildingTeam(false);
            }}
            className={`rounded px-3 py-1 font-medium transition ${
              activeTab === "departments"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Departments
          </button>
          <button
            onClick={() => setActiveTab("teams")}
            className={`rounded px-3 py-1 font-medium transition ${
              activeTab === "teams"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Teams
          </button>
          <button
            onClick={() => {
              setActiveTab("tasks");
              setIsBuildingTeam(false);
            }}
            className={`rounded px-3 py-1 font-medium transition ${
              activeTab === "tasks"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Tasks &amp; DAG
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      <div className="pt-2">
        {activeTab === "overview" && (
          <AgentWorkforceDashboard
            overview={overview}
            pendingApprovals={pendingApprovals}
          />
        )}

        {activeTab === "departments" && (
          <DepartmentRegistry
            initialDepartments={initialDepartments}
            templates={templates}
          />
        )}

        {activeTab === "teams" && (
          <>
            {isBuildingTeam ? (
              <TeamBuilder
                availableAgents={availableAgents}
                departments={initialDepartments}
                onSaveTeam={() => setIsBuildingTeam(false)}
                onCancel={() => setIsBuildingTeam(false)}
              />
            ) : (
              <TeamRegistry
                initialTeams={initialTeams}
                onCreateTeamClick={() => setIsBuildingTeam(true)}
              />
            )}
          </>
        )}

        {activeTab === "tasks" && (
          <TaskRegistry
            initialTasks={initialTasks}
          />
        )}
      </div>
    </div>
  );
};
