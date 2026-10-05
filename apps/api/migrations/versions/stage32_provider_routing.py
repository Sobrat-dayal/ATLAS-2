"""Stage 32 Provider Routing Models

Revision ID: stage32_provider_routing
Revises: stage31_provider_health
Create Date: 2026-10-05 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'stage32_provider_routing'
down_revision = 'stage31_provider_health'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum for ProviderRoutingScope
    provider_routing_scope = postgresql.ENUM('USER', 'SYSTEM', name='provider_routing_scope')
    provider_routing_scope.create(op.get_bind())

    # Create provider_routing_policies table
    op.create_table(
        'provider_routing_policies',
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scope', postgresql.ENUM('USER', 'SYSTEM', name='provider_routing_scope', create_type=False), nullable=False),
        sa.Column('owner_principal_id', sa.String(), nullable=True),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('fallback_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('schema_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('policy_id'),
        sa.UniqueConstraint('owner_principal_id', 'domain', name='uq_provider_routing_user_domain'),
        sa.UniqueConstraint('scope', 'domain', name='uq_provider_routing_system_domain')
    )

    # Create provider_routing_candidates table
    op.create_table(
        'provider_routing_candidates',
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_key', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['policy_id'], ['provider_routing_policies.policy_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('candidate_id'),
        sa.UniqueConstraint('policy_id', 'provider_key', name='uq_provider_routing_candidate_provider'),
        sa.UniqueConstraint('policy_id', 'position', name='uq_provider_routing_candidate_position')
    )

def downgrade() -> None:
    op.drop_table('provider_routing_candidates')
    op.drop_table('provider_routing_policies')
    
    # Drop enum
    provider_routing_scope = postgresql.ENUM('USER', 'SYSTEM', name='provider_routing_scope')
    provider_routing_scope.drop(op.get_bind())
