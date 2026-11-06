"""ATLAS Stage 150: Final Production Hardening & Launch Readiness Domain Contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ReadinessVerdict(str, Enum):
    GO = "GO"
    NO_GO = "NO_GO"
    AWAITING_AUTHORIZATION = "AWAITING_AUTHORIZATION"


class GateStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"


class ReadinessGate(str, Enum):
    GATE_A_FUNCTIONAL = "GATE_A_FUNCTIONAL"
    GATE_B_SECURITY = "GATE_B_SECURITY"
    GATE_C_DATA_INTEGRITY = "GATE_C_DATA_INTEGRITY"
    GATE_D_RUNTIME_RELIABILITY = "GATE_D_RUNTIME_RELIABILITY"
    GATE_E_DATABASE_RELIABILITY = "GATE_E_DATABASE_RELIABILITY"
    GATE_F_OPERATIONAL_MONITORING = "GATE_F_OPERATIONAL_MONITORING"
    GATE_G_PERFORMANCE = "GATE_G_PERFORMANCE"
    GATE_H_LEGAL_PRIVACY = "GATE_H_LEGAL_PRIVACY"
    GATE_I_INFRASTRUCTURE = "GATE_I_INFRASTRUCTURE"
    GATE_J_RELEASE_AUTHORIZATION = "GATE_J_RELEASE_AUTHORIZATION"


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass
class ServiceHealthCheck:
    service_name: str
    status: HealthStatus
    latency_ms: float
    message: str
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthReport:
    overall_status: HealthStatus
    timestamp: str
    checks: List[ServiceHealthCheck]
    active_kill_switches: List[str]
    financial_safety_active: bool


@dataclass
class GateEvaluation:
    gate: ReadinessGate
    title: str
    status: GateStatus
    score: float  # 0.0 to 100.0
    criteria_met: List[str]
    criteria_unmet: List[str]
    blockers: List[str]
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SystemReadinessReport:
    verdict: ReadinessVerdict
    readiness_score: float
    evaluated_gates: List[GateEvaluation]
    critical_blockers: List[str]
    audit_timestamp: str
    release_version: str
    git_commit_sha: Optional[str] = None
    production_authorization_granted: bool = False
    authorized_by: Optional[str] = None


@dataclass
class SecurityAuditCheck:
    check_id: str
    name: str
    category: str
    passed: bool
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    evidence: str
    remediation: Optional[str] = None


@dataclass
class SecurityAuditReport:
    timestamp: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    findings: List[SecurityAuditCheck]
    financial_firewall_enforced: bool
    ssrf_defense_enforced: bool
    zip_slip_defense_enforced: bool
    secret_scanning_enforced: bool


@dataclass
class PerformanceBenchmarkResult:
    benchmark_id: str
    name: str
    operation: str
    sample_size: int
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_rps: float
    error_rate_pct: float
    target_p95_ms: float
    meets_target: bool
    memory_growth_mb: float = 0.0


@dataclass
class DisasterRecoveryDrillResult:
    drill_id: str
    scenario: str
    target_environment: str  # strictly STAGING or ISOLATED_TEST
    backup_snapshot_id: str
    backup_timestamp: str
    restore_started_at: str
    restore_completed_at: str
    duration_seconds: float
    records_verified: int
    integrity_checksum_match: bool
    replay_side_effects_suppressed: bool
    passed: bool
    notes: str


@dataclass
class StageAuditEntry:
    stage_number: int
    stage_title: str
    status: str  # VERIFIED_COMPLETE, PARTIALLY_COMPLETE, NOT_IMPLEMENTED, etc.
    primary_route: str
    implementation_evidence: str
    test_evidence: str
    outstanding_defects: List[str] = field(default_factory=list)
