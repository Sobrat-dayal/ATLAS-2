"""Stage 20 Economic Document Entities

Revision ID: stage20_economic_document_entities
Revises: stage19_geography
Create Date: 2026-10-04 21:08:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'stage20_economic_document_entities'
down_revision: Union[str, None] = 'stage19_geography'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Economic Series
    op.create_table('economic_series',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('series_kind', sa.String(length=128), nullable=True),
        sa.Column('frequency', sa.String(length=128), nullable=True),
        sa.Column('unit_label', sa.String(length=128), nullable=True),
        sa.Column('value_representation', sa.String(length=128), nullable=True),
        sa.Column('seasonal_adjustment', sa.String(length=128), nullable=True),
        sa.Column('scope_geographic_entity_id', sa.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['scope_geographic_entity_id'], ['geographic_entities.entity_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('entity_id'),
        sa.CheckConstraint("series_kind IN ('output', 'prices', 'labor', 'interest_rate', 'monetary', 'fiscal', 'trade', 'housing', 'consumption', 'business', 'demographic', 'financial_conditions', 'sentiment', 'other')", name='ck_econ_series_kind'),
        sa.CheckConstraint("frequency IN ('intraday', 'daily', 'weekly', 'monthly', 'quarterly', 'semiannual', 'annual', 'irregular', 'other')", name='ck_econ_frequency'),
        sa.CheckConstraint("value_representation IN ('level', 'percent', 'rate', 'index', 'currency', 'count', 'ratio', 'change', 'growth_rate', 'other')", name='ck_econ_val_rep'),
        sa.CheckConstraint("seasonal_adjustment IN ('not_adjusted', 'seasonally_adjusted', 'seasonally_adjusted_annual_rate', 'other')", name='ck_econ_seas_adj')
    )
    op.create_index(op.f('ix_economic_series_scope_geographic_entity_id'), 'economic_series', ['scope_geographic_entity_id'], unique=False)

    # 2. Create Research Documents
    op.create_table('research_documents',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('document_kind', sa.String(length=128), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('language_code', sa.String(length=35), nullable=True),
        sa.Column('abstract_text', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id'),
        sa.CheckConstraint("document_kind IN ('journal_article', 'conference_paper', 'preprint', 'working_paper', 'research_report', 'technical_report', 'white_paper', 'thesis', 'dissertation', 'book_chapter', 'dataset_documentation', 'other')", name='ck_research_doc_kind')
    )
    op.create_index(op.f('ix_research_documents_document_kind'), 'research_documents', ['document_kind'], unique=False)
    op.create_index(op.f('ix_research_documents_publication_date'), 'research_documents', ['publication_date'], unique=False)

    # 3. Create News Events
    op.create_table('news_events',
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('event_kind', sa.String(length=128), nullable=True),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_status', sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(['entity_id'], ['entities.entity_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('entity_id'),
        sa.CheckConstraint("event_kind IN ('corporate', 'economic', 'market', 'political', 'geopolitical', 'regulatory', 'legal', 'technology', 'cybersecurity', 'infrastructure', 'natural_disaster', 'security_incident', 'other')", name='ck_news_event_kind'),
        sa.CheckConstraint("event_status IN ('developing', 'confirmed', 'resolved', 'historical', 'other')", name='ck_news_event_status')
    )
    op.create_index(op.f('ix_news_events_event_kind'), 'news_events', ['event_kind'], unique=False)
    op.create_index(op.f('ix_news_events_event_status'), 'news_events', ['event_status'], unique=False)
    op.create_index(op.f('ix_news_events_event_time'), 'news_events', ['event_time'], unique=False)

    # 4. Backfill existing generic entities
    op.execute("""
    INSERT INTO economic_series (entity_id)
    SELECT entity_id FROM entities 
    WHERE entity_type = 'economic_series';
    """)

    op.execute("""
    INSERT INTO research_documents (entity_id)
    SELECT entity_id FROM entities 
    WHERE entity_type = 'research_document';
    """)

    op.execute("""
    INSERT INTO news_events (entity_id)
    SELECT entity_id FROM entities 
    WHERE entity_type = 'news_event';
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_news_events_event_time'), table_name='news_events')
    op.drop_index(op.f('ix_news_events_event_status'), table_name='news_events')
    op.drop_index(op.f('ix_news_events_event_kind'), table_name='news_events')
    op.drop_table('news_events')
    
    op.drop_index(op.f('ix_research_documents_publication_date'), table_name='research_documents')
    op.drop_index(op.f('ix_research_documents_document_kind'), table_name='research_documents')
    op.drop_table('research_documents')
    
    op.drop_index(op.f('ix_economic_series_scope_geographic_entity_id'), table_name='economic_series')
    op.drop_table('economic_series')
