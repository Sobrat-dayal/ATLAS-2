"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getNewsStories,
  getNewsStory,
  getNewsStoryArticles,
  getNewsStoryEvents,
  NewsStoryQueryParams,
} from "@/lib/news/api";
import {
  NewsArticleDTO,
  NewsFinancialEventDTO,
  NewsStoryStatus,
  NewsStoryThreadDTO,
} from "@/lib/news/types";

export function useNewsStories() {
  const [stories, setStories] = useState<NewsStoryThreadDTO[]>([]);
  const [selectedStory, setSelectedStory] = useState<NewsStoryThreadDTO | null>(null);
  const [storyArticles, setStoryArticles] = useState<NewsArticleDTO[]>([]);
  const [storyEvents, setStoryEvents] = useState<NewsFinancialEventDTO[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [topicFilter, setTopicFilter] = useState<string>("");
  const [publisherFilter, setPublisherFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStories = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: NewsStoryQueryParams = {
        limit: 30,
      };
      if (statusFilter) params.status = statusFilter;
      if (topicFilter) params.topic_id = topicFilter;
      if (publisherFilter) params.publisher_id = publisherFilter;
      if (searchQuery) params.q = searchQuery;

      const res = await getNewsStories(params);
      setStories(res.stories);
      setTotalCount(res.total_count);
      setNextCursor(res.next_cursor || null);
      setHasMore(res.has_more);

      // Auto-select first story if none selected or previous selection no longer in list
      if (res.stories.length > 0) {
        setSelectedStory((prev) => {
          if (!prev) return res.stories[0];
          const exists = res.stories.find((s) => s.story_id === prev.story_id);
          return exists || res.stories[0];
        });
      } else {
        setSelectedStory(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load Story Threads";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, topicFilter, publisherFilter, searchQuery]);

  useEffect(() => {
    fetchStories();
  }, [fetchStories]);

  // Fetch story articles and events whenever selectedStory changes
  useEffect(() => {
    if (!selectedStory) {
      setStoryArticles([]);
      setStoryEvents([]);
      return;
    }

    let mounted = true;
    setIsDetailLoading(true);

    async function loadStoryDetails() {
      try {
        const [arts, evts] = await Promise.all([
          getNewsStoryArticles(selectedStory!.story_id),
          getNewsStoryEvents(selectedStory!.story_id),
        ]);
        if (mounted) {
          setStoryArticles(arts);
          setStoryEvents(evts);
        }
      } catch (err) {
        console.error("Failed to fetch story details:", err);
      } finally {
        if (mounted) setIsDetailLoading(false);
      }
    }

    loadStoryDetails();
    return () => {
      mounted = false;
    };
  }, [selectedStory?.story_id]);

  const selectStory = useCallback(
    async (storyId: string) => {
      const existing = stories.find((s) => s.story_id === storyId);
      if (existing) {
        setSelectedStory(existing);
        return;
      }
      try {
        setIsDetailLoading(true);
        const fetched = await getNewsStory(storyId);
        setSelectedStory(fetched);
      } catch (err) {
        console.error("Failed to load story by ID:", err);
      } finally {
        setIsDetailLoading(false);
      }
    },
    [stories]
  );

  return {
    stories,
    selectedStory,
    storyArticles,
    storyEvents,
    totalCount,
    hasMore,
    isLoading,
    isDetailLoading,
    error,
    statusFilter,
    setStatusFilter,
    topicFilter,
    setTopicFilter,
    publisherFilter,
    setPublisherFilter,
    searchQuery,
    setSearchQuery,
    selectStory,
    refresh: fetchStories,
  };
}
