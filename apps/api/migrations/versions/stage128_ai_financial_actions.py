"""stage128_ai_financial_actions

Revision ID: stage128_ai_financial_actions
Revises: stage127_ai_research_rag
Create Date: 2026-10-30 00:00:00.000000

Stage 128 — AI Financial Action Engine:
- ai_financial_action_plans: Multi-step action coordination plans with dependency graphs.
- ai_financial_actions: Individual planned actions across Charts, Screeners, Portfolios, and Risk.
- ai_financial_action_previews: Cryptographic previews with before/after diffs and preview hashes.
- ai_financial_action_receipts: Immutable execution receipts with verification stamps.
- ai_portfolio_scenario_drafts: Non-executing hypothetical scenario drafts.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage128_ai_financial_actions"
down_revision: Union[str, Sequence[str], None] = "stage127_ai_research_rag"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Action Plans table
    op.create_table(
        "ai_financial_action_plans",
        sa.Column("plan_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("user_intent", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="REQUESTED"),
        sa.Column("dependency_graph", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ai_financial_action_plans_owner", "ai_financial_action_plans", ["owner_user_id"])
    op.create_index("ix_ai_financial_action_plans_tenant", "ai_financial_action_plans", ["tenant_id"])

    # 2. Financial Actions table
    op.create_table(
        "ai_financial_actions",
        sa.Column("action_id", sa.String(length=64), primary_key=True),
        sa.Column("plan_id", sa.String(length=64), sa.ForeignKey("ai_financial_action_plans.plan_id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", sa.String(length=64), nullable=False),
        sa.Column("action_version", sa.String(length=16), nullable=False, server_default="1.0.0"),
        sa.Column("target_module", sa.String(length=32), nullable=False),
        sa.Column("target_resource_type", sa.String(length=64), nullable=False),
        sa.Column("target_resource_id", sa.String(length=64), nullable=False),
        sa.Column("actor_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_scope", sa.String(length=64), nullable=False),
        sa.Column("proposed_arguments", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("normalized_arguments_hash", sa.String(length=64), nullable=False),
        sa.Column("expected_resource_revision", sa.String(length=64), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("approval_policy", sa.String(length=32), nullable=False),
        sa.Column("reversibility_policy", sa.String(length=32), nullable=False),
        sa.Column("action_status", sa.String(length=32), nullable=False, server_default="REQUESTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_financial_actions_plan_id", "ai_financial_actions", ["plan_id"])
    op.create_index("ix_ai_financial_actions_target", "ai_financial_actions", ["target_resource_id"])

    # 3. Action Previews table
    op.create_table(
        "ai_financial_action_previews",
        sa.Column("preview_id", sa.String(length=64), primary_key=True),
        sa.Column("action_id", sa.String(length=64), sa.ForeignKey("ai_financial_actions.action_id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_resource_type", sa.String(length=64), nullable=False),
        sa.Column("target_resource_id", sa.String(length=64), nullable=False),
        sa.Column("current_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("proposed_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("diffs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("financial_assumptions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("estimated_cost", sa.String(length=16), nullable=False, server_default="LOW"),
        sa.Column("preview_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_financial_action_previews_action", "ai_financial_action_previews", ["action_id"])

    # 4. Action Receipts table
    op.create_table(
        "ai_financial_action_receipts",
        sa.Column("receipt_id", sa.String(length=64), primary_key=True),
        sa.Column("action_id", sa.String(length=64), nullable=False),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("tool_call_id", sa.String(length=64), nullable=True),
        sa.Column("actor_user_id", sa.String(length=64), nullable=False),
        sa.Column("target_resource_id", sa.String(length=64), nullable=False),
        sa.Column("target_revision_before", sa.String(length=64), nullable=False),
        sa.Column("target_revision_after", sa.String(length=64), nullable=False),
        sa.Column("operation_status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result_reference", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("diffs", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("undo_reference", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_ai_financial_action_receipts_user", "ai_financial_action_receipts", ["actor_user_id"])
    op.create_index("ix_ai_financial_action_receipts_action", "ai_financial_action_receipts", ["action_id"])
    op.create_index("ix_ai_financial_action_receipts_plan", "ai_financial_action_receipts", ["plan_id"])

    # 5. Portfolio Scenario Drafts table
    op.create_table(
        "ai_portfolio_scenario_drafts",
        sa.Column("scenario_id", sa.String(length=64), primary_key=True),
        sa.Column("portfolio_id", sa.String(length=64), nullable=False),
        sa.Column("portfolio_snapshot_id", sa.String(length=64), nullable=False),
        sa.Column("scenario_type", sa.String(length=32), nullable=False),
        sa.Column("baseline_allocation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("proposed_allocation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("allocation_deltas", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notional_deltas", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("assumptions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("valuation_as_of", sa.String(length=32), nullable=False),
        sa.Column("reporting_currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("is_hypothetical", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_portfolio_scenario_drafts_port", "ai_portfolio_scenario_drafts", ["portfolio_id"])


def downgrade() -> None:
    op.drop_table("ai_portfolio_scenario_drafts")
    op.drop_table("ai_financial_action_receipts")
    op.drop_table("ai_financial_action_previews")
    op.drop_table("ai_financial_actions")
    op.drop_table("ai_financial_action_plans")

