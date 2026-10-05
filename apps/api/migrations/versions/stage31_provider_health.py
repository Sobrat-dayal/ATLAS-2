"""Stage 31 Provider Health

Revision ID: stage31_provider_health
Revises: stage30_provider_configurations
Create Date: 2026-10-05 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'stage31_provider_health'
down_revision = 'stage30_provider_configurations'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # provider_health_states
    op.create_table(
        'provider_health_states',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('provider_key', sa.String(length=128), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=False),
        sa.Column('configuration_id', sa.UUID(), nullable=True),
        sa.Column('owner_principal_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('coverage', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('components', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('consecutive_successes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('probe_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['configuration_id'], ['provider_configurations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "(target_type = 'integration' AND configuration_id IS NULL AND owner_principal_id IS NULL) OR "
            "(target_type = 'configuration' AND configuration_id IS NOT NULL AND owner_principal_id IS NOT NULL)",
            name="ck_provider_health_target_type_constraints"
        )
    )

    op.create_index('ix_provider_health_states_integration', 'provider_health_states', ['provider_key', 'target_type'], unique=True, postgresql_where=sa.text("target_type = 'integration'"))
    op.create_index('ix_provider_health_states_configuration', 'provider_health_states', ['configuration_id'], unique=True, postgresql_where=sa.text("target_type = 'configuration'"))

    # provider_health_checks
    op.create_table(
        'provider_health_checks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('provider_key', sa.String(length=128), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=False),
        sa.Column('configuration_id', sa.UUID(), nullable=True),
        sa.Column('owner_principal_id', sa.UUID(), nullable=True),
        sa.Column('trigger', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('coverage', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('components', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('probe_version', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('error_code', sa.String(length=128), nullable=True),
        sa.Column('message', sa.String(length=1024), nullable=True),
        sa.Column('request_id', sa.String(length=128), nullable=True),
        sa.Column('correlation_id', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['configuration_id'], ['provider_configurations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_provider_health_checks_provider', 'provider_health_checks', ['provider_key', 'started_at'])
    op.create_index('ix_provider_health_checks_configuration', 'provider_health_checks', ['configuration_id', 'started_at'])
    op.create_index('ix_provider_health_checks_owner', 'provider_health_checks', ['owner_principal_id', 'started_at'])


def downgrade() -> None:
    op.drop_index('ix_provider_health_checks_owner', table_name='provider_health_checks')
    op.drop_index('ix_provider_health_checks_configuration', table_name='provider_health_checks')
    op.drop_index('ix_provider_health_checks_provider', table_name='provider_health_checks')
    op.drop_table('provider_health_checks')
    
    op.drop_index('ix_provider_health_states_configuration', table_name='provider_health_states', postgresql_where=sa.text("target_type = 'configuration'"))
    op.drop_index('ix_provider_health_states_integration', table_name='provider_health_states', postgresql_where=sa.text("target_type = 'integration'"))
    op.drop_table('provider_health_states')
