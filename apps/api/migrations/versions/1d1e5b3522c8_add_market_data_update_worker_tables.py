"""Add market data update worker tables

Revision ID: 1d1e5b3522c8
Revises: 363f5a71dd6a
Create Date: 2026-10-08 22:06:33.665394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d1e5b3522c8'
down_revision: Union[str, Sequence[str], None] = '363f5a71dd6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # market_data_update_targets
    op.create_table(
        'market_data_update_targets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('instrument_id', sa.UUID(), nullable=False),
        sa.Column('interval', sa.String(length=32), nullable=False),
        sa.Column('adjustment', sa.String(length=32), nullable=False, server_default='RAW'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('initial_start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cadence_seconds', sa.Integer(), nullable=False),
        sa.Column('revision_lookback_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_successful_coverage_end_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('provider_override', sa.String(length=64), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_code', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_update_targets_instrument_id'), 'market_data_update_targets', ['instrument_id'], unique=False)
    op.create_index('ix_market_data_update_targets_due', 'market_data_update_targets', ['enabled', 'next_run_at'], unique=False)

    # market_data_update_jobs
    op.create_table(
        'market_data_update_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('target_id', sa.UUID(), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
        sa.Column('range_start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('range_end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('provider_override', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('available_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('lease_owner', sa.String(length=255), nullable=True),
        sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('final_ingestion_run_id', sa.UUID(), nullable=True),
        sa.Column('final_error_code', sa.String(length=255), nullable=True),
        sa.Column('final_error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['target_id'], ['market_data_update_targets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_update_jobs_target_id'), 'market_data_update_jobs', ['target_id'], unique=False)
    op.create_index('ix_market_data_update_jobs_claim', 'market_data_update_jobs', ['status', 'available_at', 'scheduled_for'], unique=False)
    op.create_index('uq_active_job_per_target', 'market_data_update_jobs', ['target_id'], unique=True, postgresql_where=sa.text("status IN ('queued', 'running', 'retry_wait')"))
    op.create_index('uq_job_target_scheduled', 'market_data_update_jobs', ['target_id', 'scheduled_for'], unique=True)

    # market_data_update_job_attempts
    op.create_table(
        'market_data_update_job_attempts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('worker_id', sa.String(length=255), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('ingestion_run_id', sa.UUID(), nullable=True),
        sa.Column('error_code', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ingestion_run_id'], ['historical_market_data_ingestion_runs.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['market_data_update_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_update_job_attempts_job_id'), 'market_data_update_job_attempts', ['job_id'], unique=False)
    op.create_index('uq_attempt_job_number', 'market_data_update_job_attempts', ['job_id', 'attempt_number'], unique=True)


def downgrade() -> None:
    op.drop_table('market_data_update_job_attempts')
    op.drop_table('market_data_update_jobs')
    op.drop_table('market_data_update_targets')
