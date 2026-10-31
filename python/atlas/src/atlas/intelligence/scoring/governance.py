"""Model Governance, Activation, and Rollback for Intelligence Scoring (Stage 139)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from .domain import GovernanceStatus
from .errors import ScoringModelValidationError, ScoringUnauthorizedActivationError
from .models import CANONICAL_MODELS, ModelRegistry


class ScoringGovernanceAuditRecord(BaseModel):
    """Immutable audit trail entry for model lifecycle transitions."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    audit_id: str
    model_id: str
    version: str
    previous_version: Optional[str] = None
    action: str  # VALIDATE, ACTIVATE, ROLLBACK, DISABLE, RETIRE
    performed_by: str
    timestamp: str
    rationale: str
    details: Dict[str, Any] = {}


class ModelGovernanceManager:
    """Oversees model promotion gates, rollback safeguards, and governance audit trails."""

    _audit_log: List[ScoringGovernanceAuditRecord] = []

    @classmethod
    def activate_model_version(
        cls,
        model_id: str,
        version: str,
        user_id: str,
        user_roles: List[str],
        validation_manifest: Optional[Any] = None,
    ) -> ScoringGovernanceAuditRecord:
        # Check authorization (Fixture J & Security)
        authorized_roles = {"ADMIN", "RISK_ADMIN", "QUANT_LEAD", "SYSTEM"}
        if not any(r in authorized_roles for r in user_roles):
            raise ScoringUnauthorizedActivationError(user_id=user_id, action="ACTIVATE")

        model = ModelRegistry.get_model(model_id)

        # Validation gate check
        if validation_manifest and getattr(validation_manifest, "validation_status", "") == "VALIDATION_FAILED":
            raise ScoringModelValidationError(
                model_id=model_id,
                version=version,
                failure_reasons=["NDCG@10 below 0.70 threshold or excessive drift detected."],
            )

        prev_version = model.active_version
        ModelRegistry.update_active_version(model_id, version)
        model.governance_status = GovernanceStatus.ACTIVE

        record = ScoringGovernanceAuditRecord(
            audit_id=f"gov_{int(datetime.now(timezone.utc).timestamp())}",
            model_id=model_id,
            version=version,
            previous_version=prev_version,
            action="ACTIVATE",
            performed_by=user_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale=f"Promoted version '{version}' to active production.",
            details={"previous_version": prev_version},
        )
        cls._audit_log.append(record)
        return record

    @classmethod
    def rollback_model_version(
        cls,
        model_id: str,
        rollback_to_version: str,
        user_id: str,
        user_roles: List[str],
        rationale: str = "Rollback due to candidate validation failure or performance regression.",
    ) -> ScoringGovernanceAuditRecord:
        authorized_roles = {"ADMIN", "RISK_ADMIN", "QUANT_LEAD", "SYSTEM"}
        if not any(r in authorized_roles for r in user_roles):
            raise ScoringUnauthorizedActivationError(user_id=user_id, action="ROLLBACK")

        model = ModelRegistry.get_model(model_id)
        current_version = model.active_version

        ModelRegistry.update_active_version(model_id, rollback_to_version)
        model.governance_status = GovernanceStatus.ROLLED_BACK

        record = ScoringGovernanceAuditRecord(
            audit_id=f"gov_rollback_{int(datetime.now(timezone.utc).timestamp())}",
            model_id=model_id,
            version=rollback_to_version,
            previous_version=current_version,
            action="ROLLBACK",
            performed_by=user_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale=rationale,
            details={"rolled_back_from": current_version, "restored": rollback_to_version},
        )
        cls._audit_log.append(record)
        return record

    @classmethod
    def get_audit_trail(cls, model_id: Optional[str] = None) -> List[ScoringGovernanceAuditRecord]:
        if model_id:
            return [r for r in cls._audit_log if r.model_id == model_id]
        return list(cls._audit_log)

