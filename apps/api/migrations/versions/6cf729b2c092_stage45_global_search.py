"""stage45_global_search

Revision ID: 6cf729b2c092
Revises: b2b3c4d5e6f7
Create Date: 2026-10-08 23:12:23.636344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cf729b2c092'
down_revision: Union[str, Sequence[str], None] = 'b2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Enable pg_trgm extension if not already present
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # 2. Add trigram indexes to entities
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_entities_canonical_name_trgm "
        "ON entities USING gin (canonical_name_normalized gin_trgm_ops);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_entities_display_name_trgm "
        "ON entities USING gin (display_name_normalized gin_trgm_ops);"
    )
    
    # 3. Add trigram index to current aliases
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_entity_aliases_value_trgm "
        "ON entity_aliases USING gin (normalized_value gin_trgm_ops) "
        "WHERE is_current = TRUE;"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop trigram indexes
    op.execute("DROP INDEX IF EXISTS ix_entity_aliases_value_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_entities_display_name_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_entities_canonical_name_trgm;")
    
    # NOTE: We DO NOT drop the pg_trgm extension on downgrade because it 
    # might be used by other parts of the system or external databases in the same cluster.
