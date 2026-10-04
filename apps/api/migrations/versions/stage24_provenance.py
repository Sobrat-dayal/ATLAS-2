"""stage24_provenance

Revision ID: stage24_provenance
Revises: stage23_relationship_graph
Create Date: 2023-11-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'stage24_provenance'
down_revision: Union[str, None] = 'stage23_relationship_graph'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create provenance_sources table
    op.create_table(
        'provenance_sources',
        sa.Column('source_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('source_key', sa.String(length=128), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('source_kind', sa.String(length=64), nullable=False),
        sa.Column('base_url', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('source_id'),
        sa.UniqueConstraint('source_key')
    )
    op.create_check_constraint('chk_provenance_source_name_empty', 'provenance_sources', "length(name) > 0")
    op.create_check_constraint('chk_provenance_source_key_format', 'provenance_sources', "source_key IS NULL OR source_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'")

    # 2. Create provenance_records table
    op.create_table(
        'provenance_records',
        sa.Column('provenance_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('record_kind', sa.String(length=64), nullable=False),
        sa.Column('source_reference', sa.String(length=512), nullable=True),
        sa.Column('source_uri', sa.String(length=2048), nullable=True),
        sa.Column('source_locator', sa.String(length=512), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('license_name', sa.Text(), nullable=True),
        sa.Column('license_url', sa.String(length=2048), nullable=True),
        sa.Column('attribution_text', sa.String(length=2048), nullable=True),
        sa.Column('content_hash_sha256', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['provenance_sources.source_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('provenance_id')
    )
    op.create_index(op.f('ix_provenance_records_retrieved_at'), 'provenance_records', ['retrieved_at'], unique=False)
    op.create_index(op.f('ix_provenance_records_source_id'), 'provenance_records', ['source_id'], unique=False)
    op.create_check_constraint('chk_provenance_record_hash_format', 'provenance_records', "content_hash_sha256 IS NULL OR content_hash_sha256 ~ '^[0-9a-f]{64}$'")

    # 3. Create entity_provenance_links
    op.create_table(
        'entity_provenance_links',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('provenance_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('evidence_role', sa.String(length=64), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provenance_id'], ['provenance_records.provenance_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id', 'provenance_id')
    )
    op.create_index(op.f('ix_entity_provenance_links_provenance_id'), 'entity_provenance_links', ['provenance_id'], unique=False)
    op.create_check_constraint('chk_entity_prov_confidence', 'entity_provenance_links', "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)")

    # 4. Create identifier_provenance_links
    op.create_table(
        'identifier_provenance_links',
        sa.Column('identifier_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('provenance_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('evidence_role', sa.String(length=64), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['identifier_id'], ['entity_identifiers.identifier_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provenance_id'], ['provenance_records.provenance_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('identifier_id', 'provenance_id')
    )
    op.create_index(op.f('ix_identifier_provenance_links_provenance_id'), 'identifier_provenance_links', ['provenance_id'], unique=False)
    op.create_check_constraint('chk_identifier_prov_confidence', 'identifier_provenance_links', "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)")

    # 5. Create alias_provenance_links
    op.create_table(
        'alias_provenance_links',
        sa.Column('alias_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('provenance_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('evidence_role', sa.String(length=64), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['alias_id'], ['entity_aliases.alias_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provenance_id'], ['provenance_records.provenance_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('alias_id', 'provenance_id')
    )
    op.create_index(op.f('ix_alias_provenance_links_provenance_id'), 'alias_provenance_links', ['provenance_id'], unique=False)
    op.create_check_constraint('chk_alias_prov_confidence', 'alias_provenance_links', "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)")

    # 6. Create relationship_provenance_links
    op.create_table(
        'relationship_provenance_links',
        sa.Column('relationship_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('provenance_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('evidence_role', sa.String(length=64), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['provenance_id'], ['provenance_records.provenance_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['relationship_id'], ['entity_relationships.relationship_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('relationship_id', 'provenance_id')
    )
    op.create_index(op.f('ix_relationship_provenance_links_provenance_id'), 'relationship_provenance_links', ['provenance_id'], unique=False)
    op.create_check_constraint('chk_relationship_prov_confidence', 'relationship_provenance_links', "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)")


def downgrade() -> None:
    op.drop_table('relationship_provenance_links')
    op.drop_table('alias_provenance_links')
    op.drop_table('identifier_provenance_links')
    op.drop_table('entity_provenance_links')
    op.drop_table('provenance_records')
    op.drop_table('provenance_sources')
