"""FastAPI REST Router for Stage 150 Production Hardening & System Launch Readiness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal
from atlas.hardening.service import ProductionHardeningService
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/system", tags=["System - Production Hardening & Readiness"])

_hardening_service = ProductionHardeningService()
_authorized_signoff: Dict[str, Any] = {"granted": False, "authorized_by": None}


def get_hardening_service() -> ProductionHardeningService:
    return _hardening_service


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    tenant_id = str(principal.raw_claims.get("tenant_id", principal.sub))
    owner_id = principal.user_id
    return tenant_id, owner_id


class AuthorizeReleaseRequest(BaseModel):
    signatory_name: str = Field(..., min_length=2, max_length=120)
    signatory_title: str = Field(..., min_length=2, max_length=120)
    confirmation_phrase: str = Field(..., description="Must match 'CONFIRM_STAGE_150_PRODUCTION_LAUNCH'")


class DRDrillRequest(BaseModel):
    target_environment: str = Field(default="STAGING")


@router.get("/health")
def get_system_health(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> Dict[str, Any]:
    report = svc.probe_system_health()
    return {
        "overall_status": report.overall_status.value,
        "timestamp": report.timestamp,
        "financial_safety_active": report.financial_safety_active,
        "active_kill_switches": report.active_kill_switches,
        "checks": [
            {
                "service_name": c.service_name,
                "status": c.status.value,
                "latency_ms": c.latency_ms,
                "message": c.message,
                "details": c.details,
            }
            for c in report.checks
        ],
    }


@router.get("/security-audit")
def get_security_audit(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> Dict[str, Any]:
    report = svc.audit_security_policies()
    return {
        "timestamp": report.timestamp,
        "total_checks": report.total_checks,
        "passed_checks": report.passed_checks,
        "failed_checks": report.failed_checks,
        "critical_vulnerabilities": report.critical_vulnerabilities,
        "high_vulnerabilities": report.high_vulnerabilities,
        "financial_firewall_enforced": report.financial_firewall_enforced,
        "ssrf_defense_enforced": report.ssrf_defense_enforced,
        "zip_slip_defense_enforced": report.zip_slip_defense_enforced,
        "secret_scanning_enforced": report.secret_scanning_enforced,
        "findings": [
            {
                "check_id": f.check_id,
                "name": f.name,
                "category": f.category,
                "passed": f.passed,
                "severity": f.severity,
                "evidence": f.evidence,
                "remediation": f.remediation,
            }
            for f in report.findings
        ],
    }


@router.get("/benchmarks")
def get_performance_benchmarks(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> List[Dict[str, Any]]:
    benchmarks = svc.benchmark_system_performance()
    return [
        {
            "benchmark_id": b.benchmark_id,
            "name": b.name,
            "operation": b.operation,
            "sample_size": b.sample_size,
            "latency_p50_ms": b.latency_p50_ms,
            "latency_p95_ms": b.latency_p95_ms,
            "latency_p99_ms": b.latency_p99_ms,
            "throughput_rps": b.throughput_rps,
            "error_rate_pct": b.error_rate_pct,
            "target_p95_ms": b.target_p95_ms,
            "meets_target": b.meets_target,
        }
        for b in benchmarks
    ]


@router.post("/dr-drill")
def run_dr_drill(
    req: DRDrillRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> Dict[str, Any]:
    if req.target_environment.upper() not in {"STAGING", "ISOLATED_TEST"}:
        raise HTTPException(
            status_code=400,
            detail="Disaster recovery drills may only be executed against 'STAGING' or 'ISOLATED_TEST' environments.",
        )

    res = svc.simulate_disaster_recovery_drill(target_env=req.target_environment.upper())
    return {
        "drill_id": res.drill_id,
        "scenario": res.scenario,
        "target_environment": res.target_environment,
        "backup_snapshot_id": res.backup_snapshot_id,
        "restore_started_at": res.restore_started_at,
        "restore_completed_at": res.restore_completed_at,
        "duration_seconds": res.duration_seconds,
        "records_verified": res.records_verified,
        "integrity_checksum_match": res.integrity_checksum_match,
        "replay_side_effects_suppressed": res.replay_side_effects_suppressed,
        "passed": res.passed,
        "notes": res.notes,
    }


@router.get("/stage-audit")
def get_150_stage_audit(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> List[Dict[str, Any]]:
    matrix = svc.generate_150_stage_audit_matrix()
    return [
        {
            "stage_number": s.stage_number,
            "stage_title": s.stage_title,
            "status": s.status,
            "primary_route": s.primary_route,
            "implementation_evidence": s.implementation_evidence,
            "test_evidence": s.test_evidence,
            "outstanding_defects": s.outstanding_defects,
        }
        for s in matrix
    ]


@router.get("/readiness")
def get_production_readiness(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> Dict[str, Any]:
    report = svc.evaluate_readiness_gates(
        production_authorization_granted=_authorized_signoff["granted"],
        authorized_by=_authorized_signoff["authorized_by"],
    )
    return {
        "verdict": report.verdict.value,
        "readiness_score": report.readiness_score,
        "release_version": report.release_version,
        "git_commit_sha": report.git_commit_sha,
        "audit_timestamp": report.audit_timestamp,
        "production_authorization_granted": report.production_authorization_granted,
        "authorized_by": report.authorized_by,
        "critical_blockers": report.critical_blockers,
        "evaluated_gates": [
            {
                "gate": g.gate.value,
                "title": g.title,
                "status": g.status.value,
                "score": g.score,
                "criteria_met": g.criteria_met,
                "criteria_unmet": g.criteria_unmet,
                "blockers": g.blockers,
                "evaluated_at": g.evaluated_at,
            }
            for g in report.evaluated_gates
        ],
    }


@router.post("/readiness/authorize")
def authorize_production_release(
    req: AuthorizeReleaseRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    svc: Annotated[ProductionHardeningService, Depends(get_hardening_service)],
) -> Dict[str, Any]:
    if req.confirmation_phrase != "CONFIRM_STAGE_150_PRODUCTION_LAUNCH":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation phrase. Must be 'CONFIRM_STAGE_150_PRODUCTION_LAUNCH'.",
        )

    _authorized_signoff["granted"] = True
    _authorized_signoff["authorized_by"] = f"{req.signatory_name} ({req.signatory_title})"

    report = svc.evaluate_readiness_gates(
        production_authorization_granted=True,
        authorized_by=_authorized_signoff["authorized_by"],
    )
    return {
        "message": "Production release authorization recorded successfully.",
        "verdict": report.verdict.value,
        "readiness_score": report.readiness_score,
        "authorized_by": report.authorized_by,
        "authorized_at": datetime.now(timezone.utc).isoformat(),
    }
