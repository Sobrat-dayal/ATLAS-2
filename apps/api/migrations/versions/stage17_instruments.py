"""stage17_instruments

Revision ID: stage17_instruments
Revises: b3a479d2b271
Create Date: 2026-10-04 20:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'stage17_instruments'
down_revision: Union[str, None] = 'b3a479d2b271'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'financial_instruments',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'securities',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'currencies',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('currency_kind', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'crypto_assets',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('asset_kind', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'commodities',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('commodity_category', sa.String(length=64), nullable=True),
        sa.Column('unit_of_measure', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'market_indexes',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('index_kind', sa.String(length=64), nullable=True),
        sa.Column('base_currency_entity_id', sa.UUID(), nullable=True),
        sa.Column('weighting_method', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['base_currency_entity_id'], ['currencies.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'equities',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('equity_kind', sa.String(length=64), nullable=True),
        sa.Column('share_class_name', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'etfs',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('base_currency_entity_id', sa.UUID(), nullable=True),
        sa.Column('replication_method', sa.String(length=64), nullable=True),
        sa.Column('distribution_policy', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['base_currency_entity_id'], ['currencies.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'bonds',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('denomination_currency_entity_id', sa.UUID(), nullable=True),
        sa.Column('face_value', sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column('coupon_rate', sa.Numeric(precision=20, scale=10), nullable=True),
        sa.Column('coupon_type', sa.String(length=64), nullable=True),
        sa.Column('coupon_frequency', sa.SmallInteger(), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('maturity_date', sa.Date(), nullable=True),
        sa.CheckConstraint('face_value >= 0', name='bonds_face_value_check'),
        sa.CheckConstraint('coupon_frequency > 0', name='bonds_coupon_frequency_check'),
        sa.CheckConstraint('maturity_date >= issue_date', name='bonds_maturity_date_check'),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['denomination_currency_entity_id'], ['currencies.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

    op.create_table(
        'options',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('underlying_entity_id', sa.UUID(), nullable=False),
        sa.Column('option_right', sa.String(length=16), nullable=False),
        sa.Column('strike_price', sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column('expiration_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('exercise_style', sa.String(length=32), nullable=True),
        sa.Column('contract_multiplier', sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column('settlement_type', sa.String(length=32), nullable=True),
        sa.CheckConstraint('strike_price >= 0', name='options_strike_price_check'),
        sa.CheckConstraint('contract_multiplier > 0', name='options_multiplier_check'),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['underlying_entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )
    op.create_index(op.f('ix_options_underlying_entity_id'), 'options', ['underlying_entity_id'], unique=False)

    op.create_table(
        'futures',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('underlying_entity_id', sa.UUID(), nullable=False),
        sa.Column('expiration_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contract_size', sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column('settlement_type', sa.String(length=32), nullable=True),
        sa.Column('settlement_currency_entity_id', sa.UUID(), nullable=True),
        sa.CheckConstraint('contract_size > 0', name='futures_contract_size_check'),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['underlying_entity_id'], ['financial_instruments.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['settlement_currency_entity_id'], ['currencies.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )
    op.create_index(op.f('ix_futures_underlying_entity_id'), 'futures', ['underlying_entity_id'], unique=False)

    op.create_table(
        'funds',
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('fund_kind', sa.String(length=64), nullable=True),
        sa.Column('base_currency_entity_id', sa.UUID(), nullable=True),
        sa.Column('distribution_policy', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['securities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['base_currency_entity_id'], ['currencies.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id')
    )

def downgrade() -> None:
    op.drop_table('funds')
    op.drop_index(op.f('ix_futures_underlying_entity_id'), table_name='futures')
    op.drop_table('futures')
    op.drop_index(op.f('ix_options_underlying_entity_id'), table_name='options')
    op.drop_table('options')
    op.drop_table('bonds')
    op.drop_table('etfs')
    op.drop_table('equities')
    op.drop_table('market_indexes')
    op.drop_table('commodities')
    op.drop_table('crypto_assets')
    op.drop_table('currencies')
    op.drop_table('securities')
    op.drop_table('financial_instruments')
