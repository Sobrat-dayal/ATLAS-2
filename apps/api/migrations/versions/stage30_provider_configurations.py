"""stage30_provider_configurations

Revision ID: stage30_provider_configurations
Revises: stage24_provenance
Create Date: 2026-10-05 13:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'stage30_provider_configurations'
down_revision: Union[str, Sequence[str], None] = 'stage24_provenance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # provider_configurations
    op.create_table(
        'provider_configurations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('provider_id', sa.String(length=128), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'provider_id', name='uq_provider_config_user_provider')
    )
    op.create_index(op.f('ix_provider_configurations_user_id'), 'provider_configurations', ['user_id'], unique=False)

    # provider_credential_bindings
    op.create_table(
        'provider_credential_bindings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('configuration_id', sa.UUID(), nullable=False),
        sa.Column('credential_key', sa.String(length=128), nullable=False),
        sa.Column('vault_secret_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['configuration_id'], ['provider_configurations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('configuration_id', 'credential_key', name='uq_provider_credential_config_key'),
        sa.UniqueConstraint('vault_secret_id', name='uq_provider_credential_bindings_vault_secret_id')
    )
    op.create_index(op.f('ix_provider_credential_bindings_configuration_id'), 'provider_credential_bindings', ['configuration_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_provider_credential_bindings_configuration_id'), table_name='provider_credential_bindings')
    op.drop_table('provider_credential_bindings')
    op.drop_index(op.f('ix_provider_configurations_user_id'), table_name='provider_configurations')
    op.drop_table('provider_configurations')
