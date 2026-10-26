"use client";

import React, { useState } from "react";
import { useNewsSentiment, KNOWN_ENTITIES } from "@/hooks/news/useNewsSentiment";
import { SentimentDistribution } from "./SentimentDistribution";
import { SentimentTimelineChart } from "./SentimentTimelineChart";
import { SentimentRelevanceTable } from "./SentimentRelevanceTable";
import { SentimentInspector } from "./SentimentInspector";
import { NewsMarketContextPanel } from "./NewsMarketContextPanel";
import { SentimentMethodologyModal } from "./SentimentMethodologyModal";
import {
  BarChart3,
  RefreshCw,
  SlidersHorizontal,
  Building2,
  Calendar,
  Layers,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

export function NewsSentimentWorkspace() {
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);
  const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null);

  const {
    selectedEntityId,
    setSelectedEntityId,
    evaluationDays,
    setEvaluationDays,
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
    refresh,
    loadArticleSentiment,
    loadMarketReaction,
    loadEvaluation,
  } = useNewsSentiment();

  const handleSelectArticle = (articleId: string) => {
    setSelectedArticleId(articleId);
    loadArticleSentiment(articleId);
  };

  const handleTriggerMarketReaction = (articleId: string, publishedAt: string, ticker: string) => {
    loadMarketReaction({
      article_id_or_event_id: articleId,
      instrument_id: `inst-${ticker.toLowerCase()}-us`,
      ticker,
      publication_time: publishedAt,
      window_type: "PREV_CLOSE_TO_NEXT_CLOSE",
    });
  };

  const handleOpenMethodology = () => {
    setIsMethodologyOpen(true);
    if (!evaluation) {
      loadEvaluation();
    }
  };

  return (
    <div className="space-y-4 font-mono">
      {/* Top Filter and Controls Toolbar */}
      <div className="p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 flex flex-wrap items-center justify-between gap-3">
        {/* Entity Selector */}
        <div className="flex items-center space-x-2">
          <Building2 className="w-4 h-4 text-cyan-500" />
          <span className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 uppercase">Target Entity:</span>
          <div className="flex items-center space-x-1">
            {KNOWN_ENTITIES.map((ent) => {
              const isActive = selectedEntityId === ent.entityId;
              return (
                <button
                  key={ent.entityId}
                  onClick={() => setSelectedEntityId(ent.entityId)}
                  className={`px-2.5 py-1 text-xs rounded border transition-colors ${
                    isActive
                      ? "bg-cyan-500 text-white font-bold border-cyan-500 shadow-sm"
                      : "bg-zinc-50 dark:bg-zinc-950 text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                  }`}
                >
                  {ent.ticker} <span className="hidden sm:inline text-[10px] opacity-80">({ent.name})</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Date Window and Action Buttons */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 border border-zinc-200 dark:border-zinc-800 rounded p-0.5 bg-zinc-50 dark:bg-zinc-950 text-xs">
            <Calendar className="w-3.5 h-3.5 text-zinc-400 ml-1.5" />
            {[7, 14, 30, 90].map((d) => (
              <button
                key={d}
                onClick={() => setEvaluationDays(d)}
                className={`px-2 py-0.5 rounded text-[11px] transition-colors ${
                  evaluationDays === d
                    ? "bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 font-bold"
                    : "text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200"
                }`}
              >
                {d}D
              </button>
            ))}
          </div>

          <button
            onClick={handleOpenMethodology}
            className="px-2.5 py-1 text-xs rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 flex items-center space-x-1.5 transition-colors"
            title="Inspect Model Evaluation & Benchmark"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-500" />
            <span className="hidden sm:inline">Methodology</span>
          </button>

          <button
            onClick={refresh}
            disabled={isLoading}
            className="p-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400 transition-colors"
            title="Refresh Sentiment Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-cyan-500" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Grid Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Left Column: Distribution, Timeline, Relevance Table */}
        <div className="lg:col-span-7 space-y-4">
          <SentimentDistribution aggregate={aggregate} isLoading={isLoading} />
          <SentimentTimelineChart timeline={timeline} isLoading={isLoading} />
          <SentimentRelevanceTable
            relevanceList={relevanceList}
            selectedArticleId={selectedArticleId}
            onSelectArticle={handleSelectArticle}
            isLoading={isLoading}
          />
        </div>

        {/* Right Column: Inspector & Market Reaction Panel */}
        <div className="lg:col-span-5 space-y-4">
          <SentimentInspector
            annotation={selectedAnnotation}
            onTriggerMarketReaction={handleTriggerMarketReaction}
            isLoading={isLoading}
          />
          <NewsMarketContextPanel
            marketContext={marketReaction}
            isLoading={isMarketReactionLoading}
          />
        </div>
      </div>

      {/* Methodology & Evaluation Modal */}
      <SentimentMethodologyModal
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
        evaluation={evaluation}
        isLoading={isEvaluationLoading}
      />
    </div>
  );
}
