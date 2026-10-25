import datetime
import logging
import uuid
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.aliases.models import EntityAlias
from atlas.entities.models import Entity
from atlas.geography.models import Facility
from atlas.identifiers.models import EntityIdentifier, IdentifierScheme
from atlas.instruments.models import Bond, Equity, FinancialInstrument, Security
from atlas.markets.heatmaps.repository import _EQUITY_SNAPSHOTS
from atlas.relationships.models import EntityRelationship
from atlas.research.models import ResearchDocument
from atlas.watchlists.enrichment.fundamentals import _STATEMENT_STORE
from atlas.watchlists.enrichment.news import _ENTITY_NEWS_STORE

from .models import Company
from .schemas import (
    CompanyClassification,
    CompanyDocumentReference,
    CompanyFinancialSummary,
    CompanyGeography,
    CompanyIdentifierItem,
    CompanyMarketSummary,
    CompanyNewsReference,
    CompanySearchResult,
    FinancialSummaryMetric,
    RelatedSecurityItem,
)

logger = logging.getLogger(__name__)

# In-memory document registry for verified corporate filings/research documents
_CORPORATE_DOCUMENT_STORE: Dict[uuid.UUID, List[CompanyDocumentReference]] = {}


def register_verified_documents_for_company(
    company_id: uuid.UUID,
    documents: List[CompanyDocumentReference],
) -> None:
    """Helper used by tests and background adapters to register verified corporate documents."""
    _CORPORATE_DOCUMENT_STORE[company_id] = sorted(
        documents, key=lambda d: d.publication_date or datetime.date.min, reverse=True
    )


def clear_verified_documents_store() -> None:
    """Clear corporate document store (for test isolation)."""
    _CORPORATE_DOCUMENT_STORE.clear()


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_company(self, entity_id: uuid.UUID) -> Optional[Company]:
        stmt = select(Company).where(Company.entity_id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def add(self, company: Company) -> None:
        self._session.add(company)

    async def get_company_with_entity(self, entity_id: uuid.UUID) -> Optional[Tuple[Entity, Company]]:
        stmt = (
            select(Entity, Company)
            .join(Company, Entity.entity_id == Company.entity_id)
            .where(Entity.entity_id == entity_id, Entity.entity_type == "company")
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if not row:
            return None
        return row[0], row[1]

    async def search_companies(
        self,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        organization_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[CompanySearchResult], int]:
        """
        Bounded, parameterized search over canonical Company entities.
        Matches display name, legal name, canonical name, aliases, identifiers, or ticker.
        Zero provider fanout.
        """
        if page < 1 or page_size < 1 or page_size > 100:
            page = 1
            page_size = 20

        stmt = (
            select(Entity, Company)
            .join(Company, Entity.entity_id == Company.entity_id)
            .where(Entity.entity_type == "company")
        )

        if organization_type:
            stmt = stmt.where(Company.organization_type == organization_type)
        if status:
            stmt = stmt.where(Company.status == status)

        if query and query.strip():
            q = query.strip()
            # 1. Direct text matches
            conditions = [
                Entity.display_name.ilike(f"%{q}%"),
                Entity.canonical_name.ilike(f"%{q}%"),
                Company.legal_name.ilike(f"%{q}%"),
                Company.short_name.ilike(f"%{q}%"),
            ]

            # 2. Subquery on aliases
            alias_subq = (
                select(EntityAlias.entity_id)
                .where(EntityAlias.value.ilike(f"%{q}%"), EntityAlias.is_current.is_(True))
            )
            conditions.append(Entity.entity_id.in_(alias_subq))

            # 3. Subquery on identifiers (CIK, LEI, national registration)
            ident_subq = (
                select(EntityIdentifier.entity_id)
                .where(EntityIdentifier.value.ilike(f"%{q}%"), EntityIdentifier.is_current.is_(True))
            )
            conditions.append(Entity.entity_id.in_(ident_subq))

            # 4. Reverse ticker match: if query matches an instrument's ticker symbol, find issuer company
            ticker_subq = (
                select(EntityRelationship.target_entity_id)
                .join(
                    EntityIdentifier,
                    EntityIdentifier.entity_id == EntityRelationship.source_entity_id,
                )
                .where(
                    EntityIdentifier.scheme_key == "ticker",
                    EntityIdentifier.normalized_value == q.upper(),
                    EntityIdentifier.is_current.is_(True),
                    EntityRelationship.relationship_type_key == "issued_by",
                    EntityRelationship.is_current.is_(True),
                )
            )
            conditions.append(Entity.entity_id.in_(ticker_subq))

            # Reverse ticker match for 'issued' relationship
            ticker_issued_subq = (
                select(EntityRelationship.source_entity_id)
                .join(
                    EntityIdentifier,
                    EntityIdentifier.entity_id == EntityRelationship.target_entity_id,
                )
                .where(
                    EntityIdentifier.scheme_key == "ticker",
                    EntityIdentifier.normalized_value == q.upper(),
                    EntityIdentifier.is_current.is_(True),
                    EntityRelationship.relationship_type_key == "issued",
                    EntityRelationship.is_current.is_(True),
                )
            )
            conditions.append(Entity.entity_id.in_(ticker_issued_subq))

            stmt = stmt.where(or_(*conditions))

        # Total count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self._session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Paginated results
        stmt = stmt.order_by(Entity.display_name.asc()).offset((page - 1) * page_size).limit(page_size)
        rows_res = await self._session.execute(stmt)
        rows = rows_res.all()

        results: List[CompanySearchResult] = []
        for entity, company in rows:
            primary_ticker = await self._resolve_primary_ticker(company.entity_id)
            country_name, country_code = await self._resolve_country_info(company.primary_country_entity_id)
            sector, industry = self._resolve_sector_industry(company.entity_id, primary_ticker)
            has_public = bool(primary_ticker)

            results.append(
                CompanySearchResult(
                    company_entity_id=company.entity_id,
                    canonical_name=entity.canonical_name,
                    display_name=entity.display_name,
                    legal_name=company.legal_name,
                    primary_ticker=primary_ticker,
                    country=country_name,
                    country_code=country_code,
                    sector=sector,
                    industry=industry,
                    organization_type=company.organization_type,
                    status=company.status,
                    has_public_securities=has_public,
                )
            )

        return results, total

    async def get_company_aliases(self, entity_id: uuid.UUID) -> List[str]:
        stmt = (
            select(EntityAlias.value)
            .where(EntityAlias.entity_id == entity_id, EntityAlias.is_current.is_(True))
            .order_by(EntityAlias.value.asc())
        )
        res = await self._session.execute(stmt)
        return [row[0] for row in res.all()]

    async def get_company_identifiers(self, entity_id: uuid.UUID) -> List[CompanyIdentifierItem]:
        # Exclude security-only identifiers like isin, figi, cusip from company-level registration
        security_schemes = {"isin", "figi", "composite_figi", "share_class_figi", "cusip", "sedol"}

        stmt = (
            select(EntityIdentifier, IdentifierScheme.name)
            .outerjoin(IdentifierScheme, EntityIdentifier.scheme_key == IdentifierScheme.key)
            .where(
                EntityIdentifier.entity_id == entity_id,
                EntityIdentifier.is_current.is_(True),
            )
            .order_by(EntityIdentifier.scheme_key.asc())
        )
        res = await self._session.execute(stmt)
        items: List[CompanyIdentifierItem] = []
        for ident, scheme_name in res.all():
            if ident.scheme_key.lower() in security_schemes:
                continue
            items.append(
                CompanyIdentifierItem(
                    identifier_id=ident.identifier_id,
                    scheme_key=ident.scheme_key,
                    scheme_name=scheme_name or ident.scheme_key.upper(),
                    value=ident.value,
                    normalized_value=ident.normalized_value,
                    namespace=ident.namespace,
                    is_current=ident.is_current,
                    valid_from=ident.valid_from,
                    valid_to=ident.valid_to,
                    source="canonical",
                    verification_status="verified",
                )
            )
        return items

    async def get_company_geography(self, company: Company, entity: Entity) -> CompanyGeography:
        country_name, country_code = await self._resolve_country_info(company.primary_country_entity_id)

        # Check for facility relationship for headquarters
        hq_city = None
        hq_address = None
        facility_stmt = (
            select(Facility)
            .join(
                EntityRelationship,
                EntityRelationship.target_entity_id == Facility.entity_id,
            )
            .where(
                EntityRelationship.source_entity_id == company.entity_id,
                EntityRelationship.relationship_type_key.in_(["owns", "operates"]),
                EntityRelationship.is_current.is_(True),
            )
        )
        fac_res = await self._session.execute(facility_stmt)
        facility = fac_res.scalars().first()
        if facility:
            hq_city = facility.locality_name or facility.region_name
            hq_address = facility.address_text

        status = "AVAILABLE" if (country_name or hq_city) else "UNAVAILABLE"

        return CompanyGeography(
            headquarters_city=hq_city,
            headquarters_country=country_name,
            country_code=country_code,
            country_entity_id=company.primary_country_entity_id,
            incorporation_jurisdiction=country_name,
            domicile_country=country_name,
            address_text=hq_address,
            source="canonical",
            status=status,
        )

    def get_company_classification(
        self,
        company: Company,
        entity: Entity,
        primary_symbol: Optional[str] = None,
    ) -> CompanyClassification:
        sector, industry = self._resolve_sector_industry(company.entity_id, primary_symbol)
        if sector == "Unclassified" and not industry:
            return CompanyClassification(
                taxonomy="GICS",
                taxonomy_version="2023",
                sector_name=None,
                industry_name=None,
                source="canonical",
                as_of=datetime.datetime.now(datetime.timezone.utc),
                status="UNAVAILABLE",
            )

        return CompanyClassification(
            taxonomy="GICS",
            taxonomy_version="2023",
            sector_name=sector if sector != "Unclassified" else None,
            industry_name=industry,
            source="canonical",
            as_of=datetime.datetime.now(datetime.timezone.utc),
            status="AVAILABLE",
        )

    async def get_related_securities(
        self,
        company_id: uuid.UUID,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[RelatedSecurityItem], int]:
        """
        Bounded, typed resolution of instruments issued by the Company.
        Distinguishes common equity, preferred, depositary receipts (ADRs), and corporate bonds.
        """
        if page < 1 or page_size < 1 or page_size > 100:
            page = 1
            page_size = 25

        # Query instruments where company is source (issued) or target (issued_by)
        stmt = (
            select(
                EntityRelationship.relationship_type_key,
                EntityRelationship.is_current,
                EntityRelationship.source_entity_id,
                EntityRelationship.target_entity_id,
            )
            .where(
                EntityRelationship.is_current.is_(True),
                or_(
                    (
                        EntityRelationship.source_entity_id == company_id
                        and EntityRelationship.relationship_type_key == "issued"
                    ),
                    (
                        EntityRelationship.target_entity_id == company_id
                        and EntityRelationship.relationship_type_key == "issued_by"
                    ),
                ),
            )
        )
        rel_res = await self._session.execute(stmt)
        rel_rows = rel_res.all()

        instrument_id_map: Dict[uuid.UUID, str] = {}
        for row in rel_rows:
            inst_id = row.target_entity_id if row.source_entity_id == company_id else row.source_entity_id
            instrument_id_map[inst_id] = row.relationship_type_key

        unique_instrument_ids = list(instrument_id_map.keys())
        total = len(unique_instrument_ids)
        if total == 0:
            return [], 0

        # Apply pagination on instrument IDs
        start = (page - 1) * page_size
        end = start + page_size
        paged_instrument_ids = unique_instrument_ids[start:end]

        # Batch query instruments details
        inst_stmt = (
            select(
                Entity,
                FinancialInstrument,
                Security,
                Equity,
                Bond,
            )
            .join(FinancialInstrument, Entity.entity_id == FinancialInstrument.entity_id)
            .outerjoin(Security, FinancialInstrument.entity_id == Security.entity_id)
            .outerjoin(Equity, Security.entity_id == Equity.entity_id)
            .outerjoin(Bond, Security.entity_id == Bond.entity_id)
            .where(Entity.entity_id.in_(paged_instrument_ids))
        )
        inst_res = await self._session.execute(inst_stmt)
        inst_rows = inst_res.all()

        # Batch query tickers for these instruments
        ticker_stmt = (
            select(EntityIdentifier.entity_id, EntityIdentifier.value)
            .where(
                EntityIdentifier.entity_id.in_(paged_instrument_ids),
                EntityIdentifier.scheme_key == "ticker",
                EntityIdentifier.is_current.is_(True),
            )
        )
        ticker_res = await self._session.execute(ticker_stmt)
        tickers: Dict[uuid.UUID, str] = {row[0]: row[1] for row in ticker_res.all()}

        # Build related security items
        items: List[RelatedSecurityItem] = []
        for ent, fin_inst, sec, eq, bnd in inst_rows:
            symbol = tickers.get(ent.entity_id)
            rel_type = instrument_id_map.get(ent.entity_id, "issued")

            if bnd is not None:
                asset_class = "bond"
                security_type = "corporate_bond"
                share_class = None
                currency = "USD"
                venue = "OTC"
            elif eq is not None:
                asset_class = "equity"
                currency = "USD"
                venue = "NASDAQ"  # Default exchange venue
                share_class = eq.share_class_name
                if eq.equity_kind == "depositary_receipt":
                    security_type = "depositary_receipt"
                elif eq.equity_kind == "preferred":
                    security_type = "preferred_equity"
                else:
                    security_type = "common_equity"
            else:
                asset_class = "equity"
                security_type = "common_equity"
                share_class = None
                currency = "USD"
                venue = "US"

            # Check for baseline quote in verified snapshot catalog
            quote_avail = False
            last_px = None
            abs_chg = None
            pct_chg = None
            direction = "flat"
            freshness = "unknown"
            delay_st = "realtime"
            provider = None
            measure = "Last" if asset_class == "equity" else "Clean Price"

            if symbol and symbol.upper() in _EQUITY_SNAPSHOTS:
                snap = _EQUITY_SNAPSHOTS[symbol.upper()]
                quote_avail = True
                curr_p = snap.get("current_price")
                ref_p = snap.get("reference_price")
                last_px = f"{curr_p:.2f}" if curr_p is not None else None
                if curr_p is not None and ref_p is not None:
                    diff = curr_p - ref_p
                    abs_chg = f"{diff:+.2f}"
                    pct = (diff / ref_p) * 100
                    pct_chg = f"{pct:+.2f}%"
                    direction = "up" if diff > 0 else ("down" if diff < 0 else "flat")
                provider = snap.get("provider", "openbb")
                delay_st = snap.get("delay_status", "realtime")
                freshness = snap.get("freshness_status", "live")

            items.append(
                RelatedSecurityItem(
                    instrument_entity_id=ent.entity_id,
                    canonical_name=ent.canonical_name,
                    display_name=ent.display_name,
                    symbol=symbol,
                    asset_class=asset_class,
                    security_type=security_type,
                    share_class_name=share_class,
                    exchange_or_venue=venue,
                    currency=currency,
                    relationship_type=rel_type,
                    is_current=True,
                    is_primary_listing=(security_type == "common_equity" and share_class in (None, "Common", "Class A")),
                    is_quote_available=quote_avail,
                    quote_measure=measure,
                    latest_price=last_px,
                    absolute_change=abs_chg,
                    percentage_change=pct_chg,
                    change_direction=direction,
                    source_timestamp=datetime.datetime.now(datetime.timezone.utc) if quote_avail else None,
                    provider=provider,
                    freshness_status=freshness,
                    delay_status=delay_st,
                )
            )

        return items, total

    def get_company_financial_summary(self, entity_id: uuid.UUID) -> CompanyFinancialSummary:
        """
        Extracts verified high-level financial summary from Stage 34 Fundamentals store.
        Returns UNAVAILABLE if reports are missing. Zero fabricated numbers.
        """
        stored = _STATEMENT_STORE.get(entity_id)
        if not stored:
            return CompanyFinancialSummary(
                reporting_currency="USD",
                fiscal_period=None,
                period_end_date=None,
                publication_date=None,
                consolidation_scope="consolidated",
                metrics=[],
                status="UNAVAILABLE",
            )

        inc_stmt = stored.get("income_statement")
        bal_sheet = stored.get("balance_sheet")

        reporting_currency = "USD"
        fiscal_period = None
        period_end = None
        pub_date = None

        if inc_stmt is not None:
            reporting_currency = inc_stmt.reporting_currency or "USD"
            fiscal_period = inc_stmt.period_label
            period_end = inc_stmt.period_end_date
            pub_date = inc_stmt.filing_date

        if bal_sheet is not None and not fiscal_period:
            reporting_currency = bal_sheet.reporting_currency or "USD"
            fiscal_period = bal_sheet.period_label
            period_end = bal_sheet.period_end_date
            pub_date = bal_sheet.filing_date

        metrics: List[FinancialSummaryMetric] = []

        # Revenue
        if inc_stmt and hasattr(inc_stmt, "revenue") and inc_stmt.revenue is not None:
            val = float(inc_stmt.revenue)
            formatted = f"${val / 1e9:.2f}B" if val >= 1e9 else f"${val / 1e6:.2f}M"
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="revenue",
                    metric_name="Revenue",
                    value=formatted,
                    raw_value=val,
                    unit=reporting_currency,
                    scale="billions" if val >= 1e9 else "millions",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        # Net Income
        if inc_stmt and hasattr(inc_stmt, "net_income") and inc_stmt.net_income is not None:
            val = float(inc_stmt.net_income)
            formatted = f"${val / 1e9:.2f}B" if abs(val) >= 1e9 else f"${val / 1e6:.2f}M"
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="net_income",
                    metric_name="Net Income",
                    value=formatted,
                    raw_value=val,
                    unit=reporting_currency,
                    scale="billions" if abs(val) >= 1e9 else "millions",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        # Reported EPS
        if inc_stmt and hasattr(inc_stmt, "diluted_eps") and inc_stmt.diluted_eps is not None:
            val = float(inc_stmt.diluted_eps)
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="diluted_eps",
                    metric_name="Reported EPS",
                    value=f"${val:.2f}",
                    raw_value=val,
                    unit=reporting_currency,
                    scale="exact",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        # Total Assets
        if bal_sheet and hasattr(bal_sheet, "total_assets") and bal_sheet.total_assets is not None:
            val = float(bal_sheet.total_assets)
            formatted = f"${val / 1e9:.2f}B" if val >= 1e9 else f"${val / 1e6:.2f}M"
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="total_assets",
                    metric_name="Total Assets",
                    value=formatted,
                    raw_value=val,
                    unit=reporting_currency,
                    scale="billions" if val >= 1e9 else "millions",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        # Total Equity
        if bal_sheet and hasattr(bal_sheet, "total_equity") and bal_sheet.total_equity is not None:
            val = float(bal_sheet.total_equity)
            formatted = f"${val / 1e9:.2f}B" if val >= 1e9 else f"${val / 1e6:.2f}M"
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="total_equity",
                    metric_name="Total Equity",
                    value=formatted,
                    raw_value=val,
                    unit=reporting_currency,
                    scale="billions" if val >= 1e9 else "millions",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        # Cash & Equivalents
        if bal_sheet and hasattr(bal_sheet, "cash_and_equivalents") and bal_sheet.cash_and_equivalents is not None:
            val = float(bal_sheet.cash_and_equivalents)
            formatted = f"${val / 1e9:.2f}B" if val >= 1e9 else f"${val / 1e6:.2f}M"
            metrics.append(
                FinancialSummaryMetric(
                    metric_key="cash_and_equivalents",
                    metric_name="Cash & Equivalents",
                    value=formatted,
                    raw_value=val,
                    unit=reporting_currency,
                    scale="billions" if val >= 1e9 else "millions",
                    fiscal_period=fiscal_period,
                    period_end_date=period_end,
                    publication_date=pub_date,
                    consolidation_scope="consolidated",
                    restatement_status="original",
                    source="canonical",
                    status="AVAILABLE",
                )
            )

        status = "AVAILABLE" if metrics else "UNAVAILABLE"

        return CompanyFinancialSummary(
            reporting_currency=reporting_currency,
            fiscal_period=fiscal_period,
            period_end_date=period_end,
            publication_date=pub_date,
            consolidation_scope="consolidated",
            metrics=metrics,
            status=status,
        )

    def get_company_market_summary(
        self,
        company_id: uuid.UUID,
        securities: List[RelatedSecurityItem],
        primary_symbol: Optional[str] = None,
    ) -> CompanyMarketSummary:
        total_count = len(securities)
        equity_count = sum(1 for s in securities if s.asset_class == "equity")
        bond_count = sum(1 for s in securities if s.asset_class == "bond")

        ref_sec = next((s for s in securities if s.is_primary_listing), None)
        if not ref_sec and securities:
            ref_sec = securities[0]

        sym = (ref_sec.symbol if ref_sec else None) or primary_symbol
        market_cap_str = None
        market_cap_curr = "USD"
        market_cap_src = None
        market_cap_method = None

        if sym and sym.upper() in _EQUITY_SNAPSHOTS:
            snap = _EQUITY_SNAPSHOTS[sym.upper()]
            mc = snap.get("market_cap")
            if mc:
                val = float(mc)
                market_cap_str = f"${val / 1e12:.2f}T" if val >= 1e12 else f"${val / 1e9:.2f}B"
                market_cap_src = snap.get("provider", "canonical")
                market_cap_method = "share_class_weighted"

        return CompanyMarketSummary(
            reference_security_id=ref_sec.instrument_entity_id if ref_sec else None,
            reference_symbol=sym,
            reference_venue=ref_sec.exchange_or_venue if ref_sec else None,
            reference_price=ref_sec.latest_price if ref_sec else None,
            market_cap=market_cap_str,
            market_cap_currency=market_cap_curr if market_cap_str else None,
            market_cap_as_of=datetime.datetime.now(datetime.timezone.utc) if market_cap_str else None,
            market_cap_source=market_cap_src,
            market_cap_methodology=market_cap_method,
            total_securities_count=total_count,
            listed_equity_count=equity_count,
            bond_count=bond_count,
            status="AVAILABLE" if (ref_sec or market_cap_str) else "UNAVAILABLE",
        )

    def get_company_news(
        self,
        company_id: uuid.UUID,
        securities: List[RelatedSecurityItem],
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[CompanyNewsReference], int]:
        if page < 1 or page_size < 1:
            page = 1
            page_size = 10

        articles_pool: List[CompanyNewsReference] = []

        # 1. Direct company news
        if company_id in _ENTITY_NEWS_STORE:
            for art in _ENTITY_NEWS_STORE[company_id]:
                articles_pool.append(
                    CompanyNewsReference(
                        title=art.title,
                        publisher=art.publisher,
                        published_at=art.published_at,
                        url=str(art.url) if art.url else None,
                        summary=art.summary,
                        authors=list(art.authors),
                        source="canonical",
                    )
                )

        # 2. Associated securities news
        for sec in securities:
            if sec.instrument_entity_id in _ENTITY_NEWS_STORE:
                for art in _ENTITY_NEWS_STORE[sec.instrument_entity_id]:
                    articles_pool.append(
                        CompanyNewsReference(
                            title=art.title,
                            publisher=art.publisher,
                            published_at=art.published_at,
                            url=str(art.url) if art.url else None,
                            summary=art.summary,
                            authors=list(art.authors),
                            source="canonical",
                        )
                    )

        # Deduplicate by (title, publisher)
        seen = set()
        deduped: List[CompanyNewsReference] = []
        for a in articles_pool:
            key = (a.title.strip().lower(), a.publisher.strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append(a)

        deduped.sort(key=lambda a: a.published_at, reverse=True)
        total = len(deduped)

        start = (page - 1) * page_size
        end = start + page_size
        return deduped[start:end], total

    async def get_company_documents(
        self,
        company_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[CompanyDocumentReference], int]:
        if page < 1 or page_size < 1:
            page = 1
            page_size = 10

        doc_pool: List[CompanyDocumentReference] = []

        # 1. From corporate document registry
        if company_id in _CORPORATE_DOCUMENT_STORE:
            doc_pool.extend(_CORPORATE_DOCUMENT_STORE[company_id])

        # 2. From database ResearchDocument related to this company
        stmt = (
            select(ResearchDocument, Entity)
            .join(Entity, Entity.entity_id == ResearchDocument.entity_id)
            .join(
                EntityRelationship,
                EntityRelationship.target_entity_id == ResearchDocument.entity_id,
            )
            .where(
                EntityRelationship.source_entity_id == company_id,
                EntityRelationship.is_current.is_(True),
            )
        )
        res = await self._session.execute(stmt)
        for r_doc, ent in res.all():
            doc_pool.append(
                CompanyDocumentReference(
                    document_id=r_doc.entity_id,
                    title=ent.display_name or ent.canonical_name,
                    document_kind=r_doc.document_kind,
                    publication_date=r_doc.publication_date,
                    language_code=r_doc.language_code or "en",
                    source="canonical",
                )
            )

        doc_pool.sort(key=lambda d: d.publication_date or datetime.date.min, reverse=True)
        total = len(doc_pool)
        start = (page - 1) * page_size
        end = start + page_size
        return doc_pool[start:end], total

    # --- Private Helpers ---

    async def _resolve_primary_ticker(self, company_id: uuid.UUID) -> Optional[str]:
        stmt = (
            select(EntityIdentifier.value)
            .join(
                EntityRelationship,
                EntityRelationship.target_entity_id == EntityIdentifier.entity_id,
            )
            .where(
                EntityRelationship.source_entity_id == company_id,
                EntityRelationship.relationship_type_key == "issued",
                EntityRelationship.is_current.is_(True),
                EntityIdentifier.scheme_key == "ticker",
                EntityIdentifier.is_current.is_(True),
            )
            .limit(1)
        )
        res = await self._session.execute(stmt)
        val = res.scalar_one_or_none()
        if val:
            return val

        # Check reverse issued_by
        rev_stmt = (
            select(EntityIdentifier.value)
            .join(
                EntityRelationship,
                EntityRelationship.source_entity_id == EntityIdentifier.entity_id,
            )
            .where(
                EntityRelationship.target_entity_id == company_id,
                EntityRelationship.relationship_type_key == "issued_by",
                EntityRelationship.is_current.is_(True),
                EntityIdentifier.scheme_key == "ticker",
                EntityIdentifier.is_current.is_(True),
            )
            .limit(1)
        )
        rev_res = await self._session.execute(rev_stmt)
        return rev_res.scalar_one_or_none()

    async def _resolve_country_info(
        self, country_entity_id: Optional[uuid.UUID]
    ) -> Tuple[Optional[str], Optional[str]]:
        if not country_entity_id:
            return None, None

        stmt = (
            select(Entity.display_name, EntityIdentifier.value)
            .outerjoin(
                EntityIdentifier,
                (EntityIdentifier.entity_id == Entity.entity_id)
                & (EntityIdentifier.scheme_key == "iso_3166_alpha2")
                & (EntityIdentifier.is_current.is_(True)),
            )
            .where(Entity.entity_id == country_entity_id)
        )
        res = await self._session.execute(stmt)
        row = res.first()
        if not row:
            return None, None
        return row[0], row[1]

    def _resolve_sector_industry(
        self,
        company_id: uuid.UUID,
        primary_symbol: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        if primary_symbol and primary_symbol.upper() in _EQUITY_SNAPSHOTS:
            snap = _EQUITY_SNAPSHOTS[primary_symbol.upper()]
            return snap.get("sector") or "Unclassified", snap.get("industry")
        return "Unclassified", None
