"""FastAPI Router for Country Economics Intelligence (Stage 90).

Endpoints:
- GET /api/v1/economics/countries
- GET /api/v1/economics/countries/{country_id}/overview
- GET /api/v1/economics/countries/{country_id}/profile
- GET /api/v1/economics/countries/{country_id}/gdp
- GET /api/v1/economics/countries/{country_id}/gdp/production
- GET /api/v1/economics/countries/{country_id}/inflation
- GET /api/v1/economics/countries/{country_id}/labor
- GET /api/v1/economics/countries/{country_id}/industry
- GET /api/v1/economics/countries/{country_id}/monetary
- GET /api/v1/economics/countries/{country_id}/fiscal
- GET /api/v1/economics/countries/{country_id}/external
- GET /api/v1/economics/countries/{country_id}/demographics
- GET /api/v1/economics/countries/{country_id}/coverage
"""

import logging
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.economics.countries import (
    CountryCoverageResponseDTO,
    CountryDemographicsSummaryDTO,
    CountryEconomicProfileDTO,
    CountryEconomicsOverviewDTO,
    CountryEconomicsService,
    CountryExternalSummaryDTO,
    CountryFiscalSummaryDTO,
    CountryGDPDecompositionDTO,
    CountryGeographyNotFoundError,
    CountryIndicatorUnavailableError,
    CountryIndustrySummaryDTO,
    CountryInflationSummaryDTO,
    CountryLaborSummaryDTO,
    CountryMonetarySummaryDTO,
    CountryPeriodInvalidError,
    CountryProductionDecompositionDTO,
    CountryReconciliationError,
    GDPApproachKind,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/economics/countries",
    tags=["Country Economics"],
)

_service: Optional[CountryEconomicsService] = None


def get_country_economics_service() -> CountryEconomicsService:
    global _service
    if _service is None:
        _service = CountryEconomicsService()
    return _service


@router.get(
    "",
    response_model=List[CountryEconomicProfileDTO],
    summary="List Supported Sovereign Countries & Economic Areas",
    description="Returns metadata profiles for all supported sovereign nations and economic areas.",
)
async def list_countries(
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[CountryEconomicProfileDTO]:
    return service.list_countries()


@router.get(
    "/{country_id}/overview",
    response_model=CountryEconomicsOverviewDTO,
    summary="Get Sovereign Country Macroeconomic Overview",
    description="Returns high-density macroeconomic summary for a sovereign country or economic area.",
)
async def get_country_overview(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryEconomicsOverviewDTO:
    try:
        return service.get_overview(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/profile",
    response_model=CountryEconomicProfileDTO,
    summary="Get Sovereign Country Profile & Governance Metadata",
    description="Returns statistical agency, central bank, accounting standards, and reporting periods.",
)
async def get_country_profile(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryEconomicProfileDTO:
    try:
        return service.get_profile(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/gdp",
    response_model=CountryGDPDecompositionDTO,
    summary="Get National Accounts GDP & Expenditure Decomposition",
    description="Returns nominal and real GDP, per-capita GDP, and expenditure components (C + I + G + Net Exports).",
)
async def get_country_gdp(
    country_id: str,
    approach: GDPApproachKind = Query(GDPApproachKind.EXPENDITURE, description="Accounting approach (EXPENDITURE or PRODUCTION)"),
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryGDPDecompositionDTO:
    try:
        return service.get_gdp(country_id, approach)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except (CountryPeriodInvalidError, CountryReconciliationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/{country_id}/gdp/production",
    response_model=CountryProductionDecompositionDTO,
    summary="Get Gross Value Added by Economic Sector",
    description="Returns production-side value added across Agriculture, Industry, and Services sectors.",
)
async def get_country_gdp_production(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryProductionDecompositionDTO:
    try:
        return service.get_production(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/inflation",
    response_model=CountryInflationSummaryDTO,
    summary="Get Sovereign Inflation & Price Conditions",
    description="Returns headline CPI, core CPI, food and energy inflation rates, and index level history.",
)
async def get_country_inflation(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryInflationSummaryDTO:
    try:
        return service.get_inflation(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except CountryIndicatorUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/labor",
    response_model=CountryLaborSummaryDTO,
    summary="Get Labor Market, Employment & Wage Indicators",
    description="Returns unemployment rate, labor force participation, employment levels, and survey methodology.",
)
async def get_country_labor(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryLaborSummaryDTO:
    try:
        return service.get_labor(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/industry",
    response_model=CountryIndustrySummaryDTO,
    summary="Get Industrial Output, Retail Sales & Confidence",
    description="Returns industrial production index, manufacturing activity, retail sales, and sentiment.",
)
async def get_country_industry(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryIndustrySummaryDTO:
    try:
        return service.get_industry(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/monetary",
    response_model=CountryMonetarySummaryDTO,
    summary="Get Domestic Monetary Conditions & Credit",
    description="Returns policy target rate context, broad money supply (M1/M2), and bank credit to private sector.",
)
async def get_country_monetary(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryMonetarySummaryDTO:
    try:
        return service.get_monetary(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/fiscal",
    response_model=CountryFiscalSummaryDTO,
    summary="Get Sovereign Public Finances & Government Debt",
    description="Returns general government revenue, expenditure, fiscal balance, primary balance, and gross debt.",
)
async def get_country_fiscal(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryFiscalSummaryDTO:
    try:
        return service.get_fiscal(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/external",
    response_model=CountryExternalSummaryDTO,
    summary="Get Balance of Payments, Trade & FX Reserves",
    description="Returns merchandise and services trade, current account, FDI, external debt, and foreign exchange reserves.",
)
async def get_country_external(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryExternalSummaryDTO:
    try:
        return service.get_external(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/demographics",
    response_model=CountryDemographicsSummaryDTO,
    summary="Get Demographic Structure & Population Statistics",
    description="Returns total population, working-age share, youth/elderly dependency ratios, and urbanization rate.",
)
async def get_country_demographics(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryDemographicsSummaryDTO:
    try:
        return service.get_demographics(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except CountryIndicatorUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{country_id}/coverage",
    response_model=CountryCoverageResponseDTO,
    summary="Get Country Data Coverage & Availability",
    description="Returns verified availability of national accounts, inflation, labor, fiscal, and external datasets.",
)
async def get_country_coverage(
    country_id: str,
    service: CountryEconomicsService = Depends(get_country_economics_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CountryCoverageResponseDTO:
    try:
        return service.get_coverage(country_id)
    except CountryGeographyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
