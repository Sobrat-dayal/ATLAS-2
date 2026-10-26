"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getNewsCoverage,
  getNewsFeed,
  getNewsPublishers,
  getNewsSources,
  getNewsStatus,
} from "@/lib/news/api";
import {
  NewsArticleDTO,
  NewsCoverageResponseDTO,
  NewsFeedQueryParams,
  NewsFreshnessResponseDTO,
  NewsPublisherDTO,
  NewsSourceDTO,
  NewsTabKey,
} from "@/lib/news/types";

export function useNews() {
  const [activeTab, setActiveTab] = useState<NewsTabKey>("ALL");
  const [articles, setArticles] = useState<NewsArticleDTO[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<NewsArticleDTO | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedSource, setSelectedSource] = useState<string>("");
  const [selectedPublisher, setSelectedPublisher] = useState<string>("");
  const [selectedGeography, setSelectedGeography] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  // Metadata
  const [sources, setSources] = useState<NewsSourceDTO[]>([]);
  const [publishers, setPublishers] = useState<NewsPublisherDTO[]>([]);
  const [coverage, setCoverage] = useState<NewsCoverageResponseDTO | null>(null);
  const [status, setStatus] = useState<NewsFreshnessResponseDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load catalog metadata (sources, publishers, coverage, status)
  useEffect(() => {
    let mounted = true;
    async function loadMetadata() {
      try {
        const [srcs, pubs, cov, stat] = await Promise.allSettled([
          getNewsSources(),
          getNewsPublishers(),
          getNewsCoverage(),
          getNewsStatus(),
        ]);
        if (mounted) {
          if (srcs.status === "fulfilled") setSources(srcs.value);
          if (pubs.status === "fulfilled") setPublishers(pubs.value);
          if (cov.status === "fulfilled") setCoverage(cov.value);
          if (stat.status === "fulfilled") setStatus(stat.value);
        }
      } catch (err) {
        console.error("Failed to load news metadata:", err);
      }
    }
    loadMetadata();
    return () => {
      mounted = false;
    };
  }, []);

  // Fetch feed based on active filters and activeTab
  const fetchFeed = useCallback(
    async (cursor?: string, append: boolean = false) => {
      try {
        if (!append) setIsLoading(true);
        setError(null);

        const params: NewsFeedQueryParams = {
          limit: 30,
          cursor,
        };

        // Tab mapping to category or entity
        if (activeTab === "MARKETS") {
          params.category = "EQUITIES";
        } else if (activeTab === "COMPANIES") {
          params.category = "COMPANY";
        } else if (activeTab === "ECONOMICS") {
          params.category = "ECONOMICS";
        } else if (activeTab === "CENTRAL_BANKS") {
          params.category = "CENTRAL_BANKS";
        } else if (activeTab === "REGULATION") {
          params.category = "REGULATION";
        } else if (activeTab === "TECHNOLOGY") {
          params.category = "TECHNOLOGY";
        }

        // Explicit Category Filter override
        if (selectedCategory) {
          params.category = selectedCategory;
        }

        if (selectedSource) params.source_id = selectedSource;
        if (selectedPublisher) params.publisher_id = selectedPublisher;
        if (selectedGeography) params.geography = selectedGeography;
        if (searchQuery.trim()) params.q = searchQuery.trim();

        const res = await getNewsFeed(params);

        if (append) {
          setArticles((prev) => [...prev, ...res.articles]);
        } else {
          setArticles(res.articles);
          // Set initial selected article
          if (res.articles.length > 0) {
            setSelectedArticle(res.articles[0]);
          } else {
            setSelectedArticle(null);
          }
        }

        setTotalCount(res.total_count);
        setNextCursor(res.next_cursor || null);
        setHasMore(res.has_more);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load news feed";
        setError(msg);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [
      activeTab,
      selectedCategory,
      selectedSource,
      selectedPublisher,
      selectedGeography,
      searchQuery,
    ]
  );

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  const refresh = useCallback(() => {
    setIsRefreshing(true);
    fetchFeed();
    // Also refresh status
    getNewsStatus().then(setStatus).catch(() => {});
  }, [fetchFeed]);

  const loadNextPage = useCallback(() => {
    if (nextCursor && hasMore && !isLoading) {
      fetchFeed(nextCursor, true);
    }
  }, [nextCursor, hasMore, isLoading, fetchFeed]);

  const clearFilters = useCallback(() => {
    setSearchQuery("");
    setSelectedSource("");
    setSelectedPublisher("");
    setSelectedGeography("");
    setSelectedCategory("");
    setActiveTab("ALL");
  }, []);

  return {
    activeTab,
    setActiveTab,
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
    selectedSource,
    setSelectedSource,
    selectedPublisher,
    setSelectedPublisher,
    selectedGeography,
    setSelectedGeography,
    selectedCategory,
    setSelectedCategory,
    sources,
    publishers,
    coverage,
    status,
    refresh,
    loadNextPage,
    clearFilters,
  };
}
