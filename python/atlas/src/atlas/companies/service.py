import uuid
from datetime import date
from typing import Any, List, Optional
from urllib.parse import urlparse

from atlas.entities.models import Entity
from atlas.entities.service import EntityService
from atlas.market_data.live.service import LiveQuoteService

from .errors import (
    CompanyNotFoundError,
    InvalidCompanyCountryError,
    InvalidCompanyEntityError,
    InvalidCompanyStatusError,
    InvalidCompanyURLError,
    InvalidOrganizationTypeError,
    InvalidPaginationError,
)
from .models import Company
from .repository import CompanyRepository
from .schemas import (
    CompanyFinancialSummary,
    CompanyIdentity,
    CompanyMarketSummary,
    CompanyOverviewResponse,
    CompanySearchResponse,
    PaginatedDocumentsResponse,
    PaginatedNewsResponse,
    PaginatedSecuritiesResponse,
    RelatedSecurityItem,
    SectionAvailability,
)
from .types import CompanyStatus, OrganizationType


class CompanyService:
    def __init__(
        self,
        repository: CompanyRepository,
        entity_service: EntityService,
    ):
        self.repository = repository
        self.entity_service = entity_service

    def _validate_url(self, url: Optional[str]) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if not url:
            return None

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise InvalidCompanyURLError(url)
        if not parsed.netloc:
            raise InvalidCompanyURLError(url)

        return url

    def _normalize_string(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        value = value.strip()
        if not value:
            return None
        return value

    async def _validate_country(self, country_id: Optional[uuid.UUID]) -> None:
        if not country_id:
            return

        try:
            entity = await self.entity_service.get_entity(country_id)
            if entity.entity_type != "country":
                raise InvalidCompanyCountryError(str(country_id))
        except Exception as e:
            if isinstance(e, InvalidCompanyCountryError):
                raise
            raise InvalidCompanyCountryError(str(country_id)) from e

    async def get_company(self, entity_id: uuid.UUID) -> tuple[Entity, Company]:
        """
        Reads the company. Returns both the base Entity and the Company specialization.
        """
        entity = await self.entity_service.get_entity(entity_id)
        if entity.entity_type != "company":
            raise InvalidCompanyEntityError(str(entity_id))

        company = await self.repository.get_company(entity_id)
        if not company:
            raise CompanyNotFoundError(str(entity_id))

        return entity, company

    async def create_company(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        legal_name: Optional[str] = None,
        short_name: Optional[str] = None,
        organization_type: Optional[str] = None,
        status: Optional[str] = None,
        founded_date: Optional[date] = None,
        website_url: Optional[str] = None,
        primary_country_entity_id: Optional[uuid.UUID] = None,
        force_entity_id: Optional[uuid.UUID] = None,
    ) -> tuple[Entity, Company]:
        if organization_type and organization_type not in OrganizationType:
            raise InvalidOrganizationTypeError(organization_type)

        if status and status not in CompanyStatus:
            raise InvalidCompanyStatusError(status)

        await self._validate_country(primary_country_entity_id)

        validated_url = self._validate_url(website_url)

        entity = await self.entity_service.create_entity(
            entity_type="company",
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
            force_entity_id=force_entity_id,
        )

        company = Company(
            entity_id=entity.entity_id,
            legal_name=self._normalize_string(legal_name),
            short_name=self._normalize_string(short_name),
            organization_type=organization_type,
            status=status,
            founded_date=founded_date,
            website_url=validated_url,
            primary_country_entity_id=primary_country_entity_id,
        )
        self.repository.add(company)

        return entity, company

    async def update_company(
        self,
        entity_id: uuid.UUID,
        canonical_name: Any = None,
        display_name: Any = None,
        description: Any = None,
        legal_name: Any = None,
        short_name: Any = None,
        organization_type: Any = None,
        status: Any = None,
        founded_date: Any = None,
        website_url: Any = None,
        primary_country_entity_id: Any = None,
    ) -> tuple[Entity, Company]:
        entity, company = await self.get_company(entity_id)

        await self.entity_service.update_base_entity(
            entity_id=entity_id,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        if legal_name is not None:
            company.legal_name = self._normalize_string(legal_name)
        if short_name is not None:
            company.short_name = self._normalize_string(short_name)
        if organization_type is not None:
            if organization_type not in OrganizationType:
                raise InvalidOrganizationTypeError(organization_type)
            company.organization_type = organization_type
        if status is not None:
            if status not in CompanyStatus:
                raise InvalidCompanyStatusError(status)
            company.status = status
        if founded_date is not None:
            company.founded_date = founded_date
        if website_url is not None:
            company.website_url = self._validate_url(website_url)
        if primary_country_entity_id is not None:
            await self._validate_country(primary_country_entity_id)
            company.primary_country_entity_id = primary_country_entity_id

        return entity, company

    # -----------------------------------------------------------------------
    # Stage 81: High-Performance Canonical Company Overview Service
    # -----------------------------------------------------------------------
    async def get_company_overview(
        self,
        entity_id: uuid.UUID,
        quote_service: Optional[LiveQuoteService] = None,
        is_financial_entitled: bool = True,
        is_news_entitled: bool = True,
        is_doc_entitled: bool = True,
    ) -> CompanyOverviewResponse:
        """
        Builds the unified, source-qualified Company Overview model.
        Aggregates identity, classifications, geography, identifiers,
        related securities, qualified market context, financial summary, and references.
        Guarantees zero upstream provider fanout on read.
        """
        entity, company = await self.get_company(entity_id)

        # 1. Aliases & Identifiers
        aliases = await self.repository.get_company_aliases(entity_id)
        identifiers = await self.repository.get_company_identifiers(entity_id)

        # 2. Geography & Classification
        geography = await self.repository.get_company_geography(company, entity)
        primary_ticker = await self.repository._resolve_primary_ticker(entity_id)
        classification = self.repository.get_company_classification(company, entity, primary_ticker)

        # 3. Related Securities & Quotes
        securities, total_sec = await self.repository.get_related_securities(entity_id, page=1, page_size=25)
        if quote_service is not None and securities:
            await self._overlay_live_quotes(securities, quote_service)

        # 4. Market Summary
        market_summary = self.repository.get_company_market_summary(entity_id, securities, primary_ticker)

        # 5. Financial Summary (Entitlement checked)
        if is_financial_entitled:
            financial_summary = self.repository.get_company_financial_summary(entity_id)
        else:
            financial_summary = CompanyFinancialSummary(
                reporting_currency="USD",
                metrics=[],
                status="NOT_ENTITLED",
            )

        # 6. News References (Entitlement checked)
        if is_news_entitled:
            recent_news, _ = self.repository.get_company_news(entity_id, securities, page=1, page_size=10)
            news_status = "AVAILABLE" if recent_news else "UNAVAILABLE"
        else:
            recent_news = []
            news_status = "NOT_ENTITLED"

        # 7. Document References (Entitlement checked)
        if is_doc_entitled:
            documents, _ = await self.repository.get_company_documents(entity_id, page=1, page_size=10)
            doc_status = "AVAILABLE" if documents else "UNAVAILABLE"
        else:
            documents = []
            doc_status = "NOT_ENTITLED"

        # Section availability
        availability = SectionAvailability(
            identity="AVAILABLE",
            profile="AVAILABLE" if entity.description else "UNAVAILABLE",
            classification=classification.status,
            geography=geography.status,
            identifiers="AVAILABLE" if identifiers else "UNAVAILABLE",
            securities="AVAILABLE" if securities else "UNAVAILABLE",
            market_summary=market_summary.status,
            financial_summary=financial_summary.status,
            news=news_status,
            documents=doc_status,
        )

        identity = CompanyIdentity(
            company_entity_id=company.entity_id,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            legal_name=company.legal_name,
            short_name=company.short_name,
            organization_type=company.organization_type,
            status=company.status,
            founded_date=company.founded_date,
            website_url=company.website_url,
            aliases=aliases,
        )

        return CompanyOverviewResponse(
            company_entity_id=company.entity_id,
            identity=identity,
            description=entity.description,
            classification=classification,
            geography=geography,
            identifiers=identifiers,
            related_securities=securities,
            market_summary=market_summary,
            financial_summary=financial_summary,
            recent_news=recent_news,
            documents=documents,
            section_availability=availability,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def search_companies(
        self,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        organization_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> CompanySearchResponse:
        if page < 1 or page_size < 1 or page_size > 100:
            raise InvalidPaginationError("Page must be >= 1 and page_size between 1 and 100")

        results, total = await self.repository.search_companies(
            query=query,
            page=page,
            page_size=page_size,
            organization_type=organization_type,
            status=status,
        )

        return CompanySearchResponse(
            results=results,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_securities(
        self,
        entity_id: uuid.UUID,
        page: int = 1,
        page_size: int = 25,
        quote_service: Optional[LiveQuoteService] = None,
    ) -> PaginatedSecuritiesResponse:
        if page < 1 or page_size < 1 or page_size > 100:
            raise InvalidPaginationError("Page must be >= 1 and page_size between 1 and 100")

        await self.get_company(entity_id)

        items, total = await self.repository.get_related_securities(
            company_id=entity_id,
            page=page,
            page_size=page_size,
        )
        if quote_service is not None and items:
            await self._overlay_live_quotes(items, quote_service)

        return PaginatedSecuritiesResponse(
            results=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_market_summary(
        self,
        entity_id: uuid.UUID,
        quote_service: Optional[LiveQuoteService] = None,
    ) -> CompanyMarketSummary:
        await self.get_company(entity_id)
        securities, _ = await self.repository.get_related_securities(entity_id, page=1, page_size=25)
        if quote_service is not None and securities:
            await self._overlay_live_quotes(securities, quote_service)

        primary_ticker = await self.repository._resolve_primary_ticker(entity_id)
        return self.repository.get_company_market_summary(entity_id, securities, primary_ticker)

    async def get_financial_summary(
        self,
        entity_id: uuid.UUID,
        is_entitled: bool = True,
    ) -> CompanyFinancialSummary:
        await self.get_company(entity_id)
        if not is_entitled:
            return CompanyFinancialSummary(
                reporting_currency="USD",
                metrics=[],
                status="NOT_ENTITLED",
            )
        return self.repository.get_company_financial_summary(entity_id)

    async def get_news(
        self,
        entity_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        is_entitled: bool = True,
    ) -> PaginatedNewsResponse:
        if page < 1 or page_size < 1 or page_size > 100:
            raise InvalidPaginationError("Page must be >= 1 and page_size between 1 and 100")

        await self.get_company(entity_id)
        if not is_entitled:
            return PaginatedNewsResponse(results=[], total=0, page=page, page_size=page_size)

        securities, _ = await self.repository.get_related_securities(entity_id, page=1, page_size=25)
        items, total = self.repository.get_company_news(entity_id, securities, page=page, page_size=page_size)
        return PaginatedNewsResponse(results=items, total=total, page=page, page_size=page_size)

    async def get_documents(
        self,
        entity_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10,
        is_entitled: bool = True,
    ) -> PaginatedDocumentsResponse:
        if page < 1 or page_size < 1 or page_size > 100:
            raise InvalidPaginationError("Page must be >= 1 and page_size between 1 and 100")

        await self.get_company(entity_id)
        if not is_entitled:
            return PaginatedDocumentsResponse(results=[], total=0, page=page, page_size=page_size)

        items, total = await self.repository.get_company_documents(entity_id, page=page, page_size=page_size)
        return PaginatedDocumentsResponse(results=items, total=total, page=page, page_size=page_size)

    # --- Live Quote Overlay Helper (0 Provider Fanout) ---

    async def _overlay_live_quotes(
        self,
        securities: List[RelatedSecurityItem],
        quote_service: LiveQuoteService,
    ) -> None:
        inst_ids = [s.instrument_entity_id for s in securities]
        try:
            records = await quote_service.get_latest_quotes(inst_ids)
            for s in securities:
                rec = records.get(s.instrument_entity_id)
                if rec is not None and rec.quote is not None:
                    q = rec.quote
                    s.is_quote_available = True
                    s.latest_price = f"{q.price:.2f}"
                    if q.bid is not None:
                        s.bid_price = f"{q.bid:.2f}"
                    if q.ask is not None:
                        s.ask_price = f"{q.ask:.2f}"
                    if q.net_change is not None:
                        s.absolute_change = f"{q.net_change:+.2f}"
                        if q.net_change > 0:
                            s.change_direction = "up"
                        elif q.net_change < 0:
                            s.change_direction = "down"
                        else:
                            s.change_direction = "flat"
                    if q.percentage_change is not None:
                        s.percentage_change = f"{q.percentage_change:+.2f}%"
                    s.source_timestamp = q.source_timestamp
                    s.provider = q.provider or "canonical"
                    s.freshness_status = "live"
                    s.delay_status = "realtime"
        except Exception:
            # Live quote overlay failure does not block the company overview
            pass
