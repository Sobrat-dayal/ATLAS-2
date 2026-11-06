/**
 * ATLAS Stage 148: Agents V3 — Multi-Agent Teams, Specialized AI Departments,
 * Task Management, and Enterprise Orchestration TypeScript types.
 */

export type AgentStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED" | "SUSPENDED" | "DISABLED";
export type WorkflowStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";
export type RunStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED" | "AWAITING_APPROVAL" | "QUEUED";

export type NodeType =
  | "MANUAL_TRIGGER"
  | "SCHEDULE_TRIGGER"
  | "EVENT_TRIGGER"
  | "AI_AGENT"
  | "LLM_PROMPT"
  | "STRUCTURED_OUTPUT"
  | "CONDITION"
  | "SWITCH"
  | "MERGE"
  | "DATA_MAPPING"
  | "SCHEMA_VALIDATE"
  | "WAIT"
  | "ATLAS_TOOL"
  | "MCP_TOOL"
  | "RESEARCH_QUERY"
  | "HUMAN_APPROVAL"
  | "ERROR_HANDLER"
  | "RETURN";

export interface WorkflowNode {
  node_id: string;
  node_type: NodeType;
  display_name: string;
  position_x: number;
  position_y: number;
  config: Record<string, unknown>;
}

export interface WorkflowEdge {
  edge_id: string;
  from_node_id: string;
  to_node_id: string;
  label?: string;
  condition?: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowDefinition {
  workflow_id: string;
  tenant_id: string;
  owner_id: string;
  name: string;
  description: string;
  status: WorkflowStatus;
  graph?: WorkflowGraph;
  created_at: string;
  updated_at: string;
  draft_version: number;
  published_version?: number;
}

export interface WorkflowRun {
  run_id: string;
  workflow_id: string;
  tenant_id: string;
  owner_id: string;
  status: RunStatus;
  started_at: string;
  completed_at?: string;
  error?: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
}

export type DepartmentStatus = "DRAFT" | "READY" | "ACTIVE" | "PAUSED" | "DISABLED" | "ARCHIVED";
export type TeamStatus = "DRAFT" | "READY" | "PUBLISHED" | "ACTIVE" | "PAUSED" | "DISABLED" | "ARCHIVED";

export type TeamRole =
  | "COORDINATOR"
  | "SPECIALIST"
  | "REVIEWER"
  | "PLANNER"
  | "RESEARCHER"
  | "ANALYST"
  | "DEVELOPER"
  | "TESTER"
  | "DESIGNER"
  | "WRITER"
  | "SECURITY_REVIEWER"
  | "PROJECT_MANAGER"
  | "DATA_SPECIALIST"
  | "FINANCIAL_ANALYST"
  | "GENERAL_SPECIALIST";

export type TaskStatus =
  | "CREATED"
  | "VALIDATING"
  | "PLANNED"
  | "QUEUED"
  | "ASSIGNED"
  | "RUNNING"
  | "WAITING"
  | "BLOCKED"
  | "REVIEW_REQUIRED"
  | "APPROVAL_REQUIRED"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "TIMED_OUT";

export type TaskPriority = "LOW" | "NORMAL" | "HIGH" | "CRITICAL";
export type ReviewStatus = "APPROVED" | "REVISION_REQUESTED" | "REJECTED" | "ESCALATED";
export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";

export type MessageType =
  | "TASK_ASSIGNMENT"
  | "TASK_ACCEPTED"
  | "TASK_PROGRESS"
  | "TASK_RESULT"
  | "REVIEW_REQUEST"
  | "REVIEW_RESULT"
  | "CLARIFICATION_REQUEST"
  | "BLOCKER_REPORT"
  | "ESCALATION_REQUEST"
  | "TASK_CANCELLED";

export interface AgentDefinition {
  agent_id: string;
  name: string;
  description: string;
  role: string;
  model_id?: string;
  status: AgentStatus;
  created_at?: string;
  updated_at?: string;
}

export interface DepartmentDefinition {
  department_id: string;
  name: string;
  description: string;
  purpose: string;
  status: DepartmentStatus;
  knowledge_scope: string;
  budget_limit_usd: number;
  template_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DepartmentTemplate {
  template_id: string;
  name: string;
  description: string;
  purpose: string;
  recommended_roles: string[];
  default_tools: string[];
  knowledge_scope: string;
}

export interface TeamMember {
  agent_id: string;
  role: TeamRole;
  max_concurrency: number;
  capability_profile_id?: string | null;
}

export interface TeamDefinition {
  team_id: string;
  name: string;
  description: string;
  objective: string;
  status: TeamStatus;
  version: number;
  execution_enabled: boolean;
  department_id?: string | null;
  coordinator_agent_id?: string;
  budget_limit_usd: number;
  max_concurrency: number;
  review_required: boolean;
  members: TeamMember[];
}

export interface AgentTask {
  task_id: string;
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  department_id?: string | null;
  team_id?: string | null;
  project_id?: string | null;
  parent_task_id?: string | null;
  assigned_agent_id?: string | null;
  delegation_depth: number;
  input_data: Record<string, unknown>;
  output_data?: Record<string, unknown> | null;
  dependencies: string[];
  subtask_ids: string[];
  deadline?: string | null;
  budget_limit_usd: number;
  cost_estimate_usd: number;
  tokens_used: int;
  model_calls: int;
  error_message?: string | null;
  requires_human_approval: boolean;
  approval_id?: string | null;
  review_status?: ReviewStatus | null;
  artifacts: Array<{
    artifact_id: string;
    title: string;
    type: string;
    content_summary: string;
    source_citations?: Array<{ source: string; verified: boolean }>;
    created_at: string;
  }>;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface AgentMessage {
  message_id: string;
  team_id: string;
  sender_agent_id: string;
  recipient_agent_id: string;
  message_type: MessageType;
  payload: Record<string, unknown>;
  task_id?: string | null;
  correlation_id?: string | null;
  created_at: string;
}

export interface AgentTaskReview {
  review_id: string;
  task_id: string;
  reviewer_agent_id: string;
  status: ReviewStatus;
  criteria: Record<string, unknown>;
  feedback: string;
  created_at: string;
}

export interface ApprovalRequest {
  approval_id: string;
  task_id: string;
  action_type: string;
  action_payload: Record<string, unknown>;
  status: ApprovalStatus;
  requested_at: string;
  expires_at: string;
  decided_at?: string | null;
  decided_by?: string | null;
  reason?: string | null;
}

export interface OperationsOverview {
  departments_count: number;
  teams_count: number;
  active_teams_count: number;
  total_tasks: number;
  running_tasks: number;
  completed_tasks: number;
  blocked_tasks: number;
  pending_approvals_count: number;
  total_model_calls: number;
  total_tokens_used: number;
  total_estimated_cost_usd: number;
  worker_health: {
    status: string;
    active_workers: number;
    queue_depth: number;
    error_rate: number;
    live_money_trading_enabled: boolean;
  };
}

export type int = number;
