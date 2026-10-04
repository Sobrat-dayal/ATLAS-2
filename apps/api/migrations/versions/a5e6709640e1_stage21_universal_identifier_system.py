"""stage21_universal_identifier_system

Revision ID: a5e6709640e1
Revises: stage20_economic_document_entities
Create Date: 2026-10-04 21:33:28.221275

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a5e6709640e1'
down_revision: Union[str, Sequence[str], None] = 'stage20_economic_document_entities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. identifier_schemes
    identifier_schemes = op.create_table(
        "identifier_schemes",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("scope_policy", sa.String(length=64), nullable=False),
        sa.Column("normalization_strategy", sa.String(length=64), nullable=False),
        sa.Column("case_sensitive", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("max_length", sa.Integer(), nullable=False),
        sa.Column("is_system", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("key", name="pk_identifier_schemes"),
    )

    # 2. entity_identifiers
    op.create_table(
        "entity_identifiers",
        sa.Column("identifier_id", sa.UUID(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("scheme_key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.Text(), nullable=False),
        sa.Column("scope_entity_id", sa.UUID(), nullable=True),
        sa.Column("namespace", sa.String(length=128), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["entities.entity_id"], name="fk_entity_identifiers_entity", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["scheme_key"], ["identifier_schemes.key"], name="fk_entity_identifiers_scheme", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["scope_entity_id"], ["entities.entity_id"], name="fk_entity_identifiers_scope", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("identifier_id", name="pk_entity_identifiers"),
        sa.CheckConstraint("length(trim(value)) > 0", name="ck_entity_identifiers_value_not_empty"),
        sa.CheckConstraint(
            "length(trim(normalized_value)) > 0", name="ck_entity_identifiers_normalized_value_not_empty"
        ),
        sa.CheckConstraint(
            "namespace IS NULL OR length(trim(namespace)) > 0", name="ck_entity_identifiers_namespace_not_empty"
        ),
        sa.CheckConstraint(
            "((is_current = TRUE) AND (valid_to IS NULL)) OR ((is_current = FALSE) AND (valid_to IS NOT NULL))",
            name="ck_entity_identifiers_current_history",
        ),
        sa.CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_from <= valid_to",
            name="ck_entity_identifiers_validity_dates",
        ),
    )

    op.create_index(
        "ix_entity_identifiers_entity_id", "entity_identifiers", ["entity_id"], unique=False
    )
    op.create_index(
        "ix_entity_identifiers_scope_entity_id", "entity_identifiers", ["scope_entity_id"], unique=False
    )

    op.execute(
        """
        CREATE UNIQUE INDEX ix_entity_identifiers_current_lookup
        ON entity_identifiers (scheme_key, normalized_value, COALESCE(scope_entity_id, '00000000-0000-0000-0000-000000000000'::uuid), COALESCE(namespace, ''))
        WHERE is_current = TRUE;
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX ix_entity_identifiers_current_assignment
        ON entity_identifiers (entity_id, scheme_key, COALESCE(scope_entity_id, '00000000-0000-0000-0000-000000000000'::uuid), COALESCE(namespace, ''))
        WHERE is_current = TRUE;
        """
    )

    # 3. Seed identifier schemes
    schemes_data = [
        ("ticker", "Market Ticker", "financial", "entity", "uppercase_trim", False, 64),
        ("figi", "FIGI", "financial", "global", "uppercase_trim", False, 12),
        ("composite_figi", "Composite FIGI", "financial", "global", "uppercase_trim", False, 12),
        ("share_class_figi", "Share Class FIGI", "financial", "global", "uppercase_trim", False, 12),
        ("isin", "ISIN", "financial", "global", "compact_uppercase", False, 12),
        ("cusip", "CUSIP", "financial", "global", "compact_uppercase", False, 9),
        ("sedol", "SEDOL", "financial", "global", "compact_uppercase", False, 7),
        ("occ_option_symbol", "OCC Option Symbol", "financial", "global", "compact_uppercase", False, 21),
        ("exchange_contract_code", "Exchange Contract Code", "financial", "entity", "uppercase_trim", False, 64),
        ("iso_4217_alpha", "ISO 4217 Alpha", "financial", "global", "uppercase_trim", False, 3),
        ("iso_4217_numeric", "ISO 4217 Numeric", "financial", "global", "digits_only", False, 3),
        ("cik", "CIK", "organization", "global", "digits_only", False, 10),
        ("lei", "LEI", "organization", "global", "compact_uppercase", False, 20),
        ("iso_3166_alpha2", "ISO 3166 Alpha-2", "geographic", "global", "uppercase_trim", False, 2),
        ("iso_3166_alpha3", "ISO 3166 Alpha-3", "geographic", "global", "uppercase_trim", False, 3),
        ("iso_3166_numeric", "ISO 3166 Numeric", "geographic", "global", "digits_only", False, 3),
        ("iata_airport", "IATA Airport Code", "geographic", "global", "uppercase_trim", False, 3),
        ("icao_airport", "ICAO Airport Code", "geographic", "global", "uppercase_trim", False, 4),
        ("unlocode", "UN/LOCODE", "geographic", "global", "compact_uppercase", False, 5),
        ("mic", "Market Identifier Code (MIC)", "geographic", "global", "uppercase_trim", False, 4),
        ("fred_series", "FRED Series ID", "economic", "global", "uppercase_trim", False, 64),
        ("world_bank_indicator", "World Bank Indicator", "economic", "global", "uppercase_trim", False, 64),
        ("oecd_series", "OECD Series", "economic", "global", "preserve_trim", False, 128),
        ("imf_series", "IMF Series", "economic", "global", "preserve_trim", False, 128),
        ("doi", "DOI", "research", "global", "doi", False, 256),
        ("arxiv", "arXiv ID", "research", "global", "arxiv", False, 64),
        ("openalex", "OpenAlex ID", "research", "global", "openalex", False, 64),
        ("semantic_scholar", "Semantic Scholar ID", "research", "global", "preserve_trim", False, 64),
        ("pubmed", "PubMed ID", "research", "global", "digits_only", False, 32),
        ("isbn_10", "ISBN-10", "research", "global", "isbn10", False, 10),
        ("isbn_13", "ISBN-13", "research", "global", "isbn13", False, 13),
        ("crossref", "Crossref ID", "research", "global", "preserve_trim", False, 128),
        ("provider_external_id", "Provider External ID", "provider", "namespace", "preserve_trim", True, 256),
    ]
    
    op.bulk_insert(
        identifier_schemes,
        [
            dict(
                key=row[0],
                name=row[1],
                category=row[2],
                scope_policy=row[3],
                normalization_strategy=row[4],
                case_sensitive=row[5],
                max_length=row[6],
                is_system=True,
            ) for row in schemes_data
        ]
    )


def downgrade() -> None:
    op.execute("DROP INDEX ix_entity_identifiers_current_assignment")
    op.execute("DROP INDEX ix_entity_identifiers_current_lookup")
    op.drop_index("ix_entity_identifiers_scope_entity_id", table_name="entity_identifiers")
    op.drop_index("ix_entity_identifiers_entity_id", table_name="entity_identifiers")
    op.drop_table("entity_identifiers")
    op.drop_table("identifier_schemes")
