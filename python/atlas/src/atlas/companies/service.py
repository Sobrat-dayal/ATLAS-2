import uuid
from datetime import date
from typing import Optional, Any
from urllib.parse import urlparse

from atlas.entities.service import EntityService
from atlas.entities.models import Entity
from .repository import CompanyRepository
from .models import Company
from .types import OrganizationType, CompanyStatus
from .errors import (
    CompanyNotFoundError,
    CompanyDataInconsistentError,
    InvalidOrganizationTypeError,
    InvalidCompanyStatusError,
    InvalidCompanyCountryError,
    InvalidCompanyURLError
)

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
        
        # We must get the entity and ensure it is a "country".
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
            raise CompanyNotFoundError(str(entity_id))

        company = await self.repository.get_company(entity_id)
        if not company:
            raise CompanyDataInconsistentError(str(entity_id))

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
        """
        Atomically creates base Entity and Company specialization.
        Does not commit. Caller is responsible for transaction.
        """
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
            force_entity_id=force_entity_id
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
        """
        Updates Company and base Entity fields.
        Use `None` for UNCHANGED. Pass explicit values to update.
        Note: to unset a nullable field, use a sentinel or pass the empty string/None and handle it appropriately.
        For Stage 18, we will treat None as UNCHANGED for base entity fields per the signature, 
        and handle kwargs for company fields explicitly.
        """
        entity, company = await self.get_company(entity_id)

        # Base entity update
        await self.entity_service.update_base_entity(
            entity_id=entity_id,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description
        )

        # Update Company fields
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

        # Assuming entity_service.update_base_entity doesn't explicitly refresh updated_at if not flushed,
        # but SQLAlchemy will handle updated_at automatically on flush due to the onupdate server_default.
        # So we don't need to manually touch entities.updated_at here.

        return entity, company
