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
    NewsCustomFeedLimitExceededError,
    NewsCustomFeedNotFoundError,
    NewsDigestNotFoundError,
    NewsEventNotFoundError,
    NewsFinancialEventNotFoundError,
    NewsMonitoringRuleInvalidError,
    NewsMonitoringRuleLimitExceededError,
    NewsMonitoringRuleNotFoundError,
    NewsQueryInvalidError,
    NewsSearchInvalidError,
    NewsStoryNotFoundError,
)
from atlas.news.repository import NewsFeedQuery
from atlas.news.schemas import (
    # Stage 103 Monitoring, Custom Feeds, Alerts & Digests
    CreateCustomNewsFeedDTO,
    CreateNewsDigestSubscriptionDTO,
    CreateNewsMonitoringRuleDTO,
    CustomNewsFeedDTO,
    EntitySentimentAggregateDTO,
    EventSentimentProfileDTO,
    FinancialEventTypeDefinitionDTO,
    MarketReactionRequestDTO,
    MonitoringHealthStatusDTO,
    NewsAlertFeedResponseDTO,
    NewsArticleDTO,
    NewsCoverageResponseDTO,
    NewsDigestRunDTO,
    NewsDigestSubscriptionDTO,
    NewsDiscoveryQueryDTO,
    NewsDiscoveryResponseDTO,
    NewsEntityRelevanceDTO,
    NewsEventEvidenceDTO,
    NewsEventFeedResponseDTO,
    NewsEventResponse,
    NewsFacetsResponseDTO,
    NewsFeedResponseDTO,
    NewsFinancialEventDTO,
    NewsFreshnessResponseDTO,
    NewsIngestionRequestDTO,
    NewsIngestionResponseDTO,
    NewsMonitoringRuleDTO,
    NewsPublisherDTO,
    NewsRulePreviewRequestDTO,
    NewsRulePreviewResponseDTO,
    NewsRuleValidationRequestDTO,
    NewsRuleValidationResponseDTO,
    NewsSearchSuggestionDTO,
    NewsSentimentAnnotationDTO,
    NewsSourceDTO,
    NewsStoryFeedResponseDTO,
    NewsStoryThreadDTO,
    NewsTimelineRequestDTO,
    NewsTimelineResponseDTO,
    NewsTopicDTO,
    ObservedNewsMarketContextDTO,
    SentimentEvaluationResultDTO,
    SentimentTimelineResponseDTO,
    StorySentimentProfileDTO,
    UpdateCustomNewsFeedDTO,
    UpdateNewsDigestSubscriptionDTO,
    UpdateNewsMonitoringRuleDTO,
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
# Stage 100 Discovery, Facets, Timelines & Topics Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/api/v1/news/discover",
    response_model=NewsDiscoveryResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Advanced multi-dimensional news discovery, search, and filtering",
)
def discover_news(
    query: NewsDiscoveryQueryDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.discover_news(query, is_entitled=True)
    except NewsSearchInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"News discovery failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="News discovery query failed")


@router.post(
    "/api/v1/news/facets",
    response_model=NewsFacetsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get multi-dimensional facet counts for news discovery query",
)
def get_news_facets(
    query: NewsDiscoveryQueryDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_facets(query, is_entitled=True)
    except Exception as e:
        logger.error(f"News facet calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Facet calculation failed")


@router.post(
    "/api/v1/news/timeline",
    response_model=NewsTimelineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Generate chronological news timeline with timezone-aware grouping",
)
def get_news_timeline(
    request: NewsTimelineRequestDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_timeline(request, is_entitled=True)
    except Exception as e:
        logger.error(f"News timeline generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Timeline generation failed")


@router.get(
    "/api/v1/news/topics",
    response_model=List[NewsTopicDTO],
    status_code=status.HTTP_200_OK,
    summary="List canonical financial news topics and taxonomy definitions",
)
def list_news_topics(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_topics()


@router.get(
    "/api/v1/news/topics/{topic_id}",
    response_model=NewsTopicDTO,
    status_code=status.HTTP_200_OK,
    summary="Get canonical financial news topic details",
)
def get_news_topic(
    topic_id: str = Path(..., description="Canonical topic slug (e.g. 'EARNINGS_RELEASES')"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_topic(topic_id)
    except NewsCategoryUnsupportedError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/suggestions",
    response_model=List[NewsSearchSuggestionDTO],
    status_code=status.HTTP_200_OK,
    summary="Get metadata-backed autocomplete suggestions for news search combobox",
)
def get_news_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Prefix search string"),
    limit: int = Query(8, ge=1, le=20, description="Max suggestions to return"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_suggestions(prefix=q, limit=limit)


# ---------------------------------------------------------------------------
# Stage 101 Story Intelligence Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/news/stories",
    response_model=NewsStoryFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get source-authorized canonical Story Thread feed",
)
def get_news_stories(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by story status (ACTIVE, QUIET, etc.)"),
    entity_id: Optional[str] = Query(None, description="Filter by primary or related canonical entity ID"),
    topic_id: Optional[str] = Query(None, description="Filter by canonical topic ID"),
    publisher_id: Optional[str] = Query(None, description="Filter by verified publisher ID"),
    q: Optional[str] = Query(None, description="Search query across story titles and member headlines"),
    start_date: Optional[datetime.datetime] = Query(None, description="Published on or after UTC datetime"),
    end_date: Optional[datetime.datetime] = Query(None, description="Published on or before UTC datetime"),
    limit: int = Query(30, ge=1, le=100, description="Page limit (default 30, max 100)"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_stories(
        status=status_filter,
        entity_id=entity_id,
        topic_id=topic_id,
        publisher_id=publisher_id,
        q=q,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/api/v1/news/stories/{story_id}",
    response_model=NewsStoryThreadDTO,
    status_code=status.HTTP_200_OK,
    summary="Get canonical Story Thread details",
)
def get_news_story(
    story_id: str = Path(..., description="Canonical Story Thread ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_story(story_id)
    except NewsStoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/stories/{story_id}/articles",
    response_model=List[NewsArticleDTO],
    status_code=status.HTTP_200_OK,
    summary="Get chronological member articles in Story Thread",
)
def get_news_story_articles(
    story_id: str = Path(..., description="Canonical Story Thread ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_story_articles(story_id)
    except NewsStoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/stories/{story_id}/events",
    response_model=List[NewsFinancialEventDTO],
    status_code=status.HTTP_200_OK,
    summary="Get linked verified financial events for Story Thread",
)
def get_news_story_events(
    story_id: str = Path(..., description="Canonical Story Thread ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_story_events(story_id)
    except NewsStoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 101 Financial Event Classification Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/news/events/types",
    response_model=List[FinancialEventTypeDefinitionDTO],
    status_code=status.HTTP_200_OK,
    summary="Get canonical financial event taxonomy and definitions",
)
def get_news_event_types(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_event_types()


@router.get(
    "/api/v1/news/events",
    response_model=NewsEventFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get source-evidenced financial event feed",
)
def get_news_events(
    event_type: Optional[str] = Query(None, description="Filter by canonical event type"),
    lifecycle_status: Optional[str] = Query(None, description="Filter by lifecycle status (PROPOSED, ANNOUNCED, COMPLETED, etc.)"),
    assertion_status: Optional[str] = Query(None, description="Filter by assertion status (OFFICIALLY_REPORTED, RUMORED, etc.)"),
    primary_entity_id: Optional[str] = Query(None, description="Filter by primary subject canonical entity ID"),
    related_entity_id: Optional[str] = Query(None, description="Filter by any participant entity ID"),
    story_id: Optional[str] = Query(None, description="Filter by associated Story Thread ID"),
    q: Optional[str] = Query(None, description="Search query across event titles and participants"),
    start_date: Optional[datetime.datetime] = Query(None, description="Event occurrence on or after UTC datetime"),
    end_date: Optional[datetime.datetime] = Query(None, description="Event occurrence on or before UTC datetime"),
    limit: int = Query(30, ge=1, le=100, description="Page limit (default 30, max 100)"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_events(
        event_type=event_type,
        lifecycle_status=lifecycle_status,
        assertion_status=assertion_status,
        primary_entity_id=primary_entity_id,
        related_entity_id=related_entity_id,
        story_id=story_id,
        q=q,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/api/v1/news/events/{event_id}",
    response_model=NewsFinancialEventDTO,
    status_code=status.HTTP_200_OK,
    summary="Get verified financial event details",
)
def get_news_event_by_id(
    event_id: str = Path(..., description="Canonical Financial Event ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_event(event_id)
    except NewsFinancialEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/events/{event_id}/evidence",
    response_model=List[NewsEventEvidenceDTO],
    status_code=status.HTTP_200_OK,
    summary="Get structured source evidence records for event",
)
def get_news_event_evidence(
    event_id: str = Path(..., description="Canonical Financial Event ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_event_evidence(event_id)
    except NewsFinancialEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/entities/{entity_id}/events",
    response_model=List[NewsFinancialEventDTO],
    status_code=status.HTTP_200_OK,
    summary="Get verified financial events associated with an entity",
)
def get_entity_events(
    entity_id: str = Path(..., description="Canonical entity ID (e.g. 'comp-aapl-001')"),
    limit: int = Query(20, ge=1, le=100, description="Max events to return"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_entity_events(entity_id=entity_id, limit=limit)



# ---------------------------------------------------------------------------
# Stage 102 Sentiment, Relevance & Market Context Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/api/v1/news/articles/{article_id}/sentiment",
    response_model=List[NewsSentimentAnnotationDTO],
    status_code=status.HTTP_200_OK,
    summary="Get source-qualified article sentiment annotations",
)
def get_article_sentiment(
    article_id: str = Path(..., description="Canonical Article ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_article_sentiment(article_id, is_entitled=True)
    except NewsArticleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NewsArticleWithdrawnError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))


@router.get(
    "/api/v1/news/entities/{entity_id}/sentiment",
    response_model=EntitySentimentAggregateDTO,
    status_code=status.HTTP_200_OK,
    summary="Get target entity sentiment aggregate over evaluation window",
)
def get_entity_sentiment_aggregate(
    entity_id: str = Path(..., description="Canonical entity ID (e.g. 'comp-aapl-001')"),
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    sources: Optional[List[str]] = Query(None, description="Optional publisher or provider filters"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_entity_sentiment_aggregate(entity_id=entity_id, days=days, sources=sources)


@router.get(
    "/api/v1/news/entities/{entity_id}/sentiment/timeline",
    response_model=SentimentTimelineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get historical sentiment observations bucketed by interval",
)
def get_entity_sentiment_timeline(
    entity_id: str = Path(..., description="Canonical entity ID (e.g. 'comp-aapl-001')"),
    interval: str = Query("DAY", pattern="^(DAY|WEEK|MONTH)$", description="Bucketing interval"),
    days: int = Query(30, ge=1, le=365, description="Lookback window in days"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_entity_sentiment_timeline(entity_id=entity_id, interval=interval, days=days)


@router.get(
    "/api/v1/news/stories/{story_id}/sentiment",
    response_model=StorySentimentProfileDTO,
    status_code=status.HTTP_200_OK,
    summary="Get story thread sentiment distribution profile",
)
def get_story_sentiment(
    story_id: str = Path(..., description="Canonical Story Thread ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_story_sentiment(story_id)
    except NewsStoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/events/{event_id}/sentiment",
    response_model=EventSentimentProfileDTO,
    status_code=status.HTTP_200_OK,
    summary="Get event sentiment distribution profile",
)
def get_event_sentiment(
    event_id: str = Path(..., description="Canonical Financial Event ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_event_sentiment(event_id)
    except NewsFinancialEventNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/entities/{entity_id}/relevance",
    response_model=List[NewsEntityRelevanceDTO],
    status_code=status.HTTP_200_OK,
    summary="Get entity relevance records for an article or entity target",
)
def get_entity_relevance(
    entity_id: str = Path(..., description="Canonical Article ID or Entity ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_entity_relevance(entity_id)
    except NewsArticleNotFoundError:
        return []


@router.get(
    "/api/v1/news/articles/{article_id}/relevance",
    response_model=List[NewsEntityRelevanceDTO],
    status_code=status.HTTP_200_OK,
    summary="Get entity relevance records for an article",
)
def get_article_relevance(
    article_id: str = Path(..., description="Canonical Article ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_entity_relevance(article_id)
    except NewsArticleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/analytics/methodologies",
    status_code=status.HTTP_200_OK,
    summary="Get approved sentiment taxonomy and methodology specifications",
)
def get_sentiment_methodologies(
    user: AuthPrincipal = Depends(get_current_user),
):
    return {
        "taxonomy_version": "v1.0.0-financial",
        "classifier_version": "rules-fin-2026.1",
        "sentiment_labels": [
            {"code": "POSITIVE", "description": "Favorable evaluative framing toward target"},
            {"code": "NEGATIVE", "description": "Unfavorable evaluative framing toward target"},
            {"code": "NEUTRAL", "description": "Objective descriptive factual reporting"},
            {"code": "MIXED", "description": "Material conflicting favorable and unfavorable views"},
            {"code": "INSUFFICIENT_EVIDENCE", "description": "Text insufficient for defensible classification"},
            {"code": "NOT_APPLICABLE", "description": "Target not meaningfully discussed"},
        ],
        "financial_aspects": [
            "EARNINGS_PERFORMANCE", "REVENUE_GROWTH", "PROFITABILITY",
            "CASH_FLOW", "BALANCE_SHEET", "DEBT_FINANCING", "CORPORATE_GOVERNANCE",
            "REGULATORY_EXPOSURE", "PRODUCT_DEVELOPMENT", "OPERATIONAL_PERFORMANCE",
            "MANAGEMENT", "CORPORATE_TRANSACTION", "GENERAL"
        ],
        "relevance_classes": [
            "PRIMARY_SUBJECT", "DIRECT_PARTICIPANT", "VERIFIED_MENTION",
            "VERIFIED_RELATED_ENTITY", "CONTEXTUAL_MARKET_REFERENCE", "INSUFFICIENT_EVIDENCE"
        ],
        "noncausal_policy": "Market reaction measurements are descriptive historical observations. Correlation does not imply causation.",
    }


@router.post(
    "/api/v1/news/analytics/market-reaction",
    response_model=ObservedNewsMarketContextDTO,
    status_code=status.HTTP_200_OK,
    summary="Calculate descriptive observed market reaction around publication window",
)
def post_market_reaction(
    req: MarketReactionRequestDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_observed_market_reaction(req)


@router.get(
    "/api/v1/news/analytics/evaluation",
    response_model=SentimentEvaluationResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Run and inspect golden corpus evaluation metrics (Macro-F1, Precision, Recall)",
)
def get_sentiment_evaluation(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_sentiment_evaluation()


# ---------------------------------------------------------------------------
# Stage 103 Personalized News Monitoring, Alerts, Custom Feeds & Digests
# ---------------------------------------------------------------------------

@router.get(
    "/api/v1/news/monitoring/rules",
    response_model=List[NewsMonitoringRuleDTO],
    status_code=status.HTTP_200_OK,
    summary="List authenticated user's news monitoring rules",
)
def list_monitoring_rules(
    active_only: bool = Query(False, description="Filter for active rules only"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    return service.list_monitoring_rules(owner_user_id=user_id, active_only=active_only)


@router.post(
    "/api/v1/news/monitoring/rules",
    response_model=NewsMonitoringRuleDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new news monitoring rule",
)
def create_monitoring_rule(
    dto: CreateNewsMonitoringRuleDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.create_monitoring_rule(dto, owner_user_id=user_id)
    except NewsMonitoringRuleInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NewsMonitoringRuleLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create monitoring rule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/api/v1/news/monitoring/rules/{rule_id}",
    response_model=NewsMonitoringRuleDTO,
    status_code=status.HTTP_200_OK,
    summary="Get single news monitoring rule detail",
)
def get_monitoring_rule(
    rule_id: str = Path(..., description="Rule ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.get_monitoring_rule(rule_id, owner_user_id=user_id)
    except NewsMonitoringRuleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/api/v1/news/monitoring/rules/{rule_id}",
    response_model=NewsMonitoringRuleDTO,
    status_code=status.HTTP_200_OK,
    summary="Update or toggle an existing news monitoring rule",
)
def update_monitoring_rule(
    rule_id: str = Path(..., description="Rule ID"),
    dto: UpdateNewsMonitoringRuleDTO = ...,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.update_monitoring_rule(rule_id, owner_user_id=user_id, dto=dto)
    except NewsMonitoringRuleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/api/v1/news/monitoring/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete a news monitoring rule",
)
def delete_monitoring_rule(
    rule_id: str = Path(..., description="Rule ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        service.delete_monitoring_rule(rule_id, owner_user_id=user_id)
        return None
    except NewsMonitoringRuleNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/api/v1/news/monitoring/rules/validate",
    response_model=NewsRuleValidationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Validate proposed monitoring rule without saving",
)
def validate_monitoring_rule(
    req: NewsRuleValidationRequestDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.validate_monitoring_rule(req)


@router.post(
    "/api/v1/news/monitoring/rules/preview",
    response_model=NewsRulePreviewResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Preview historical matches for a proposed rule without notifications",
)
def preview_monitoring_rule(
    req: NewsRulePreviewRequestDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.preview_monitoring_rule(req)


@router.get(
    "/api/v1/news/monitoring/alerts",
    response_model=NewsAlertFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get alert match and audit history for current user",
)
def list_alert_matches(
    limit: int = Query(50, ge=1, le=200, description="Max alerts to return"),
    rule_id: Optional[str] = Query(None, description="Filter alerts by rule ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by match status"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    return service.list_alert_matches(
        owner_user_id=user_id,
        limit=limit,
        rule_id=rule_id,
        status=status_filter,
    )


@router.get(
    "/api/v1/news/monitoring/status",
    response_model=MonitoringHealthStatusDTO,
    status_code=status.HTTP_200_OK,
    summary="Get news monitoring pipeline health, lag, and delivery metrics",
)
def get_monitoring_status(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.get_monitoring_health()


@router.get(
    "/api/v1/news/custom-feeds",
    response_model=List[CustomNewsFeedDTO],
    status_code=status.HTTP_200_OK,
    summary="List saved custom news feeds for user",
)
def list_custom_feeds(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    return service.list_custom_feeds(owner_user_id=user_id)


@router.post(
    "/api/v1/news/custom-feeds",
    response_model=CustomNewsFeedDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new saved custom news feed",
)
def create_custom_feed(
    dto: CreateCustomNewsFeedDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.create_custom_feed(dto, owner_user_id=user_id)
    except NewsMonitoringRuleInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NewsCustomFeedLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))


@router.get(
    "/api/v1/news/custom-feeds/{feed_id}",
    response_model=CustomNewsFeedDTO,
    status_code=status.HTTP_200_OK,
    summary="Get single custom news feed definition",
)
def get_custom_feed(
    feed_id: str = Path(..., description="Feed ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.get_custom_feed(feed_id, owner_user_id=user_id)
    except NewsCustomFeedNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/api/v1/news/custom-feeds/{feed_id}",
    response_model=CustomNewsFeedDTO,
    status_code=status.HTTP_200_OK,
    summary="Update saved custom news feed configuration",
)
def update_custom_feed(
    feed_id: str = Path(..., description="Feed ID"),
    dto: UpdateCustomNewsFeedDTO = ...,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.update_custom_feed(feed_id, owner_user_id=user_id, dto=dto)
    except NewsCustomFeedNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/api/v1/news/custom-feeds/{feed_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a saved custom news feed",
)
def delete_custom_feed(
    feed_id: str = Path(..., description="Feed ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        service.delete_custom_feed(feed_id, owner_user_id=user_id)
        return None
    except NewsCustomFeedNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/custom-feeds/{feed_id}/articles",
    response_model=NewsFeedResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Execute canonical search and retrieve articles matching custom feed",
)
def get_custom_feed_articles(
    feed_id: str = Path(..., description="Feed ID"),
    limit: int = Query(30, ge=1, le=100),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.execute_custom_feed(feed_id, owner_user_id=user_id, limit=limit)
    except NewsCustomFeedNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/digests",
    response_model=List[NewsDigestSubscriptionDTO],
    status_code=status.HTTP_200_OK,
    summary="List news digest subscriptions for user",
)
def list_digests(
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    return service.list_digest_subscriptions(owner_user_id=user_id)


@router.post(
    "/api/v1/news/digests",
    response_model=NewsDigestSubscriptionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scheduled news digest subscription",
)
def create_digest(
    dto: CreateNewsDigestSubscriptionDTO,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.create_digest_subscription(dto, owner_user_id=user_id)
    except NewsMonitoringRuleInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/api/v1/news/digests/{digest_id}",
    response_model=NewsDigestSubscriptionDTO,
    status_code=status.HTTP_200_OK,
    summary="Get single news digest subscription",
)
def get_digest(
    digest_id: str = Path(..., description="Digest ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.get_digest_subscription(digest_id, owner_user_id=user_id)
    except NewsDigestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/api/v1/news/digests/{digest_id}",
    response_model=NewsDigestSubscriptionDTO,
    status_code=status.HTTP_200_OK,
    summary="Update digest configuration or cadence",
)
def update_digest(
    digest_id: str = Path(..., description="Digest ID"),
    dto: UpdateNewsDigestSubscriptionDTO = ...,
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.update_digest_subscription(digest_id, owner_user_id=user_id, dto=dto)
    except NewsDigestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/api/v1/news/digests/{digest_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a news digest subscription",
)
def delete_digest(
    digest_id: str = Path(..., description="Digest ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        service.delete_digest_subscription(digest_id, owner_user_id=user_id)
        return None
    except NewsDigestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/digests/{digest_id}/preview",
    response_model=NewsDigestRunDTO,
    status_code=status.HTTP_200_OK,
    summary="Preview currently eligible content for a digest without running dispatch",
)
def preview_digest(
    digest_id: str = Path(..., description="Digest ID"),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.preview_digest(digest_id, owner_user_id=user_id)
    except NewsDigestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/api/v1/news/digests/{digest_id}/trigger",
    response_model=NewsDigestRunDTO,
    status_code=status.HTTP_200_OK,
    summary="Trigger on-demand execution and dispatch for a news digest",
)
def trigger_digest(
    digest_id: str = Path(..., description="Digest ID"),
    session: Session = Depends(get_db_session),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    try:
        return service.generate_and_dispatch_digest(digest_id, owner_user_id=user_id, session=session)
    except NewsDigestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/api/v1/news/digests/{digest_id}/history",
    response_model=List[NewsDigestRunDTO],
    status_code=status.HTTP_200_OK,
    summary="List past digest runs and dispatch history",
)
def list_digest_history(
    digest_id: str = Path(..., description="Digest ID"),
    limit: int = Query(20, ge=1, le=100),
    service: NewsService = Depends(get_news_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = getattr(user, "sub", None) or getattr(user, "user_id", None) or "usr-dev-atlas"
    return service.list_digest_runs(owner_user_id=user_id, digest_id=digest_id, limit=limit)


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
