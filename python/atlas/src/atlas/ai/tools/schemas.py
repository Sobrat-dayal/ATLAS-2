"""Pydantic schemas for Stage 126: ATLAS AI Tool Gateway.

Defines validated request/response models for all 19 canonical read-only tools
and REST API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ---------------- Gateway API Schemas ----------------


class AiToolDescriptorResponse(BaseModel):
    """Public descriptor of a registered AI tool."""

    tool_id: str
    version: str
    category: str
    name: str
    description: str
    capability_scope: str
    approval_class: str
    provider_disclosure_policy: str
    parameters_schema: Dict[str, Any]
    returns_schema: Dict[str, Any]
    lifecycle_status: str
    timeout_seconds: float
    rate_limit_per_minute: int


class AiToolListResponse(BaseModel):
    """Response containing available authorized tools."""

    tools: List[AiToolDescriptorResponse]
    total: int


class AiToolCallResponse(BaseModel):
    """Response representing an executed or queued AI tool call."""

    id: str
    tool_id: str
    tool_version: str
    status: str
    arguments: Dict[str, Any]
    normalized_arguments_hash: str
    result: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    approval_class: str
    approval_request_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AiToolCallListResponse(BaseModel):
    """Response listing user tool calls."""

    calls: List[AiToolCallResponse]
    total: int


class AiToolPreferencesResponse(BaseModel):
    """User preferences for tool discovery, auto-approval, and permissions."""

    user_id: str
    enabled_tools: List[str]
    disabled_tools: List[str]
    auto_approve_read_only: bool
    require_approval_for_sensitive: bool
    updated_at: datetime


class AiToolPreferencesUpdateRequest(BaseModel):
    """Request to update user tool preferences."""

    enabled_tools: Optional[List[str]] = None
    disabled_tools: Optional[List[str]] = None
    auto_approve_read_only: Optional[bool] = None
    require_approval_for_sensitive: Optional[bool] = None


class AiToolApprovalResponse(BaseModel):
    """Response detailing a human confirmation approval request."""

    id: str
    tool_call_id: str
    user_id: str
    tool_id: str
    approval_class: str
    normalized_arguments_hash: str
    arguments_summary: Dict[str, Any]
    status: str
    expires_at: datetime
    consumed_at: Optional[datetime] = None
    decision_reason: Optional[str] = None
    created_at: datetime


class AiToolApprovalActionRequest(BaseModel):
    """Request to approve or deny an approval request."""

    decision_reason: Optional[str] = None


class AiToolExecuteRequest(BaseModel):
    """Request to directly dispatch an authorized tool call."""

    tool_id: str
    arguments: Dict[str, Any]
    generation_run_id: Optional[str] = None
    conversation_id: Optional[str] = None
    approval_request_id: Optional[str] = None


class AiToolExecuteResponse(BaseModel):
    """Response from executing a tool call."""

    tool_call_id: str
    tool_id: str
    success: bool
    data: Any
    source_manifest: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    as_of: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    truncated: bool = False
    content_hash: str = ""


# ---------------- Canonical Tool Arguments & Outputs ----------------


# 1. atlas.instrument.search
class InstrumentSearchInput(BaseModel):
    query: str = Field(
        ..., min_length=1, max_length=100, description="Company name, ticker, or search query"
    )
    exchange: Optional[str] = Field(
        None, max_length=20, description="Filter by exchange, e.g. NASDAQ, NYSE"
    )
    asset_class: Optional[str] = Field(
        None, max_length=30, description="Filter by asset class, e.g. Equity, ETF"
    )
    limit: int = Field(5, ge=1, le=20, description="Maximum results to return")


# 2. atlas.instrument.get
class InstrumentGetInput(BaseModel):
    instrument_id: str = Field(
        ..., min_length=1, max_length=64, description="Canonical Instrument ID or ticker"
    )


# 3. atlas.company.get
class CompanyGetInput(BaseModel):
    company_id: Optional[str] = Field(None, max_length=64, description="Canonical Company ID")
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")


# 4. atlas.company.financials
class CompanyFinancialsInput(BaseModel):
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")
    company_id: Optional[str] = Field(None, max_length=64, description="Canonical Company ID")
    statement_type: str = Field(
        "INCOME_STATEMENT", description="INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW"
    )
    period: str = Field("ANNUAL", description="ANNUAL or QUARTERLY")
    limit: int = Field(4, ge=1, le=10, description="Number of periods")


# 5. atlas.market.quote
class MarketQuoteInput(BaseModel):
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")
    instrument_id: Optional[str] = Field(None, max_length=64, description="Canonical Instrument ID")


# 6. atlas.market.history_summary
class MarketHistorySummaryInput(BaseModel):
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")
    instrument_id: Optional[str] = Field(None, max_length=64, description="Canonical Instrument ID")
    timeframe: str = Field("1Y", description="1M, 3M, 6M, 1Y, 5Y")
    interval: str = Field("1D", description="1D, 1W, 1M")


# 7. atlas.watchlist.list
class WatchlistListInput(BaseModel):
    limit: int = Field(10, ge=1, le=50, description="Maximum watchlists to list")


# 8. atlas.screener.get_definition
class ScreenerGetDefinitionInput(BaseModel):
    screener_id: str = Field(..., min_length=1, max_length=64, description="Canonical Screener ID")


# 9. atlas.economics.search_series
class EconomicsSearchSeriesInput(BaseModel):
    query: str = Field(
        ..., min_length=1, max_length=100, description="Search term for macro indicators"
    )
    country: Optional[str] = Field("US", max_length=10, description="Country code, e.g. US, EU, JP")
    limit: int = Field(5, ge=1, le=20, description="Maximum series to return")


# 10. atlas.economics.get_observations
class EconomicsGetObservationsInput(BaseModel):
    series_id: str = Field(
        ..., min_length=1, max_length=64, description="Economic series identifier, e.g. CPIAUCSL"
    )
    limit: int = Field(12, ge=1, le=60, description="Number of recent observations")


# 11. atlas.news.search_headlines
class NewsSearchHeadlinesInput(BaseModel):
    query: Optional[str] = Field(None, max_length=100, description="Keywords to filter headlines")
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")
    limit: int = Field(5, ge=1, le=20, description="Maximum headlines to retrieve")


# 12. atlas.research.list_metadata
class ResearchListMetadataInput(BaseModel):
    query: Optional[str] = Field(None, max_length=100, description="Keywords to search reports")
    symbol: Optional[str] = Field(None, max_length=20, description="Ticker symbol")
    limit: int = Field(5, ge=1, le=20, description="Maximum research reports")


# 13. atlas.portfolio.list
class PortfolioListInput(BaseModel):
    limit: int = Field(10, ge=1, le=50, description="Maximum portfolios to list")


# 14. atlas.portfolio.get_summary
class PortfolioGetSummaryInput(BaseModel):
    portfolio_id: str = Field(..., min_length=1, max_length=64, description="Target Portfolio ID")
    include_holdings: bool = Field(
        False, description="Whether to include position details (requires consent)"
    )


# 15. atlas.portfolio.get_performance
class PortfolioGetPerformanceInput(BaseModel):
    portfolio_id: str = Field(..., min_length=1, max_length=64, description="Target Portfolio ID")
    benchmark_id: Optional[str] = Field("SPY", max_length=20, description="Benchmark symbol")
    timeframe: str = Field("YTD", description="1M, 3M, 6M, 1Y, YTD, ALL")


# 16. atlas.risk.list_runs
class RiskListRunsInput(BaseModel):
    portfolio_id: Optional[str] = Field(None, max_length=64, description="Filter by Portfolio ID")
    limit: int = Field(5, ge=1, le=20, description="Maximum runs to retrieve")


# 17. atlas.risk.get_run_summary
class RiskGetRunSummaryInput(BaseModel):
    run_id: str = Field(..., min_length=1, max_length=64, description="Immutable Risk Run ID")


# 18. atlas.data.list_sources
class DataListSourcesInput(BaseModel):
    category: Optional[str] = Field(None, max_length=50, description="Filter by category")
    limit: int = Field(10, ge=1, le=50, description="Maximum data sources")


# 19. atlas.saved.list
class SavedListInput(BaseModel):
    resource_type: Optional[str] = Field(None, max_length=50, description="Filter by resource type")
    limit: int = Field(10, ge=1, le=50, description="Maximum saved items")


# 20. atlas.workspace.list
class WorkspaceListInput(BaseModel):
    limit: int = Field(10, ge=1, le=50, description="Maximum workspaces")


# --- Stage 127 Research & RAG Tools ---


# 21. atlas.research.search_documents
class ResearchSearchDocumentsInput(BaseModel):
    query: Optional[str] = Field(None, max_length=200, description="Optional text search")
    symbol: Optional[str] = Field(None, max_length=20, description="Target company ticker")
    document_type: Optional[str] = Field(
        None, max_length=50, description="e.g. '10-K', 'CAPEX_PLAN'"
    )
    historical_as_of: Optional[str] = Field(None, description="Point-in-time ISO timestamp")
    limit: int = Field(5, ge=1, le=20, description="Maximum documents")


# 22. atlas.research.search_passages
class ResearchSearchPassagesInput(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="Research search query")
    symbols: Optional[List[str]] = Field(None, description="Optional target symbols")
    historical_as_of: Optional[str] = Field(None, description="Point-in-time ISO timestamp")
    limit: int = Field(5, ge=1, le=15, description="Maximum passages to retrieve")


# 23. atlas.research.get_document_metadata
class ResearchGetDocumentMetadataInput(BaseModel):
    document_id: str = Field(..., min_length=1, max_length=64, description="Target document ID")


# 24. atlas.research.get_authorized_excerpt
class ResearchGetAuthorizedExcerptInput(BaseModel):
    document_id: str = Field(..., min_length=1, max_length=64, description="Target document ID")
    page_number: Optional[int] = Field(None, ge=1, description="Optional page number")


# 25. atlas.research.compare_documents
class ResearchCompareDocumentsInput(BaseModel):
    document_id_a: str = Field(..., min_length=1, max_length=64, description="First document ID")
    document_id_b: str = Field(..., min_length=1, max_length=64, description="Second document ID")
    aspects: Optional[List[str]] = Field(None, description="Comparison aspects, e.g. ['CAPEX']")


# 26. atlas.research.get_citation_source
class ResearchGetCitationSourceInput(BaseModel):
    citation_id: str = Field(..., min_length=1, max_length=64, description="Citation ID to resolve")
