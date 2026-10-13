/**
 * Stage 54 Approval Requests and Decisions Domain Types.
 *
 * CRITICAL SECURITY RULE: APPROVAL IS NOT EXECUTION.
 * Approving records a human decision in PostgreSQL; it does not trigger execution.
 */

export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";
export type ApprovalDecisionType = "APPROVE" | "REJECT";
export type ApprovalStatusFilter = "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED" | "CANCELLED" | "ALL";

export interface ApprovalItem {
  approval_id: string;
  approver_user_id: string;
  producer_key: string;
  action_kind: string;
  proposal_reference: string;
  title: string;
  summary: string;
  status: ApprovalStatus;
  display_status: string; // PENDING | APPROVED | REJECTED | EXPIRED | CANCELLED
  requested_at: string;
  expires_at: string;
  decided_at: string | null;
  is_expired: boolean;
  version: number;
}

export interface DecisionRecord {
  decision_id: string;
  decision: ApprovalDecisionType;
  decided_at: string;
  reason: string | null;
}

export interface ApprovalDetail extends ApprovalItem {
  proposal_digest: string;
  decided_by_user_id: string | null;
  decision_record: DecisionRecord | null;
}

export interface ApprovalDecisionInput {
  decision: ApprovalDecisionType;
  decision_idempotency_key?: string;
  reason?: string | null;
  expected_version?: number;
}

export interface ApprovalDecisionResponse {
  approval_id: string;
  status: ApprovalStatus;
  decided_at: string;
  version: number;
  decision: ApprovalDecisionType;
  message: string;
}

export interface ApprovalListResponse {
  items: ApprovalItem[];
  next_cursor: string | null;
  has_more: boolean;
  total_count: number;
}

export interface ApprovalCountsResponse {
  pending_count: number;
}
