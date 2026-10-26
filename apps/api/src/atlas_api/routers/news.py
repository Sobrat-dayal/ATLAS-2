"""FastAPI Router for Institutional Financial News Platform (Stage 99).

Endpoints:
- GET  /api/v1/news/feed
- GET  /api/v1/news/articles/{article_id}
- GET  /api/v1/news/articles/{article_id}/revisions
- GET  /api/v1/news/sources
- GET  /api/v1/news/publishers
- GET  /api/v1/news/categories
- GET  /api/v1/news/search
- GET  /api/v1/news/entities/{entity_id}
- GET  /api/v1/news/coverage
- GET  /api/v1/news/status
- POST /api/v1/news/ingest
- GET  /api/v1/news-events/{entity_id}  (Stage 20 / 36 legacy compatibility)
"""

import datetime
import logging
import uuid
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.news.errors import (
    NewsArticleNotFoundError,
    NewsArticleRestrictedError,
    NewsArticleWithdrawnError,
    NewsCategoryUnsupportedError,
    NewsEventNotFoundError,
    NewsQueryInvalidError,
    NewsSearchInvalidError,
)
from atlas.news.repository import NewsFeedQuery
from atlas.news.schemas import (
    NewsArticleDTO,
    NewsCoverageResponseDTO,
    NewsEventResponse,
    NewsFeedResponseDTO,
    NewsFreshnessResponseDTO,
    NewsIngestionRequestDTO,
    NewsIngestionResponseDTO,
    NewsPublisherDTO,
    NewsSourceDTO,
)
from atlas.news.service import (
    NewsEventService,
    NewsService,
    get_news_service,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["News"],
)


# ---------------------------------------------------------------------------
# Stage 99 News Platform Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/news/feed",
    response_model=NewsFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get source-qualified chronological news feed",
)
def get_news_feed(
    category: Optional[str] = Query(None, description="Filter by canonical news category"),
    source_id: Optional[str] = Query(None, description="Filter by authorized source provider ID"),
    publisher_id: Optional[str] = Query(None, description="Filter by verified publisher ID"),
    entity_id: Optional[str] = Query(None, description="Filter by company, instrument, or regulator ID/ticker"),
    geography: Optional[str] = Query(None, description="Filter by ISO country/region code"),
    q: Optional[str] = Query(None, description="Full-text headline/excerpt search query"),
    start_date: Optional[datetime.datetime] = Query(None, description="Published on or after UTC datetime"),
    end_date: Optional[datetime.datetime] = Query(None, description="Published on or before UTC datetime"),
    limit: int = Query(30, ge=1, le=100, description="Page limit (default 30, max 100)"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    query = NewsFeedQuery(
        category=category,
        source_id=source_id,
        publisher_id=publisher_id,
        entity_id=entity_id,
        geography=geography,
        q=q,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        cursor=cursor,
    )
    try:
        return service.get_feed(query, is_entitled=True)
    except NewsCategoryUnsupportedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NewsQueryInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch news feed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve news feed")


@router.get(
    "/api/v1/news/articles/{article_id}",
    response_model=NewsArticleDTO,
    status_code=status.HTTP_200_OK,
    summary="Get canonical article details",
)
def get_news_article(
    article_id: str = Path(..., description="Canonical article ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_article(article_id, is_entitled=True)
    except NewsArticleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NewsArticleWithdrawnError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))
    except NewsArticleRestrictedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching article '{article_id}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve article")


@router.get(
    "/api/v1/news/articles/{article_id}/revisions",
    status_code=status.HTTP_200_OK,
    summary="Get article correction and revision audit history",
)
def get_article_revisions(
    article_id: str = Path(..., description="Canonical article ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_article_revisions(article_id)
    except NewsArticleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching article revisions '{article_id}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve revisions")


@router.get(
    "/api/v1/news/sources",
    response_model=List[NewsSourceDTO],
    status_code=status.HTTP_200_OK,
    summary="List authorized news sources and provider capabilities",
)
def list_news_sources(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_sources()


@router.get(
    "/api/v1/news/publishers",
    response_model=List[NewsPublisherDTO],
    status_code=status.HTTP_200_OK,
    summary="List verified financial publishers in the canonical registry",
)
def list_news_publishers(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_publishers()


@router.get(
    "/api/v1/news/categories",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    summary="List supported canonical news taxonomy categories",
)
def list_news_categories(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_categories()


@router.get(
    "/api/v1/news/search",
    response_model=NewsFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Search authorized news headlines and excerpts",
)
def search_news(
    q: str = Query(..., min_length=1, max_length=200, description="Keyword search string"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    limit: int = Query(30, ge=1, le=100, description="Max results"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.search_news(q=q, limit=limit, category=category, is_entitled=True)
    except NewsSearchInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Search failed for query '{q}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed")


@router.get(
    "/api/v1/news/entities/{entity_id}",
    response_model=NewsFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get news linked to a specific company or instrument",
)
def get_entity_news(
    entity_id: str = Path(..., description="Canonical Company or Instrument entity ID or symbol"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_entity_news(entity_id=entity_id, limit=limit, is_entitled=True)


@router.get(
    "/api/v1/news/coverage",
    response_model=NewsCoverageResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get news coverage, provider counts, and geographic reach",
)
def get_news_coverage(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_coverage()


@router.get(
    "/api/v1/news/status",
    response_model=NewsFreshnessResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get source freshness, latency class, and health summary",
)
def get_news_status(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_freshness_status()


@router.post(
    "/api/v1/news/ingest",
    response_model=NewsIngestionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Ingest batch of source news articles (protected worker/admin endpoint)",
)
def ingest_news(
    request: NewsIngestionRequestDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.ingest_articles(request)
    except Exception as e:
        logger.error(f"Ingestion batch failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion error: {e}")


# ---------------------------------------------------------------------------
# Stage 20 / Stage 36 Legacy Compatibility Endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/news-events/{entity_id}",
    response_model=NewsEventResponse,
    status_code=status.HTTP_200_OK,
    tags=["News Events"],
)
def get_news_event(
    entity_id: uuid.UUID = Path(..., description="The news event UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user),
):
    event_service = NewsEventService(session)
    try:
        return event_service.get_news_event(entity_id)
    except NewsEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
