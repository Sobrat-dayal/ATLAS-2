"""FastAPI Router for Company Filings Intelligence (Stage 86).

Provides authenticated endpoints for regulatory filing discovery, document viewing,
full-text search, XBRL financial facts inspection, and amendment diff comparison.
"""

from typing import Optional

from atlas.authorization.permissions import PermissionCode
from atlas.companies.filings import (
    CompanyFilingsService,
    FilingCatalogResponseDTO,
    FilingCategory,
    FilingComparisonResponseDTO,
    FilingContentDTO,
    FilingCoverageDTO,
    FilingDetailDTO,
    FilingDocumentDTO,
    FilingDocumentNotFoundError,
    FilingNotFoundError,
    FilingSearchResponseDTO,
    FilingSourceReferenceDTO,
    XBRLFactsResponseDTO,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.authorization.dependencies import RequirePermission

router = APIRouter(
    prefix="/companies/{company_id}/filings",
    tags=["Company Filings Intelligence"],
)

_service: Optional[CompanyFilingsService] = None


def get_filings_service() -> CompanyFilingsService:
    """Dependency injector for CompanyFilingsService."""
    global _service
    if _service is None:
        _service = CompanyFilingsService()
    return _service


@router.get(
    "",
    response_model=FilingCatalogResponseDTO,
    summary="List regulatory filings catalog",
)
async def get_filings_catalog(
    company_id: str,
    category: Optional[FilingCategory] = Query(None, description="Filter by filing category"),
    form_type: Optional[str] = Query(None, description="Filter by specific form code (e.g. 10-K, 10-Q, 8-K)"),
    from_date: Optional[str] = Query(None, description="Filter filings on or after YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="Filter filings on or before YYYY-MM-DD"),
    limit: int = Query(25, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Page offset"),
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingCatalogResponseDTO:
    """Returns paginated catalog of regulatory filings for the company."""
    return service.get_filings_catalog(
        company_id=company_id,
        category=category,
        form_type=form_type,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/overview",
    summary="Get company filings overview summary",
)
async def get_filings_overview(
    company_id: str,
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    """Returns overview summary of filings: coverage, latest 10-K, latest 10-Q, latest 8-K."""
    coverage = service.get_filing_coverage(company_id)
    recent_annual = service.get_filings_catalog(
        company_id=company_id, category=FilingCategory.ANNUAL_REPORTS, limit=1
    )
    recent_quarterly = service.get_filings_catalog(
        company_id=company_id, category=FilingCategory.QUARTERLY_REPORTS, limit=1
    )
    recent_current = service.get_filings_catalog(
        company_id=company_id, category=FilingCategory.CURRENT_REPORTS, limit=1
    )

    return {
        "company_id": company_id,
        "coverage": coverage,
        "latest_annual": recent_annual.items[0] if recent_annual.items else None,
        "latest_quarterly": recent_quarterly.items[0] if recent_quarterly.items else None,
        "latest_current_report": recent_current.items[0] if recent_current.items else None,
    }


@router.get(
    "/coverage",
    response_model=FilingCoverageDTO,
    summary="Get regulatory filing coverage and source policy",
)
async def get_filing_coverage(
    company_id: str,
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingCoverageDTO:
    """Returns regulatory authority, total filings count, available forms, and source policy."""
    return service.get_filing_coverage(company_id)


@router.get(
    "/search",
    response_model=FilingSearchResponseDTO,
    summary="Full-text search within company filings",
)
async def search_filings(
    company_id: str,
    q: str = Query(..., min_length=1, description="Search term or phrase"),
    limit: int = Query(25, ge=1, le=50, description="Max search hits"),
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingSearchResponseDTO:
    """Performs full-text search across indexed filing documents and sections."""
    return service.search_filings(company_id=company_id, query=q, limit=limit)


@router.get(
    "/compare",
    response_model=FilingComparisonResponseDTO,
    summary="Compare two filings or amendments",
)
async def compare_filings(
    company_id: str,
    left_id: str = Query(..., description="Prior or original filing ID"),
    right_id: str = Query(..., description="Amended or subsequent filing ID"),
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingComparisonResponseDTO:
    """Computes textual section differences and XBRL fact variances between two filings."""
    try:
        return service.compare_filings(left_filing_id=left_id, right_filing_id=right_id)
    except FilingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{filing_id}",
    response_model=FilingDetailDTO,
    summary="Get filing details, document list, and sections",
)
async def get_filing_detail(
    company_id: str,
    filing_id: str,
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingDetailDTO:
    """Returns detailed filing record with attachment catalog and document sections."""
    try:
        return service.get_filing_detail(filing_id)
    except FilingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{filing_id}/documents",
    response_model=list[FilingDocumentDTO],
    summary="List all document exhibits in a filing",
)
async def get_filing_documents(
    company_id: str,
    filing_id: str,
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> list[FilingDocumentDTO]:
    """Returns list of all files, exhibits, and XBRL attachments in the filing."""
    try:
        return service.get_filing_documents(filing_id)
    except FilingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{filing_id}/content",
    response_model=FilingContentDTO,
    summary="Get safely sanitized document HTML and plain text",
)
async def get_filing_content(
    company_id: str,
    filing_id: str,
    document_id: Optional[str] = Query(None, description="Optional specific document ID"),
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingContentDTO:
    """Returns sanitized HTML and clean text suitable for secure viewing."""
    try:
        return service.get_filing_content(filing_id=filing_id, document_id=document_id)
    except (FilingNotFoundError, FilingDocumentNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{filing_id}/facts",
    response_model=XBRLFactsResponseDTO,
    summary="Get extracted XBRL financial facts",
)
async def get_filing_facts(
    company_id: str,
    filing_id: str,
    concept: Optional[str] = Query(None, description="Filter by concept name (e.g. Revenues)"),
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> XBRLFactsResponseDTO:
    """Returns normalized XBRL financial facts extracted from the filing."""
    try:
        return service.get_filing_facts(filing_id=filing_id, concept_filter=concept)
    except FilingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{filing_id}/sources",
    response_model=FilingSourceReferenceDTO,
    summary="Get official regulatory provenance reference",
)
async def get_filing_source(
    company_id: str,
    filing_id: str,
    service: CompanyFilingsService = Depends(get_filings_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FilingSourceReferenceDTO:
    """Returns official regulator link, content SHA-256 hash, and attribution."""
    try:
        return service.get_filing_source(filing_id)
    except FilingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
