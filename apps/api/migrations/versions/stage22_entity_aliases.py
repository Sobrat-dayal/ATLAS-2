"""stage22_entity_aliases

Revision ID: stage22_entity_aliases
Revises: a5e6709640e1
Create Date: 2026-10-04 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
import re
import unicodedata

# revision identifiers, used by Alembic.
revision: str = 'stage22_entity_aliases'
down_revision: Union[str, None] = 'a5e6709640e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def normalize_entity_name(name: str) -> str:
    if not name:
        return ""
    normalized = unicodedata.normalize("NFKC", name)
    normalized = normalized.casefold()
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def upgrade() -> None:
    # 1. Add canonical_name_normalized and display_name_normalized to entities table
    op.add_column('entities', sa.Column('canonical_name_normalized', sa.String(length=512), nullable=True))
    op.add_column('entities', sa.Column('display_name_normalized', sa.String(length=512), nullable=True))

    # Fetch all entities to backfill
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT entity_id, canonical_name, display_name FROM entities"))
    
    for row in res.fetchall():
        entity_id = row[0]
        canonical_name = row[1]
        display_name = row[2]
        
        cn_norm = normalize_entity_name(canonical_name)
        dn_norm = normalize_entity_name(display_name)
        
        conn.execute(
            sa.text("UPDATE entities SET canonical_name_normalized = :cn, display_name_normalized = :dn WHERE entity_id = :id"),
            {"cn": cn_norm, "dn": dn_norm, "id": entity_id}
        )

    op.alter_column('entities', 'canonical_name_normalized', nullable=False)
    op.alter_column('entities', 'display_name_normalized', nullable=False)
    
    op.create_index(op.f('ix_entities_canonical_name_normalized'), 'entities', ['canonical_name_normalized'], unique=False)
    op.create_index(op.f('ix_entities_display_name_normalized'), 'entities', ['display_name_normalized'], unique=False)

    # 2. Create alias_types table
    op.create_table('alias_types',
    sa.Column('key', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=128), nullable=False),
    sa.Column('normalization_strategy', sa.String(length=128), nullable=False),
    sa.Column('is_system', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )

    # 3. Create entity_aliases table
    op.create_table('entity_aliases',
    sa.Column('alias_id', sa.UUID(), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('alias_type_key', sa.String(length=128), nullable=False),
    sa.Column('value', sa.String(length=512), nullable=False),
    sa.Column('normalized_value', sa.String(length=512), nullable=False),
    sa.Column('language_code', sa.String(length=35), nullable=True),
    sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_to', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['alias_type_key'], ['alias_types.key'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('alias_id'),
    sa.CheckConstraint('valid_to >= valid_from', name='chk_valid_to_after_from')
    )
    op.create_index(op.f('ix_entity_aliases_entity_id'), 'entity_aliases', ['entity_id'], unique=False)
    op.create_index(op.f('ix_entity_aliases_normalized_value'), 'entity_aliases', ['normalized_value'], unique=False)
    
    # partial unique index for current aliases
    op.execute(
        "CREATE UNIQUE INDEX uq_entity_aliases_current ON entity_aliases "
        "(entity_id, alias_type_key, normalized_value, COALESCE(language_code, '')) "
        "WHERE is_current = TRUE"
    )

    # Insert default alias types
    op.execute("""
        INSERT INTO alias_types (key, name, category, normalization_strategy, description, is_system) VALUES
        ('common_name', 'Common Name', 'name', 'standard', 'The primary common name of the entity', true),
        ('short_name', 'Short Name', 'name', 'standard', 'A shortened name or common acronym', true),
        ('acronym', 'Acronym', 'abbreviation', 'standard', 'Common acronym used to refer to the entity', true),
        ('abbreviation', 'Abbreviation', 'abbreviation', 'standard', 'Common abbreviation', true),
        ('brand_name', 'Brand Name', 'brand', 'standard', 'Brand name used by the entity', true),
        ('localized_name', 'Localized Name', 'localized', 'standard', 'Name translated or localized', true),
        ('informal_name', 'Informal Name', 'informal', 'standard', 'Informal or slang name', true),
        ('former_name', 'Former Name', 'historical', 'standard', 'A previously held name', true)
        ON CONFLICT (key) DO NOTHING;
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_entity_aliases_current")
    op.drop_index(op.f('ix_entity_aliases_normalized_value'), table_name='entity_aliases')
    op.drop_index(op.f('ix_entity_aliases_entity_id'), table_name='entity_aliases')
    op.drop_table('entity_aliases')
    op.drop_table('alias_types')
    
    op.drop_index(op.f('ix_entities_display_name_normalized'), table_name='entities')
    op.drop_index(op.f('ix_entities_canonical_name_normalized'), table_name='entities')
    op.drop_column('entities', 'display_name_normalized')
    op.drop_column('entities', 'canonical_name_normalized')
