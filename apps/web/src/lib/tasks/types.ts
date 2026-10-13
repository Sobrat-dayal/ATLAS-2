/**
 * Stage 54 Personal Tasks Domain Types.
 */

export type TaskStatus = "OPEN" | "COMPLETED" | "CANCELLED";
export type TaskStatusFilter = "OPEN" | "COMPLETED" | "CANCELLED" | "ALL";

export interface Task {
  task_id: string;
  owner_user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  due_at: string | null;
  module_id: string | null;
  entity_id: string | null;
  entity_name?: string | null;
  entity_ticker?: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  cancelled_at: string | null;
  version: number;
  is_overdue: boolean;
  is_due_soon: boolean;
}

export interface CreateTaskInput {
  title: string;
  description?: string | null;
  due_at?: string | null;
  module_id?: string | null;
  entity_id?: string | null;
  idempotency_key?: string | null;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string | null;
  due_at?: string | null;
  module_id?: string | null;
  entity_id?: string | null;
  expected_version?: number;
}

export interface TaskListResponse {
  items: Task[];
  next_cursor: string | null;
  has_more: boolean;
  total_count: number;
}

export interface TaskCountsResponse {
  open_count: number;
  overdue_count: number;
}
