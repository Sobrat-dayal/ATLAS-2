"""SQLAlchemy ORM models for AI financial actions (Stage 128, Part LXXIII)."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AiFinancialActionPlanModel(Base):
    """Database model for an AI action plan."""

    __tablename__ = "ai_financial_action_plans"

    plan_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    conversation_id = Column(String(64), nullable=True)
    user_intent = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="REQUESTED")
    dependency_graph = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class AiFinancialActionModel(Base):
    """Database model for a single planned action."""

    __tablename__ = "ai_financial_actions"

    action_id = Column(String(64), primary_key=True)
    plan_id = Column(
        String(64), ForeignKey("ai_financial_action_plans.plan_id"), nullable=False, index=True
    )
    action_type = Column(String(64), nullable=False, index=True)
    action_version = Column(String(16), nullable=False, default="1.0.0")
    target_module = Column(String(32), nullable=False)
    target_resource_type = Column(String(64), nullable=False)
    target_resource_id = Column(String(64), nullable=False, index=True)
    actor_user_id = Column(String(64), nullable=False)
    tenant_scope = Column(String(64), nullable=False)
    proposed_arguments = Column(JSON, nullable=False, default=dict)
    normalized_arguments_hash = Column(String(64), nullable=False)
    expected_resource_revision = Column(String(64), nullable=False)
    classification = Column(String(32), nullable=False)
    approval_policy = Column(String(32), nullable=False)
    reversibility_policy = Column(String(32), nullable=False)
    action_status = Column(String(32), nullable=False, default="REQUESTED")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class AiFinancialActionPreviewModel(Base):
    """Database model for a generated action preview."""

    __tablename__ = "ai_financial_action_previews"

    preview_id = Column(String(64), primary_key=True)
    action_id = Column(
        String(64), ForeignKey("ai_financial_actions.action_id"), nullable=False, index=True
    )
    target_resource_type = Column(String(64), nullable=False)
    target_resource_id = Column(String(64), nullable=False)
    current_state = Column(JSON, nullable=False, default=dict)
    proposed_state = Column(JSON, nullable=False, default=dict)
    diffs = Column(JSON, nullable=False, default=list)
    financial_assumptions = Column(JSON, nullable=False, default=list)
    estimated_cost = Column(String(16), nullable=False, default="LOW")
    preview_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class AiActionExecutionReceiptModel(Base):
    """Database model for an immutable execution receipt."""

    __tablename__ = "ai_financial_action_receipts"

    receipt_id = Column(String(64), primary_key=True)
    action_id = Column(String(64), nullable=False, index=True)
    plan_id = Column(String(64), nullable=False, index=True)
    tool_call_id = Column(String(64), nullable=True)
    actor_user_id = Column(String(64), nullable=False, index=True)
    target_resource_id = Column(String(64), nullable=False)
    target_revision_before = Column(String(64), nullable=False)
    target_revision_after = Column(String(64), nullable=False)
    operation_status = Column(String(32), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    result_reference = Column(JSON, nullable=False, default=dict)
    diffs = Column(JSON, nullable=False, default=list)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    undo_reference = Column(String(64), nullable=True)


class AiPortfolioScenarioDraftModel(Base):
    """Database model for a saved hypothetical portfolio scenario draft."""

    __tablename__ = "ai_portfolio_scenario_drafts"

    scenario_id = Column(String(64), primary_key=True)
    portfolio_id = Column(String(64), nullable=False, index=True)
    portfolio_snapshot_id = Column(String(64), nullable=False)
    scenario_type = Column(String(32), nullable=False)
    baseline_allocation = Column(JSON, nullable=False)
    proposed_allocation = Column(JSON, nullable=False)
    allocation_deltas = Column(JSON, nullable=False)
    notional_deltas = Column(JSON, nullable=False)
    assumptions = Column(JSON, nullable=False)
    valuation_as_of = Column(String(32), nullable=False)
    reporting_currency = Column(String(8), nullable=False, default="USD")
    is_hypothetical = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
