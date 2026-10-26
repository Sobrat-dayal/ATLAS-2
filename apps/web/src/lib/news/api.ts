/**
 * Authenticated REST API Client for ATLAS Institutional Financial News (Stage 99).
 */

import {
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
  NewsAlertMatchDTO,
  NewsArticleDTO,
  NewsCoverageResponseDTO,
  NewsDigestRunDTO,
  NewsDigestSubscriptionDTO,
  NewsEntityRelevanceDTO,
  NewsFeedQueryParams,
  NewsFeedResponseDTO,
  NewsFinancialEventDTO,
  NewsFreshnessResponseDTO,
  NewsMonitoringRuleDTO,
  NewsPublisherDTO,
  NewsRulePreviewRequestDTO,
  NewsRulePreviewResponseDTO,
  NewsRuleValidationRequestDTO,
  NewsRuleValidationResponseDTO,
  NewsSentimentAnnotationDTO,
  NewsSourceDTO,
  ObservedNewsMarketContextDTO,
  SentimentEvaluationResultDTO,
  SentimentTimelineResponseDTO,
  StorySentimentProfileDTO,
  UpdateCustomNewsFeedDTO,
  UpdateNewsDigestSubscriptionDTO,
  UpdateNewsMonitoringRuleDTO,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
}

export class NewsApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "NEWS_API_ERROR") {
    super(message);
    this.name = "NewsApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    let errorCode = "UNKNOWN_NEWS_ERROR";
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Fallback to HTTP text
    }
    throw new NewsApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function getNewsFeed(params?: NewsFeedQueryParams): Promise<NewsFeedResponseDTO> {
  const url = new URL("/api/v1/news/feed", getBaseApiUrl());
  if (params) {
    if (params.category) url.searchParams.set("category", params.category);
    if (params.source_id) url.searchParams.set("source_id", params.source_id);
    if (params.publisher_id) url.searchParams.set("publisher_id", params.publisher_id);
    if (params.entity_id) url.searchParams.set("entity_id", params.entity_id);
    if (params.geography) url.searchParams.set("geography", params.geography);
    if (params.q) url.searchParams.set("q", params.q);
    if (params.start_date) url.searchParams.set("start_date", params.start_date);
    if (params.end_date) url.searchParams.set("end_date", params.end_date);
    if (params.limit) url.searchParams.set("limit", String(params.limit));
    if (params.cursor) url.searchParams.set("cursor", params.cursor);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getNewsArticle(articleId: string): Promise<NewsArticleDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/articles/${encodeURIComponent(articleId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsArticleDTO>(res);
}

export async function getNewsSources(): Promise<NewsSourceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/sources`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsSourceDTO[]>(res);
}

export async function getNewsPublishers(): Promise<NewsPublisherDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/publishers`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsPublisherDTO[]>(res);
}

export async function getNewsCategories(): Promise<string[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/categories`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<string[]>(res);
}

export async function searchNews(
  q: string,
  category?: string,
  limit: number = 30
): Promise<NewsFeedResponseDTO> {
  const url = new URL("/api/v1/news/search", getBaseApiUrl());
  url.searchParams.set("q", q);
  if (category) url.searchParams.set("category", category);
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getEntityNews(
  entityId: string,
  limit: number = 20
): Promise<NewsFeedResponseDTO> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getNewsCoverage(): Promise<NewsCoverageResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsCoverageResponseDTO>(res);
}

export async function getNewsStatus(): Promise<NewsFreshnessResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/status`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFreshnessResponseDTO>(res);
}

// ---------------------------------------------------------------------------
// Stage 100 Discovery, Facets, and Timeline Endpoints
// ---------------------------------------------------------------------------

export async function discoverNews(
  query: import("./types").NewsDiscoveryQueryDTO
): Promise<import("./types").NewsDiscoveryResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/discover`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(query),
  });
  return handleResponse<import("./types").NewsDiscoveryResponseDTO>(res);
}

export async function getNewsFacets(
  query: import("./types").NewsDiscoveryQueryDTO
): Promise<import("./types").NewsFacetsResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/facets`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(query),
  });
  return handleResponse<import("./types").NewsFacetsResponseDTO>(res);
}

export async function getNewsTimeline(
  request: import("./types").NewsTimelineRequestDTO
): Promise<import("./types").NewsTimelineResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/timeline`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  return handleResponse<import("./types").NewsTimelineResponseDTO>(res);
}

export async function getNewsTopics(): Promise<import("./types").NewsTopicDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/topics`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsTopicDTO[]>(res);
}

export async function getNewsTopic(
  topicId: string
): Promise<import("./types").NewsTopicDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/topics/${encodeURIComponent(topicId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsTopicDTO>(res);
}

export async function getNewsSuggestions(
  q: string,
  limit: number = 8
): Promise<import("./types").NewsSearchSuggestionDTO[]> {
  const url = new URL("/api/v1/news/suggestions", getBaseApiUrl());
  url.searchParams.set("q", q);
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsSearchSuggestionDTO[]>(res);
}

// ---------------------------------------------------------------------------
// Stage 101 Story Intelligence & Financial Event API Client Functions
// ---------------------------------------------------------------------------

export interface NewsStoryQueryParams {
  status?: string;
  entity_id?: string;
  topic_id?: string;
  publisher_id?: string;
  q?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  cursor?: string;
}

export async function getNewsStories(
  params?: NewsStoryQueryParams
): Promise<import("./types").NewsStoryFeedResponseDTO> {
  const url = new URL("/api/v1/news/stories", getBaseApiUrl());
  if (params) {
    if (params.status) url.searchParams.set("status", params.status);
    if (params.entity_id) url.searchParams.set("entity_id", params.entity_id);
    if (params.topic_id) url.searchParams.set("topic_id", params.topic_id);
    if (params.publisher_id) url.searchParams.set("publisher_id", params.publisher_id);
    if (params.q) url.searchParams.set("q", params.q);
    if (params.start_date) url.searchParams.set("start_date", params.start_date);
    if (params.end_date) url.searchParams.set("end_date", params.end_date);
    if (params.limit) url.searchParams.set("limit", String(params.limit));
    if (params.cursor) url.searchParams.set("cursor", params.cursor);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsStoryFeedResponseDTO>(res);
}

export async function getNewsStory(
  storyId: string
): Promise<import("./types").NewsStoryThreadDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/stories/${encodeURIComponent(storyId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsStoryThreadDTO>(res);
}

export async function getNewsStoryArticles(
  storyId: string
): Promise<import("./types").NewsArticleDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/stories/${encodeURIComponent(storyId)}/articles`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsArticleDTO[]>(res);
}

export async function getNewsStoryEvents(
  storyId: string
): Promise<import("./types").NewsFinancialEventDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/stories/${encodeURIComponent(storyId)}/events`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsFinancialEventDTO[]>(res);
}

export interface NewsEventQueryParams {
  event_type?: string;
  lifecycle_status?: string;
  assertion_status?: string;
  primary_entity_id?: string;
  related_entity_id?: string;
  story_id?: string;
  q?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  cursor?: string;
}

export async function getNewsEvents(
  params?: NewsEventQueryParams
): Promise<import("./types").NewsEventFeedResponseDTO> {
  const url = new URL("/api/v1/news/events", getBaseApiUrl());
  if (params) {
    if (params.event_type) url.searchParams.set("event_type", params.event_type);
    if (params.lifecycle_status) url.searchParams.set("lifecycle_status", params.lifecycle_status);
    if (params.assertion_status) url.searchParams.set("assertion_status", params.assertion_status);
    if (params.primary_entity_id) url.searchParams.set("primary_entity_id", params.primary_entity_id);
    if (params.related_entity_id) url.searchParams.set("related_entity_id", params.related_entity_id);
    if (params.story_id) url.searchParams.set("story_id", params.story_id);
    if (params.q) url.searchParams.set("q", params.q);
    if (params.start_date) url.searchParams.set("start_date", params.start_date);
    if (params.end_date) url.searchParams.set("end_date", params.end_date);
    if (params.limit) url.searchParams.set("limit", String(params.limit));
    if (params.cursor) url.searchParams.set("cursor", params.cursor);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsEventFeedResponseDTO>(res);
}

export async function getNewsEvent(
  eventId: string
): Promise<import("./types").NewsFinancialEventDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/events/${encodeURIComponent(eventId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsFinancialEventDTO>(res);
}

export async function getNewsEventEvidence(
  eventId: string
): Promise<import("./types").NewsEventEvidenceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/events/${encodeURIComponent(eventId)}/evidence`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").NewsEventEvidenceDTO[]>(res);
}

export async function getNewsEventTypes(): Promise<
  import("./types").FinancialEventTypeDefinitionDTO[]
> {
  const url = `${getBaseApiUrl()}/api/v1/news/events/types`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<import("./types").FinancialEventTypeDefinitionDTO[]>(res);
}

export async function getEntityEvents(
  entityId: string,
  limit: number = 20
): Promise<NewsFinancialEventDTO[]> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}/events`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFinancialEventDTO[]>(res);
}

// =========================================================================
// STAGE 102: Financial Sentiment, Relevance & Market Reaction Client
// =========================================================================

export async function getArticleSentiment(
  articleId: string
): Promise<NewsSentimentAnnotationDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/articles/${encodeURIComponent(articleId)}/sentiment`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsSentimentAnnotationDTO[]>(res);
}

export async function getEntitySentiment(
  entityId: string,
  days: number = 30
): Promise<EntitySentimentAggregateDTO> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}/sentiment`,
    getBaseApiUrl()
  );
  url.searchParams.set("days", String(days));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EntitySentimentAggregateDTO>(res);
}

export async function getEntitySentimentTimeline(
  entityId: string,
  interval: string = "DAY",
  days: number = 30
): Promise<SentimentTimelineResponseDTO> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}/sentiment/timeline`,
    getBaseApiUrl()
  );
  url.searchParams.set("interval", interval);
  url.searchParams.set("days", String(days));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<SentimentTimelineResponseDTO>(res);
}

export async function getStorySentiment(
  storyId: string,
  targetEntityId?: string
): Promise<StorySentimentProfileDTO> {
  const url = new URL(
    `/api/v1/news/stories/${encodeURIComponent(storyId)}/sentiment`,
    getBaseApiUrl()
  );
  if (targetEntityId) {
    url.searchParams.set("target_entity_id", targetEntityId);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<StorySentimentProfileDTO>(res);
}

export async function getEventSentiment(
  eventId: string,
  targetEntityId?: string
): Promise<EventSentimentProfileDTO> {
  const url = new URL(
    `/api/v1/news/events/${encodeURIComponent(eventId)}/sentiment`,
    getBaseApiUrl()
  );
  if (targetEntityId) {
    url.searchParams.set("target_entity_id", targetEntityId);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<EventSentimentProfileDTO>(res);
}

export async function getEntityRelevance(
  entityId: string,
  limit: number = 50
): Promise<NewsEntityRelevanceDTO[]> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}/relevance`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsEntityRelevanceDTO[]>(res);
}

export async function getArticleRelevance(
  articleId: string
): Promise<NewsEntityRelevanceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/articles/${encodeURIComponent(articleId)}/relevance`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsEntityRelevanceDTO[]>(res);
}

export async function getNewsMethodologies(): Promise<Record<string, unknown>> {
  const url = `${getBaseApiUrl()}/api/v1/news/analytics/methodologies`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<Record<string, unknown>>(res);
}

export async function getObservedMarketReaction(
  req: MarketReactionRequestDTO
): Promise<ObservedNewsMarketContextDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/analytics/market-reaction`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(req),
  });
  return handleResponse<ObservedNewsMarketContextDTO>(res);
}

export async function getSentimentEvaluation(): Promise<SentimentEvaluationResultDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/analytics/evaluation`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<SentimentEvaluationResultDTO>(res);
}

// ============================================================================
// Stage 103: Monitoring Rules, Custom Feeds, Alerts & Digests
// ============================================================================

export async function getMonitoringRules(params?: {
  is_active?: boolean;
  rule_type?: string;
}): Promise<NewsMonitoringRuleDTO[]> {
  const url = new URL("/api/v1/news/monitoring/rules", getBaseApiUrl());
  if (params?.is_active !== undefined) {
    url.searchParams.set("is_active", String(params.is_active));
  }
  if (params?.rule_type) {
    url.searchParams.set("rule_type", params.rule_type);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsMonitoringRuleDTO[]>(res);
}

export async function getMonitoringRule(
  ruleId: string
): Promise<NewsMonitoringRuleDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules/${encodeURIComponent(ruleId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsMonitoringRuleDTO>(res);
}

export async function createMonitoringRule(
  dto: CreateNewsMonitoringRuleDTO
): Promise<NewsMonitoringRuleDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<NewsMonitoringRuleDTO>(res);
}

export async function updateMonitoringRule(
  ruleId: string,
  dto: UpdateNewsMonitoringRuleDTO
): Promise<NewsMonitoringRuleDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules/${encodeURIComponent(ruleId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<NewsMonitoringRuleDTO>(res);
}

export async function deleteMonitoringRule(ruleId: string): Promise<void> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules/${encodeURIComponent(ruleId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new NewsApiError(`HTTP ${res.status}: ${res.statusText}`, res.status);
  }
}

export async function validateMonitoringRule(
  req: NewsRuleValidationRequestDTO
): Promise<NewsRuleValidationResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules/validate`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(req),
  });
  return handleResponse<NewsRuleValidationResponseDTO>(res);
}

export async function previewMonitoringRule(
  req: NewsRulePreviewRequestDTO
): Promise<NewsRulePreviewResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/rules/preview`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(req),
  });
  return handleResponse<NewsRulePreviewResponseDTO>(res);
}

export async function getAlertMatches(params?: {
  rule_id?: string;
  match_status?: string;
  priority?: string;
  limit?: number;
  offset?: number;
}): Promise<NewsAlertFeedResponseDTO> {
  const url = new URL("/api/v1/news/monitoring/alerts", getBaseApiUrl());
  if (params?.rule_id) url.searchParams.set("rule_id", params.rule_id);
  if (params?.match_status) url.searchParams.set("match_status", params.match_status);
  if (params?.priority) url.searchParams.set("priority", params.priority);
  if (params?.limit) url.searchParams.set("limit", String(params.limit));
  if (params?.offset) url.searchParams.set("offset", String(params.offset));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsAlertFeedResponseDTO>(res);
}

export async function getMonitoringHealth(): Promise<MonitoringHealthStatusDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/monitoring/status`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<MonitoringHealthStatusDTO>(res);
}

export async function getCustomFeeds(): Promise<CustomNewsFeedDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/custom-feeds`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<CustomNewsFeedDTO[]>(res);
}

export async function getCustomFeed(feedId: string): Promise<CustomNewsFeedDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/custom-feeds/${encodeURIComponent(feedId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<CustomNewsFeedDTO>(res);
}

export async function createCustomFeed(
  dto: CreateCustomNewsFeedDTO
): Promise<CustomNewsFeedDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/custom-feeds`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<CustomNewsFeedDTO>(res);
}

export async function updateCustomFeed(
  feedId: string,
  dto: UpdateCustomNewsFeedDTO
): Promise<CustomNewsFeedDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/custom-feeds/${encodeURIComponent(feedId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<CustomNewsFeedDTO>(res);
}

export async function deleteCustomFeed(feedId: string): Promise<void> {
  const url = `${getBaseApiUrl()}/api/v1/news/custom-feeds/${encodeURIComponent(feedId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new NewsApiError(`HTTP ${res.status}: ${res.statusText}`, res.status);
  }
}

export async function executeCustomFeedArticles(
  feedId: string,
  limit: number = 20
): Promise<{ feed: CustomNewsFeedDTO; articles: NewsArticleDTO[]; total_count: number }> {
  const url = new URL(
    `/api/v1/news/custom-feeds/${encodeURIComponent(feedId)}/articles`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<{ feed: CustomNewsFeedDTO; articles: NewsArticleDTO[]; total_count: number }>(res);
}

export async function getDigests(): Promise<NewsDigestSubscriptionDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsDigestSubscriptionDTO[]>(res);
}

export async function getDigest(
  digestId: string
): Promise<NewsDigestSubscriptionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests/${encodeURIComponent(digestId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsDigestSubscriptionDTO>(res);
}

export async function createDigest(
  dto: CreateNewsDigestSubscriptionDTO
): Promise<NewsDigestSubscriptionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<NewsDigestSubscriptionDTO>(res);
}

export async function updateDigest(
  digestId: string,
  dto: UpdateNewsDigestSubscriptionDTO
): Promise<NewsDigestSubscriptionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests/${encodeURIComponent(digestId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(dto),
  });
  return handleResponse<NewsDigestSubscriptionDTO>(res);
}

export async function deleteDigest(digestId: string): Promise<void> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests/${encodeURIComponent(digestId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new NewsApiError(`HTTP ${res.status}: ${res.statusText}`, res.status);
  }
}

export async function previewDigest(
  digestId: string
): Promise<NewsDigestRunDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests/${encodeURIComponent(digestId)}/preview`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsDigestRunDTO>(res);
}

export async function triggerDigest(
  digestId: string
): Promise<NewsDigestRunDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/digests/${encodeURIComponent(digestId)}/trigger`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse<NewsDigestRunDTO>(res);
}

export async function getDigestHistory(
  digestId: string,
  limit: number = 20
): Promise<NewsDigestRunDTO[]> {
  const url = new URL(
    `/api/v1/news/digests/${encodeURIComponent(digestId)}/history`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsDigestRunDTO[]>(res);
}




