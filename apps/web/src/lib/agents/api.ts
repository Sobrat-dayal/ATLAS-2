/**
 * ATLAS Stage 148: Enterprise Multi-Agent, Department, Team, Task, and Operations API Client.
 */

import type {
  AgentDefinition,
  AgentMessage,
  AgentTask,
  ApprovalRequest,
  DepartmentDefinition,
  DepartmentTemplate,
  MessageType,
  OperationsOverview,
  ReviewStatus,
  TaskPriority,
  TeamDefinition,
  TeamRole,
} from "./types";

const BASE = "/api/v1/agents";

// ============================================================================
// Departments
// ============================================================================

export async function listDepartments(): Promise<DepartmentDefinition[]> {
  const r = await fetch(`${BASE}/departments`);
  if (!r.ok) throw new Error(`listDepartments error: ${r.status}`);
  return r.json();
}

export async function listDepartmentTemplates(): Promise<DepartmentTemplate[]> {
  const r = await fetch(`${BASE}/departments/templates`);
  if (!r.ok) throw new Error(`listDepartmentTemplates error: ${r.status}`);
  return r.json();
}

export async function createDepartment(payload: {
  name: string;
  description?: string;
  purpose?: string;
  knowledge_scope?: string;
  budget_limit_usd?: number;
  template_id?: string;
}): Promise<DepartmentDefinition> {
  const r = await fetch(`${BASE}/departments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`createDepartment error: ${r.status}`);
  return r.json();
}

export async function activateDepartment(departmentId: string): Promise<DepartmentDefinition> {
  const r = await fetch(`${BASE}/departments/${departmentId}/activate`, { method: "POST" });
  if (!r.ok) throw new Error(`activateDepartment error: ${r.status}`);
  return r.json();
}

export async function pauseDepartment(departmentId: string): Promise<DepartmentDefinition> {
  const r = await fetch(`${BASE}/departments/${departmentId}/pause`, { method: "POST" });
  if (!r.ok) throw new Error(`pauseDepartment error: ${r.status}`);
  return r.json();
}

export async function disableDepartment(departmentId: string): Promise<DepartmentDefinition> {
  const r = await fetch(`${BASE}/departments/${departmentId}/disable`, { method: "POST" });
  if (!r.ok) throw new Error(`disableDepartment error: ${r.status}`);
  return r.json();
}

// ============================================================================
// Teams
// ============================================================================

export async function listTeams(departmentId?: string): Promise<TeamDefinition[]> {
  const url = departmentId
    ? `${BASE}/teams?department_id=${encodeURIComponent(departmentId)}`
    : `${BASE}/teams`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`listTeams error: ${r.status}`);
  return r.json();
}

export async function getTeam(teamId: string): Promise<TeamDefinition> {
  const r = await fetch(`${BASE}/teams/${teamId}`);
  if (!r.ok) throw new Error(`getTeam error: ${r.status}`);
  return r.json();
}

export async function createTeam(payload: {
  name: string;
  description?: string;
  objective: string;
  department_id?: string;
  budget_limit_usd?: number;
  max_concurrency?: number;
  review_required?: boolean;
  members: Array<{ agent_id: string; role: TeamRole; max_concurrency?: number }>;
}): Promise<TeamDefinition> {
  const r = await fetch(`${BASE}/teams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`createTeam error: ${r.status}`);
  return r.json();
}

export async function publishTeam(teamId: string): Promise<TeamDefinition> {
  const r = await fetch(`${BASE}/teams/${teamId}/publish`, { method: "POST" });
  if (!r.ok) throw new Error(`publishTeam error: ${r.status}`);
  return r.json();
}

export async function activateTeam(teamId: string): Promise<TeamDefinition> {
  const r = await fetch(`${BASE}/teams/${teamId}/activate`, { method: "POST" });
  if (!r.ok) throw new Error(`activateTeam error: ${r.status}`);
  return r.json();
}

export async function disableTeam(teamId: string): Promise<TeamDefinition> {
  const r = await fetch(`${BASE}/teams/${teamId}/disable`, { method: "POST" });
  if (!r.ok) throw new Error(`disableTeam error: ${r.status}`);
  return r.json();
}

// ============================================================================
// Tasks
// ============================================================================

export async function listTasks(params?: {
  department_id?: string;
  team_id?: string;
  project_id?: string;
  status?: string;
}): Promise<AgentTask[]> {
  const query = new URLSearchParams();
  if (params?.department_id) query.set("department_id", params.department_id);
  if (params?.team_id) query.set("team_id", params.team_id);
  if (params?.project_id) query.set("project_id", params.project_id);
  if (params?.status) query.set("status", params.status);

  const r = await fetch(`${BASE}/tasks?${query.toString()}`);
  if (!r.ok) throw new Error(`listTasks error: ${r.status}`);
  return r.json();
}

export async function getTask(taskId: string): Promise<AgentTask> {
  const r = await fetch(`${BASE}/tasks/${taskId}`);
  if (!r.ok) throw new Error(`getTask error: ${r.status}`);
  return r.json();
}

export async function createTask(payload: {
  title: string;
  description?: string;
  priority?: TaskPriority;
  department_id?: string;
  team_id?: string;
  project_id?: string;
  parent_task_id?: string;
  assigned_agent_id?: string;
  input_data?: Record<string, unknown>;
  expected_output_schema?: Record<string, unknown>;
  dependencies?: string[];
  budget_limit_usd?: number;
  deadline?: string;
  requires_human_approval?: boolean;
}): Promise<AgentTask> {
  const r = await fetch(`${BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`createTask error: ${r.status}`);
  return r.json();
}

export async function planTask(taskId: string): Promise<AgentTask[]> {
  const r = await fetch(`${BASE}/tasks/${taskId}/plan`, { method: "POST" });
  if (!r.ok) throw new Error(`planTask error: ${r.status}`);
  return r.json();
}

export async function assignTask(taskId: string, agentId: string): Promise<AgentTask> {
  const r = await fetch(`${BASE}/tasks/${taskId}/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id: agentId }),
  });
  if (!r.ok) throw new Error(`assignTask error: ${r.status}`);
  return r.json();
}

export async function runTask(taskId: string): Promise<AgentTask> {
  const r = await fetch(`${BASE}/tasks/${taskId}/run`, { method: "POST" });
  if (!r.ok) throw new Error(`runTask error: ${r.status}`);
  return r.json();
}

export async function cancelTask(taskId: string): Promise<AgentTask> {
  const r = await fetch(`${BASE}/tasks/${taskId}/cancel`, { method: "POST" });
  if (!r.ok) throw new Error(`cancelTask error: ${r.status}`);
  return r.json();
}

export async function getTaskMessages(taskId: string): Promise<AgentMessage[]> {
  const r = await fetch(`${BASE}/tasks/${taskId}/messages`);
  if (!r.ok) throw new Error(`getTaskMessages error: ${r.status}`);
  return r.json();
}

export async function sendTaskMessage(
  taskId: string,
  payload: {
    team_id: string;
    sender_agent_id: string;
    recipient_agent_id: string;
    message_type: MessageType;
    payload: Record<string, unknown>;
    correlation_id?: string;
  }
): Promise<AgentMessage> {
  const r = await fetch(`${BASE}/tasks/${taskId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`sendTaskMessage error: ${r.status}`);
  return r.json();
}

export async function submitTaskReview(
  taskId: string,
  payload: {
    reviewer_agent_id: string;
    status: ReviewStatus;
    feedback?: string;
  }
): Promise<unknown> {
  const r = await fetch(`${BASE}/tasks/${taskId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`submitTaskReview error: ${r.status}`);
  return r.json();
}

// ============================================================================
// Operations & Approvals
// ============================================================================

export async function getOperationsOverview(): Promise<OperationsOverview> {
  const r = await fetch(`${BASE}/operations/overview`);
  if (!r.ok) throw new Error(`getOperationsOverview error: ${r.status}`);
  return r.json();
}

export async function getOperationsHealth(): Promise<Record<string, unknown>> {
  const r = await fetch(`${BASE}/operations/health`);
  if (!r.ok) throw new Error(`getOperationsHealth error: ${r.status}`);
  return r.json();
}

export async function getOperationsUsage(): Promise<Record<string, unknown>> {
  const r = await fetch(`${BASE}/operations/usage`);
  if (!r.ok) throw new Error(`getOperationsUsage error: ${r.status}`);
  return r.json();
}

export async function listApprovals(): Promise<ApprovalRequest[]> {
  const r = await fetch(`${BASE}/approvals`);
  if (!r.ok) throw new Error(`listApprovals error: ${r.status}`);
  return r.json();
}

export async function resolveApproval(
  approvalId: string,
  decision: "APPROVED" | "REJECTED",
  reason?: string
): Promise<ApprovalRequest> {
  const r = await fetch(`${BASE}/approvals/${approvalId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, reason }),
  });
  if (!r.ok) throw new Error(`resolveApproval error: ${r.status}`);
  return r.json();
}

// ============================================================================
// Agents
// ============================================================================

export async function listAgents(): Promise<AgentDefinition[]> {
  const r = await fetch(BASE);
  if (!r.ok) throw new Error(`listAgents error: ${r.status}`);
  return r.json();
}
