"""Stage 19 Geographic Entities

Revision ID: stage19_geography
Revises: stage18_companies
Create Date: 2026-10-04 20:57:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'stage19_geography'
down_revision: Union[str, None] = 'stage18_companies'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Geographic Entities
    op.create_table('geographic_entities',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    # 2. Create Countries
    op.create_table('countries',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('country_kind', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['geographic_entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    # 3. Create Facilities
    op.create_table('facilities',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('country_entity_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('region_name', sa.String(length=256), nullable=True),
        sa.Column('locality_name', sa.String(length=256), nullable=True),
        sa.Column('address_text', sa.String(length=2048), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('elevation_meters', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.CheckConstraint('(latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL)', name='ck_facility_coord_pair'),
        sa.CheckConstraint('latitude >= -90 AND latitude <= 90', name='ck_facility_lat_range'),
        sa.CheckConstraint('longitude >= -180 AND longitude <= 180', name='ck_facility_lon_range'),
        sa.ForeignKeyConstraint(['country_entity_id'], ['countries.entity_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['entity_id'], ['geographic_entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )
    op.create_index(op.f('ix_facilities_country_entity_id'), 'facilities', ['country_entity_id'], unique=False)

    # 4. Create Ports
    op.create_table('ports',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('port_kind', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['facilities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    # 5. Create Airports
    op.create_table('airports',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('airport_kind', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['facilities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    # 6. Create Exchanges
    op.create_table('exchanges',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('country_entity_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('exchange_kind', sa.String(length=128), nullable=True),
        sa.Column('timezone_name', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['country_entity_id'], ['countries.entity_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['entity_id'], ['geographic_entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )
    op.create_index(op.f('ix_exchanges_country_entity_id'), 'exchanges', ['country_entity_id'], unique=False)

    # 7. Backfill existing geographic entities
    op.execute("""
    INSERT INTO geographic_entities (entity_id)
    SELECT entity_id FROM entities 
    WHERE entity_type IN ('country', 'facility', 'port', 'airport', 'exchange');
    """)

    op.execute("""
    INSERT INTO countries (entity_id)
    SELECT entity_id FROM entities WHERE entity_type = 'country';
    """)

    op.execute("""
    INSERT INTO facilities (entity_id)
    SELECT entity_id FROM entities WHERE entity_type IN ('facility', 'port', 'airport');
    """)

    op.execute("""
    INSERT INTO ports (entity_id)
    SELECT entity_id FROM entities WHERE entity_type = 'port';
    """)

    op.execute("""
    INSERT INTO airports (entity_id)
    SELECT entity_id FROM entities WHERE entity_type = 'airport';
    """)

    op.execute("""
    INSERT INTO exchanges (entity_id)
    SELECT entity_id FROM entities WHERE entity_type = 'exchange';
    """)

    # 8. Modify Company primary_country_entity_id FK
    op.drop_constraint('companies_primary_country_entity_id_fkey', 'companies', type_='foreignkey')
    op.create_foreign_key(None, 'companies', 'countries', ['primary_country_entity_id'], ['entity_id'], ondelete='SET NULL')


def downgrade() -> None:
    # Reverse company FK
    op.drop_constraint(None, 'companies', type_='foreignkey')
    op.create_foreign_key('companies_primary_country_entity_id_fkey', 'companies', 'entities', ['primary_country_entity_id'], ['entity_id'], ondelete='RESTRICT')

    # Drop tables
    op.drop_index(op.f('ix_exchanges_country_entity_id'), table_name='exchanges')
    op.drop_table('exchanges')
    op.drop_table('airports')
    op.drop_table('ports')
    op.drop_index(op.f('ix_facilities_country_entity_id'), table_name='facilities')
    op.drop_table('facilities')
    op.drop_table('countries')
    op.drop_table('geographic_entities')
