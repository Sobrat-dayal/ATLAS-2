/**
 * Stage 150: System Hardening & Readiness API client.
 */

import type {
  DisasterRecoveryDrillResult,
  PerformanceBenchmarkResult,
  SecurityAuditReport,
  StageAuditEntry,
  SystemHealthReport,
  SystemReadinessReport,
} from "./types";

const BASE = "/api/v1/system";

export async function getSystemHealth(): Promise<SystemHealthReport> {
  const r = await fetch(`${BASE}/health`);
  if (!r.ok) throw new Error(`getSystemHealth: ${r.status}`);
  return r.json();
}

export async function getSecurityAudit(): Promise<SecurityAuditReport> {
  const r = await fetch(`${BASE}/security-audit`);
  if (!r.ok) throw new Error(`getSecurityAudit: ${r.status}`);
  return r.json();
}

export async function getPerformanceBenchmarks(): Promise<PerformanceBenchmarkResult[]> {
  const r = await fetch(`${BASE}/benchmarks`);
  if (!r.ok) throw new Error(`getPerformanceBenchmarks: ${r.status}`);
  return r.json();
}

export async function runDisasterRecoveryDrill(targetEnvironment = "STAGING"): Promise<DisasterRecoveryDrillResult> {
  const r = await fetch(`${BASE}/dr-drill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_environment: targetEnvironment }),
  });
  if (!r.ok) throw new Error(`runDisasterRecoveryDrill: ${r.status}`);
  return r.json();
}

export async function get150StageAuditMatrix(): Promise<StageAuditEntry[]> {
  const r = await fetch(`${BASE}/stage-audit`);
  if (!r.ok) throw new Error(`get150StageAuditMatrix: ${r.status}`);
  return r.json();
}

export async function getProductionReadiness(): Promise<SystemReadinessReport> {
  const r = await fetch(`${BASE}/readiness`);
  if (!r.ok) throw new Error(`getProductionReadiness: ${r.status}`);
  return r.json();
}

export async function authorizeProductionRelease(payload: {
  signatory_name: string;
  signatory_title: string;
  confirmation_phrase: string;
}): Promise<{
  message: string;
  verdict: string;
  readiness_score: number;
  authorized_by: string;
  authorized_at: string;
}> {
  const r = await fetch(`${BASE}/readiness/authorize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error(err.detail || err.error?.message || `authorizeProductionRelease: ${r.status}`);
  }
  return r.json();
}
