"use client";

import React from "react";
import {
  NewsArticleDTO,
  NewsTimelineInterval,
  NewsTimelineResponseDTO,
} from "@/lib/news/types";

interface NewsTimelineProps {
  timelineData: NewsTimelineResponseDTO | null;
  selectedArticle: NewsArticleDTO | null;
  onSelectArticle: (article: NewsArticleDTO) => void;
  interval: NewsTimelineInterval;
  onIntervalChange: (interval: NewsTimelineInterval) => void;
  timezone: string;
  isLoading: boolean;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
}

export function NewsTimeline({
  timelineData,
  selectedArticle,
  onSelectArticle,
  interval,
  onIntervalChange,
  timezone,
  isLoading,
  onNavigateEntity,
}: NewsTimelineProps) {
  if (isLoading && !timelineData) {
    return (
      <div className="flex items-center justify-center p-16 text-zinc-400 font-mono text-xs border border-zinc-200 dark:border-zinc-800 rounded bg-white dark:bg-zinc-900 shadow-sm">
        <span className="animate-pulse">Aggregating chronological news timeline ({interval})...</span>
      </div>
    );
  }

  if (!timelineData || timelineData.buckets.length === 0) {
    return (
      <div className="p-8 text-center text-zinc-500 font-mono text-xs bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
        <p className="font-semibold text-zinc-700 dark:text-zinc-300 mb-1">No Timeline Events</p>
        <p className="text-[11px] text-zinc-400">
          No authorized news articles matched the active discovery query for the selected interval ({interval}).
        </p>
      </div>
    );
  }

  const formatArticleTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="flex flex-col space-y-4 font-mono text-xs">
      {/* Timeline Controls & Summary Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Timeline Interval:
          </span>
          <div className="flex rounded border border-zinc-200 dark:border-zinc-800 p-0.5 bg-zinc-50 dark:bg-zinc-950">
            {(["DAY", "WEEK", "MONTH"] as const).map((intKey) => (
              <button
                key={intKey}
                onClick={() => onIntervalChange(intKey)}
                className={`px-2.5 py-1 text-[10px] font-semibold rounded uppercase tracking-wider transition-colors ${
                  interval === intKey
                    ? "bg-cyan-500 text-white shadow-sm"
                    : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
                }`}
              >
                {intKey === "DAY" ? "Daily" : intKey === "WEEK" ? "Weekly" : "Monthly"}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-3 text-[11px] text-zinc-500 dark:text-zinc-400">
          <span>
            <strong className="text-zinc-800 dark:text-zinc-200 font-semibold">{timelineData.total_articles}</strong> articles across{" "}
            <strong className="text-zinc-800 dark:text-zinc-200 font-semibold">{timelineData.total_buckets}</strong> buckets
          </span>
          <span className="text-zinc-300 dark:text-zinc-700">|</span>
          <span className="text-zinc-400">TZ: {timezone}</span>
        </div>
      </div>

      {/* Chronological Buckets */}
      <div className="space-y-4">
        {timelineData.buckets.map((bucket) => (
          <div
            key={bucket.bucket_id}
            className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm overflow-hidden"
          >
            {/* Bucket Header */}
            <div className="px-4 py-2.5 bg-zinc-50/80 dark:bg-zinc-800/40 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-cyan-500" />
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 text-xs">
                  {bucket.label}
                </h3>
              </div>
              <span className="px-2 py-0.5 text-[10px] rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 font-semibold">
                {bucket.article_count} {bucket.article_count === 1 ? "article" : "articles"}
              </span>
            </div>

            {/* Bucket Articles */}
            <div className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
              {bucket.articles.map((article) => {
                const isSelected = selectedArticle?.article_id === article.article_id;
                return (
                  <div
                    key={article.article_id}
                    onClick={() => onSelectArticle(article)}
                    className={`p-3.5 transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-cyan-500/5 dark:bg-cyan-500/10 border-l-2 border-cyan-500"
                        : "hover:bg-zinc-50 dark:hover:bg-zinc-800/40"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      {/* Left: Time + Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 text-[10px] text-zinc-400 mb-1">
                          <span className="font-semibold text-zinc-600 dark:text-zinc-300">
                            {formatArticleTime(article.published_at)}
                          </span>
                          <span>•</span>
                          <span className="text-zinc-700 dark:text-zinc-200 font-medium">
                            {article.publisher_name}
                          </span>
                          {article.is_corrected && (
                            <span className="px-1 py-0.2 rounded text-[9px] bg-amber-500/10 text-amber-600 border border-amber-500/20">
                              CORRECTED
                            </span>
                          )}
                          {article.is_duplicate && (
                            <span className="px-1 py-0.2 rounded text-[9px] bg-zinc-200 dark:bg-zinc-700 text-zinc-500">
                              SYNDICATED
                            </span>
                          )}
                        </div>

                        <h4 className="font-medium text-zinc-900 dark:text-zinc-100 text-xs leading-snug line-clamp-2 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                          {article.headline}
                        </h4>

                        {article.permitted_excerpt && (
                          <p className="mt-1 text-[11px] text-zinc-500 dark:text-zinc-400 line-clamp-2">
                            {article.permitted_excerpt}
                          </p>
                        )}

                        {/* Linked Entities */}
                        {article.linked_entities && article.linked_entities.length > 0 && (
                          <div className="flex flex-wrap items-center gap-1.5 mt-2">
                            {article.linked_entities.map((e) => (
                              <button
                                key={e.entity_id}
                                onClick={(ev) => {
                                  ev.stopPropagation();
                                  if (onNavigateEntity) {
                                    onNavigateEntity(e.entity_id, e.entity_type, e.ticker);
                                  }
                                }}
                                className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-100 dark:bg-zinc-800 hover:bg-cyan-500/10 hover:text-cyan-500 text-zinc-600 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700 transition-colors"
                              >
                                {e.ticker || e.canonical_name}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Right: Badge */}
                      <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded uppercase font-semibold text-zinc-400 bg-zinc-100 dark:bg-zinc-800/80">
                        {article.article_type.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
