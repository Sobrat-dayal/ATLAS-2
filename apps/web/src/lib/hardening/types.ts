/**
 * Stage 150: System Hardening & Launch Readiness Types
 */

export type ReadinessVerdict = "AWAITING_AUTHORIZATION" | "GO" | "NO_GO" | "BLOCKED";

export type GateStatus = "PASS" | "WARN" | "FAIL" | "PENDING_SIGN_OFF";

export interface GateEvaluation {
  gate: string;
  title: string;
  status: GateStatus;
  score: number;
  criteria_met: string[];
  criteria_unmet: string[];
  blockers: string[];
  evaluated_at: string;
}

export interface SystemReadinessReport {
  verdict: ReadinessVerdict;
  readiness_score: number;
  release_version: string;
  git_commit_sha: string;
  audit_timestamp: string;
  production_authorization_granted: boolean;
  authorized_by: string | null;
  critical_blockers: string[];
  evaluated_gates: GateEvaluation[];
}

export interface ServiceHealthCheck {
  service_name: string;
  status: "HEALTHY" | "DEGRADED" | "UNHEALTHY";
  latency_ms: number;
  message: string;
  details: Record<string, any>;
}

export interface SystemHealthReport {
  overall_status: "HEALTHY" | "DEGRADED" | "UNHEALTHY";
  timestamp: string;
  financial_safety_active: boolean;
  active_kill_switches: number;
  checks: ServiceHealthCheck[];
}

export interface SecurityAuditCheck {
  check_id: string;
  name: string;
  category: string;
  passed: boolean;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFORMATIONAL";
  evidence: string;
  remediation?: string;
}

export interface SecurityAuditReport {
  timestamp: string;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  critical_vulnerabilities: number;
  high_vulnerabilities: number;
  financial_firewall_enforced: boolean;
  ssrf_defense_enforced: boolean;
  zip_slip_defense_enforced: boolean;
  secret_scanning_enforced: boolean;
  findings: SecurityAuditCheck[];
}

export interface PerformanceBenchmarkResult {
  benchmark_id: string;
  name: string;
  operation: string;
  sample_size: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  throughput_rps: number;
  error_rate_pct: number;
  target_p95_ms: number;
  meets_target: boolean;
}

export interface DisasterRecoveryDrillResult {
  drill_id: string;
  scenario: string;
  target_environment: string;
  backup_snapshot_id: string;
  restore_started_at: string;
  restore_completed_at: string;
  duration_seconds: number;
  records_verified: number;
  integrity_checksum_match: boolean;
  replay_side_effects_suppressed: boolean;
  passed: boolean;
  notes: string;
}

export interface StageAuditEntry {
  stage_number: number;
  stage_title: string;
  status: string;
  primary_route: string;
  implementation_evidence: string;
  test_evidence: string;
  outstanding_defects: number;
}
