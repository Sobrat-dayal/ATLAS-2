"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  discoverNews,
  getNewsCoverage,
  getNewsFacets,
  getNewsPublishers,
  getNewsSources,
  getNewsStatus,
  getNewsSuggestions,
  getNewsTimeline,
  getNewsTopics,
} from "@/lib/news/api";
import {
  NewsArticleDTO,
  NewsCoverageResponseDTO,
  NewsDatePreset,
  NewsDiscoveryMode,
  NewsDiscoveryQueryDTO,
  NewsFacetsResponseDTO,
  NewsFreshnessResponseDTO,
  NewsPublisherDTO,
  NewsSearchSuggestionDTO,
  NewsSortOrder,
  NewsSourceDTO,
  NewsTimelineInterval,
  NewsTimelineResponseDTO,
  NewsTopicDTO,
} from "@/lib/news/types";

export type NewsViewMode = "FEED" | "STORIES" | "EVENTS" | "TIMELINE";

export function useNewsDiscovery() {
  // Discovery and View Mode
  const [mode, setMode] = useState<NewsDiscoveryMode>("ALL");
  const [view, setView] = useState<NewsViewMode>("FEED");

  // Articles & Selection
  const [articles, setArticles] = useState<NewsArticleDTO[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<NewsArticleDTO | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [selectedIndustry, setSelectedIndustry] = useState<string>("");
  const [selectedSource, setSelectedSource] = useState<string>("");
  const [selectedPublisher, setSelectedPublisher] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedEntityId, setSelectedEntityId] = useState<string>("");
  const [datePreset, setDatePreset] = useState<NewsDatePreset>("ALL_TIME");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<NewsSortOrder>("PUBLISHED_DESC");

  // Timeline Configuration
  const [timelineInterval, setTimelineInterval] = useState<NewsTimelineInterval>("DAY");
  const [timelineTimezone, setTimelineTimezone] = useState<string>("UTC");
  const [timelineData, setTimelineData] = useState<NewsTimelineResponseDTO | null>(null);

  // Facets & Metadata Catalogs
  const [facets, setFacets] = useState<NewsFacetsResponseDTO | null>(null);
  const [topics, setTopics] = useState<NewsTopicDTO[]>([]);
  const [sources, setSources] = useState<NewsSourceDTO[]>([]);
  const [publishers, setPublishers] = useState<NewsPublisherDTO[]>([]);
  const [coverage, setCoverage] = useState<NewsCoverageResponseDTO | null>(null);
  const [status, setStatus] = useState<NewsFreshnessResponseDTO | null>(null);

  // Autocomplete Suggestions
  const [suggestions, setSuggestions] = useState<NewsSearchSuggestionDTO[]>([]);
  const [isSuggestionsLoading, setIsSuggestionsLoading] = useState<boolean>(false);
  const suggestionDebounceRef = useRef<NodeJS.Timeout | null>(null);

  // Loading & Error States
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load catalogs on mount
  useEffect(() => {
    let mounted = true;
    async function loadCatalogs() {
      try {
        const [srcs, pubs, tops, cov, stat] = await Promise.allSettled([
          getNewsSources(),
          getNewsPublishers(),
          getNewsTopics(),
          getNewsCoverage(),
          getNewsStatus(),
        ]);
        if (mounted) {
          if (srcs.status === "fulfilled") setSources(srcs.value);
          if (pubs.status === "fulfilled") setPublishers(pubs.value);
          if (tops.status === "fulfilled") setTopics(tops.value);
          if (cov.status === "fulfilled") setCoverage(cov.value);
          if (stat.status === "fulfilled") setStatus(stat.value);
        }
      } catch (err) {
        console.error("Failed to load initial news metadata:", err);
      }
    }
    loadCatalogs();
    return () => {
      mounted = false;
    };
  }, []);

  // Build current Discovery Query DTO
  const buildQuery = useCallback(
    (cursor?: string): NewsDiscoveryQueryDTO => {
      const q: NewsDiscoveryQueryDTO = {
        mode,
        sort_order: sortOrder,
        limit: 30,
        cursor,
      };

      if (searchQuery.trim()) q.query = searchQuery.trim();
      if (selectedTopic) q.topic_ids = [selectedTopic];
      if (selectedIndustry) q.industries = [selectedIndustry];
      if (selectedSource) q.source_ids = [selectedSource];
      if (selectedPublisher) q.publisher_ids = [selectedPublisher];
      if (selectedCountry) q.countries = [selectedCountry];
      if (selectedCategory) q.categories = [selectedCategory];
      if (selectedEntityId) q.entity_ids = [selectedEntityId];

      if (datePreset !== "ALL_TIME") {
        q.date_preset = datePreset;
      }
      if (datePreset === "CUSTOM") {
        if (startDate) q.start_date = startDate;
        if (endDate) q.end_date = endDate;
      }

      return q;
    },
    [
      mode,
      sortOrder,
      searchQuery,
      selectedTopic,
      selectedIndustry,
      selectedSource,
      selectedPublisher,
      selectedCountry,
      selectedCategory,
      selectedEntityId,
      datePreset,
      startDate,
      endDate,
    ]
  );

  // Fetch articles feed
  const fetchFeed = useCallback(
    async (cursor?: string, append: boolean = false) => {
      try {
        if (!append) setIsLoading(true);
        setError(null);

        const query = buildQuery(cursor);
        const [feedRes, facetRes] = await Promise.all([
          discoverNews(query),
          getNewsFacets(query),
        ]);

        if (append) {
          setArticles((prev) => [...prev, ...feedRes.articles]);
        } else {
          setArticles(feedRes.articles);
          if (feedRes.articles.length > 0) {
            setSelectedArticle((prev) =>
              prev ? feedRes.articles.find((a) => a.article_id === prev.article_id) || feedRes.articles[0] : feedRes.articles[0]
            );
          } else {
            setSelectedArticle(null);
          }
        }

        setTotalCount(feedRes.total_count);
        setNextCursor(feedRes.next_cursor || null);
        setHasMore(feedRes.has_more);
        setFacets(facetRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to discover financial news";
        setError(msg);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [buildQuery]
  );

  // Fetch timeline
  const fetchTimeline = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const query = buildQuery();
      const res = await getNewsTimeline({
        query,
        interval: timelineInterval,
        timezone: timelineTimezone,
      });
      setTimelineData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load news timeline";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [buildQuery, timelineInterval, timelineTimezone]);

  // Execute feed or timeline whenever filters change
  useEffect(() => {
    if (view === "TIMELINE") {
      fetchTimeline();
    } else {
      fetchFeed();
    }
  }, [view, fetchFeed, fetchTimeline]);

  // Autocomplete suggestions search with debounce
  const fetchSuggestions = useCallback((q: string) => {
    if (suggestionDebounceRef.current) {
      clearTimeout(suggestionDebounceRef.current);
    }
    const trimmed = q.trim();
    if (!trimmed || trimmed.length < 2) {
      setSuggestions([]);
      setIsSuggestionsLoading(false);
      return;
    }

    setIsSuggestionsLoading(true);
    suggestionDebounceRef.current = setTimeout(async () => {
      try {
        const res = await getNewsSuggestions(trimmed, 8);
        setSuggestions(res);
      } catch (err) {
        console.error("Failed to fetch news suggestions:", err);
        setSuggestions([]);
      } finally {
        setIsSuggestionsLoading(false);
      }
    }, 200);
  }, []);

  const loadNextPage = useCallback(() => {
    if (hasMore && nextCursor && !isLoading) {
      fetchFeed(nextCursor, true);
    }
  }, [hasMore, nextCursor, isLoading, fetchFeed]);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    if (view === "TIMELINE") {
      await fetchTimeline();
    } else {
      await fetchFeed();
    }
    try {
      const [cov, stat] = await Promise.all([getNewsCoverage(), getNewsStatus()]);
      setCoverage(cov);
      setStatus(stat);
    } catch {
      // Ignore background freshness errors
    }
  }, [view, fetchTimeline, fetchFeed]);

  const clearFilters = useCallback(() => {
    setSearchQuery("");
    setSelectedTopic("");
    setSelectedIndustry("");
    setSelectedSource("");
    setSelectedPublisher("");
    setSelectedCountry("");
    setSelectedCategory("");
    setSelectedEntityId("");
    setDatePreset("ALL_TIME");
    setStartDate("");
    setEndDate("");
    setSortOrder("PUBLISHED_DESC");
  }, []);

  const hasActiveFilters = Boolean(
    searchQuery ||
      selectedTopic ||
      selectedIndustry ||
      selectedSource ||
      selectedPublisher ||
      selectedCountry ||
      selectedCategory ||
      selectedEntityId ||
      datePreset !== "ALL_TIME" ||
      sortOrder !== "PUBLISHED_DESC"
  );

  return {
    mode,
    setMode,
    view,
    setView,
    articles,
    selectedArticle,
    setSelectedArticle,
    totalCount,
    hasMore,
    isLoading,
    isRefreshing,
    error,
    searchQuery,
    setSearchQuery,
    selectedTopic,
    setSelectedTopic,
    selectedIndustry,
    setSelectedIndustry,
    selectedSource,
    setSelectedSource,
    selectedPublisher,
    setSelectedPublisher,
    selectedCountry,
    setSelectedCountry,
    selectedCategory,
    setSelectedCategory,
    selectedEntityId,
    setSelectedEntityId,
    datePreset,
    setDatePreset,
    startDate,
    setStartDate,
    endDate,
    setEndDate,
    sortOrder,
    setSortOrder,
    timelineInterval,
    setTimelineInterval,
    timelineTimezone,
    setTimelineTimezone,
    timelineData,
    facets,
    topics,
    sources,
    publishers,
    coverage,
    status,
    suggestions,
    isSuggestionsLoading,
    fetchSuggestions,
    loadNextPage,
    refresh,
    clearFilters,
    hasActiveFilters,
  };
}
