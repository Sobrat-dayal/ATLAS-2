"""Base interface for AI financial action adapters (Stage 128, Part XIII)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from atlas.ai.actions.domain import (
    AiActionClassification,
    AiActionDiff,
    AiActionType,
    AiFinancialAction,
    AiFinancialActionPreview,
    ApprovalPolicy,
    ReversibilityPolicy,
)


class ActionAdapter(ABC):
    """Abstract base class for all domain-specific action adapters."""

    @property
    @abstractmethod
    def action_type(self) -> AiActionType:
        """The canonical action type handled by this adapter."""
        ...

    @property
    @abstractmethod
    def target_module(self) -> str:
        """The target module name (charts, screeners, portfolios, risk)."""
        ...

    @property
    @abstractmethod
    def classification(self) -> AiActionClassification:
        """Action classification."""
        ...

    @property
    @abstractmethod
    def default_approval_policy(self) -> ApprovalPolicy:
        """Default approval requirement."""
        ...

    @property
    @abstractmethod
    def reversibility_policy(self) -> ReversibilityPolicy:
        """Whether this action is reversible."""
        ...

    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Returns JSON schema for proposed arguments."""
        ...

    @abstractmethod
    def validate_parameters(self, proposed_args: Dict[str, Any]) -> Dict[str, Any]:
        """Strictly validates proposed arguments or raises AiActionError."""
        ...

    @abstractmethod
    async def get_current_state(
        self,
        resource_id: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str]:
        """Retrieves current state dict and current revision string."""
        ...

    @abstractmethod
    async def generate_preview(
        self,
        action_id: str,
        resource_id: str,
        current_state: Dict[str, Any],
        current_revision: str,
        proposed_args: Dict[str, Any],
        actor_user_id: str,
        tenant_id: str,
    ) -> AiFinancialActionPreview:
        """Computes before/after diffs, financial assumptions, and returns a preview."""
        ...

    @abstractmethod
    async def execute(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[Dict[str, Any], str, List[AiActionDiff]]:
        """Executes the action on real financial services.

        Returns:
            Tuple of (result_data, new_revision, applied_diffs)
        """
        ...

    async def undo(
        self,
        action: AiFinancialAction,
        receipt: Any,
        actor_user_id: str,
        tenant_id: str,
    ) -> str:
        """Reverts the action if reversible, returning the restored revision.

        Default raises NotImplementedError.
        """
        raise NotImplementedError(f"Undo not supported for action type {self.action_type.value}")
