"""stage23_relationship_graph

Revision ID: stage23_relationship_graph
Revises: stage22_entity_aliases
Create Date: 2026-10-04 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'stage23_relationship_graph'
down_revision: Union[str, None] = 'stage22_entity_aliases'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create relationship_types table
    op.create_table(
        'relationship_types',
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=128), nullable=False),
        sa.Column('inverse_key', sa.String(length=128), nullable=True),
        sa.Column('canonical_key', sa.String(length=128), nullable=False),
        sa.Column('is_symmetric', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('source_policy_key', sa.String(length=128), nullable=False),
        sa.Column('target_policy_key', sa.String(length=128), nullable=False),
        sa.Column('allows_self', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('key')
    )

    # 2. Seed system relationship types
    # (Since these are statically defined in code, we insert them into the DB for consistency and FKs)
    system_types = [
        ("issued", "Issued", "Company issued Security", "corporate", "issued_by", "issued", False, "company", "security", False, True),
        ("issued_by", "Issued By", "Security issued by Company", "corporate", "issued", "issued", False, "security", "company", False, True),
        ("listed_on", "Listed On", "Security listed on Exchange", "market", "lists", "listed_on", False, "security", "exchange", False, True),
        ("lists", "Lists", "Exchange lists Security", "market", "listed_on", "listed_on", False, "exchange", "security", False, True),
        ("parent_of", "Parent Of", "Company is parent of Company", "ownership", "subsidiary_of", "parent_of", False, "company", "company", False, True),
        ("subsidiary_of", "Subsidiary Of", "Company is subsidiary of Company", "ownership", "parent_of", "parent_of", False, "company", "company", False, True),
        ("competitor_of", "Competitor Of", "Company is competitor of Company", "competition", "competitor_of", "competitor_of", True, "company", "company", False, True),
        ("supplies", "Supplies", "Company supplies Company", "supply_chain", "supplied_by", "supplies", False, "company", "company", False, True),
        ("supplied_by", "Supplied By", "Company supplied by Company", "supply_chain", "supplies", "supplies", False, "company", "company", False, True),
        ("owns", "Owns", "Company owns Facility", "ownership", "owned_by", "owns", False, "company", "facility", False, True),
        ("owned_by", "Owned By", "Facility owned by Company", "ownership", "owns", "owns", False, "facility", "company", False, True),
        ("operates", "Operates", "Company operates Facility or Exchange", "operations", "operated_by", "operates", False, "company", "facility_or_exchange", False, True),
        ("operated_by", "Operated By", "Facility or Exchange operated by Company", "operations", "operates", "operates", False, "facility_or_exchange", "company", False, True),
        ("authored", "Authored", "Person authored Research Document", "research", "authored_by", "authored", False, "person", "research_document", False, True),
        ("authored_by", "Authored By", "Research Document authored by Person", "research", "authored", "authored", False, "research_document", "person", False, True),
    ]
    
    op.bulk_insert(
        sa.table('relationship_types',
            sa.column('key', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.Text),
            sa.column('category', sa.String),
            sa.column('inverse_key', sa.String),
            sa.column('canonical_key', sa.String),
            sa.column('is_symmetric', sa.Boolean),
            sa.column('source_policy_key', sa.String),
            sa.column('target_policy_key', sa.String),
            sa.column('allows_self', sa.Boolean),
            sa.column('is_system', sa.Boolean),
        ),
        [
            {
                "key": key, "name": name, "description": desc, "category": cat,
                "inverse_key": inv, "canonical_key": can, "is_symmetric": sym,
                "source_policy_key": spk, "target_policy_key": tpk,
                "allows_self": self, "is_system": sys
            }
            for (key, name, desc, cat, inv, can, sym, spk, tpk, self, sys) in system_types
        ]
    )

    # 3. Create entity_relationships table
    op.create_table(
        'entity_relationships',
        sa.Column('relationship_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type_key', sa.String(length=128), nullable=False),
        sa.Column('source_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['relationship_type_key'], ['relationship_types.key'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['source_entity_id'], ['entities.entity_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_entity_id'], ['entities.entity_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('relationship_id')
    )
    
    op.create_index(op.f('ix_entity_relationships_source_entity_id'), 'entity_relationships', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_entity_relationships_target_entity_id'), 'entity_relationships', ['target_entity_id'], unique=False)
    
    op.execute(
        "CREATE UNIQUE INDEX uq_entity_relationships_current ON entity_relationships (relationship_type_key, source_entity_id, target_entity_id) WHERE is_current = true"
    )

def downgrade() -> None:
    op.drop_index('uq_entity_relationships_current', table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_target_entity_id'), table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_source_entity_id'), table_name='entity_relationships')
    op.drop_table('entity_relationships')
    op.drop_table('relationship_types')
