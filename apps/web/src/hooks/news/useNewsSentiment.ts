"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getEntitySentiment,
  getEntitySentimentTimeline,
  getEntityRelevance,
  getArticleSentiment,
  getObservedMarketReaction,
  getSentimentEvaluation,
} from "@/lib/news/api";
import {
  EntitySentimentAggregateDTO,
  NewsEntityRelevanceDTO,
  NewsSentimentAnnotationDTO,
  ObservedNewsMarketContextDTO,
  SentimentEvaluationResultDTO,
  SentimentTimelineResponseDTO,
  MarketReactionRequestDTO,
} from "@/lib/news/types";

export interface KnownEntityOption {
  entityId: string;
  name: string;
  ticker: string;
}

export const KNOWN_ENTITIES: KnownEntityOption[] = [
  { entityId: "comp-aapl-001", name: "Apple Inc.", ticker: "AAPL" },
  { entityId: "comp-msft-002", name: "Microsoft Corp.", ticker: "MSFT" },
  { entityId: "comp-nvda-003", name: "NVIDIA Corp.", ticker: "NVDA" },
  { entityId: "comp-tsla-004", name: "Tesla Inc.", ticker: "TSLA" },
];

export function useNewsSentiment() {
  const [selectedEntityId, setSelectedEntityId] = useState<string>("comp-aapl-001");
  const [evaluationDays, setEvaluationDays] = useState<number>(30);
  const [timelineInterval, setTimelineInterval] = useState<string>("DAY");

  const [aggregate, setAggregate] = useState<EntitySentimentAggregateDTO | null>(null);
  const [timeline, setTimeline] = useState<SentimentTimelineResponseDTO | null>(null);
  const [relevanceList, setRelevanceList] = useState<NewsEntityRelevanceDTO[]>([]);
  const [annotations, setAnnotations] = useState<NewsSentimentAnnotationDTO[]>([]);
  const [selectedAnnotation, setSelectedAnnotation] = useState<NewsSentimentAnnotationDTO | null>(null);
  const [marketReaction, setMarketReaction] = useState<ObservedNewsMarketContextDTO | null>(null);
  const [evaluation, setEvaluation] = useState<SentimentEvaluationResultDTO | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isEvaluationLoading, setIsEvaluationLoading] = useState<boolean>(false);
  const [isMarketReactionLoading, setIsMarketReactionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load entity aggregate, timeline and relevance
  const loadEntityAnalytics = useCallback(async (entityId: string, days: number = 30) => {
    setIsLoading(true);
    setError(null);
    try {
      const [aggData, timeData, relData] = await Promise.all([
        getEntitySentiment(entityId, days).catch(() => null),
        getEntitySentimentTimeline(entityId, "DAY", days).catch(() => null),
        getEntityRelevance(entityId, 50).catch(() => []),
      ]);

      if (aggData) {
        setAggregate(aggData);
      } else {
        // Fallback default structure if network unreachable
        setAggregate({
          target_entity_id: entityId,
          target_canonical_name: KNOWN_ENTITIES.find((k) => k.entityId === entityId)?.name || entityId,
          target_ticker: KNOWN_ENTITIES.find((k) => k.entityId === entityId)?.ticker || "EQUITY",
          evaluation_window_days: days,
          eligible_count: 0,
          positive_count: 0,
          negative_count: 0,
          neutral_count: 0,
          mixed_count: 0,
          insufficient_evidence_count: 0,
          net_sentiment: 0.0,
          unique_story_count: 0,
          independent_publisher_count: 0,
          top_aspects: [],
          coverage_completeness: "INSUFFICIENT",
          methodology_version: "v1.0.0-institutional",
          evaluation_time: new Date().toISOString(),
        });
      }

      setTimeline(timeData);
      setRelevanceList(relData || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sentiment analytics");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load article annotations for selected article
  const loadArticleSentiment = useCallback(async (articleId: string) => {
    try {
      const annList = await getArticleSentiment(articleId);
      setAnnotations(annList);
      if (annList.length > 0) {
        setSelectedAnnotation(annList[0]);
      }
    } catch {
      setAnnotations([]);
    }
  }, []);

  // Load market context
  const loadMarketReaction = useCallback(async (req: MarketReactionRequestDTO) => {
    setIsMarketReactionLoading(true);
    try {
      const reaction = await getObservedMarketReaction(req);
      setMarketReaction(reaction);
    } catch {
      setMarketReaction(null);
    } finally {
      setIsMarketReactionLoading(false);
    }
  }, []);

  // Load Golden Benchmark evaluation
  const loadEvaluation = useCallback(async () => {
    setIsEvaluationLoading(true);
    try {
      const res = await getSentimentEvaluation();
      setEvaluation(res);
    } catch {
      setEvaluation(null);
    } finally {
      setIsEvaluationLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadEntityAnalytics(selectedEntityId, evaluationDays);
  }, [loadEntityAnalytics, selectedEntityId, evaluationDays]);

  return {
    selectedEntityId,
    setSelectedEntityId,
    evaluationDays,
    setEvaluationDays,
    timelineInterval,
    setTimelineInterval,
    aggregate,
    timeline,
    relevanceList,
    annotations,
    selectedAnnotation,
    setSelectedAnnotation,
    marketReaction,
    evaluation,
    isLoading,
    isEvaluationLoading,
    isMarketReactionLoading,
    error,
    refresh: () => loadEntityAnalytics(selectedEntityId, evaluationDays),
    loadArticleSentiment,
    loadMarketReaction,
    loadEvaluation,
  };
}
