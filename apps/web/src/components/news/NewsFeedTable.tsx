"use client";

import React, { useEffect, useRef } from "react";
import { Building2, CheckCircle2, ChevronDown, Landmark, Sparkles } from "lucide-react";
import { NewsArticleDTO } from "@/lib/news/types";
import {
  formatPublishedTime,
  formatRelativeTime,
  getCategoryBadgeStyle,
} from "@/lib/news/formatting";

interface NewsFeedTableProps {
  articles: NewsArticleDTO[];
  selectedArticle: NewsArticleDTO | null;
  onSelectArticle: (article: NewsArticleDTO) => void;
  totalCount: number;
  hasMore: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
}

export function NewsFeedTable({
  articles,
  selectedArticle,
  onSelectArticle,
  totalCount,
  hasMore,
  isLoading,
  onLoadMore,
  onNavigateEntity,
}: NewsFeedTableProps) {
  const tableRef = useRef<HTMLDivElement>(null);

  // Keyboard navigation: Up / Down arrow keys
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (!articles || articles.length === 0) return;

      // Ignore when user is typing in an input or textarea
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      const currentIndex = selectedArticle
        ? articles.findIndex((a) => a.article_id === selectedArticle.article_id)
        : -1;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        const nextIndex = currentIndex < articles.length - 1 ? currentIndex + 1 : 0;
        onSelectArticle(articles[nextIndex]);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : articles.length - 1;
        onSelectArticle(articles[prevIndex]);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [articles, selectedArticle, onSelectArticle]);

  if (articles.length === 0 && !isLoading) {
    return null; // Empty state will be handled by container
  }

  return (
    <div className="flex flex-col flex-1 min-w-0" ref={tableRef}>
      <div className="overflow-x-auto border border-zinc-200 dark:border-zinc-800 rounded bg-white dark:bg-zinc-900 shadow-sm">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-800/60 text-zinc-500 dark:text-zinc-400 font-mono text-[11px]">
              <th className="py-2 px-3 font-semibold w-24">TIME (UTC)</th>
              <th className="py-2 px-3 font-semibold w-36">SOURCE</th>
              <th className="py-2 px-3 font-semibold">HEADLINE</th>
              <th className="py-2 px-3 font-semibold w-28 hidden md:table-cell">CATEGORY</th>
              <th className="py-2 px-3 font-semibold w-48 hidden lg:table-cell">ENTITIES</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60 font-sans">
            {articles.map((article) => {
              const isSelected = selectedArticle?.article_id === article.article_id;
              const primaryCategory = article.categories[0] || "GENERAL_FINANCIAL";
              const catStyle = getCategoryBadgeStyle(primaryCategory);
              const relativeTime = formatRelativeTime(article.published_at);

              return (
                <tr
                  key={article.article_id}
                  onClick={() => onSelectArticle(article)}
                  className={`cursor-pointer transition-colors group ${
                    isSelected
                      ? "bg-zinc-100 dark:bg-zinc-800 border-l-2 border-l-zinc-900 dark:border-l-zinc-100"
                      : "hover:bg-zinc-50 dark:hover:bg-zinc-800/40"
                  }`}
                >
                  {/* Publication Time */}
                  <td className="py-2.5 px-3 font-mono text-[11px] text-zinc-500 dark:text-zinc-400 whitespace-nowrap">
                    <span title={article.published_at}>
                      {formatPublishedTime(article.published_at)}
                    </span>
                    {relativeTime && (
                      <span className="block text-[10px] text-zinc-400 dark:text-zinc-500 font-sans">
                        {relativeTime}
                      </span>
                    )}
                  </td>

                  {/* Publisher / Source */}
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <span className="font-semibold text-zinc-800 dark:text-zinc-200 truncate max-w-[120px]">
                        {article.publisher_name}
                      </span>
                      <span title="Verified Publisher">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />
                      </span>
                    </div>
                  </td>

                  {/* Headline */}
                  <td className="py-2.5 px-3 min-w-[200px]">
                    <div className="flex items-start gap-2">
                      <span
                        className={`font-medium line-clamp-2 leading-relaxed ${
                          isSelected
                            ? "text-zinc-950 dark:text-zinc-50 font-semibold"
                            : "text-zinc-800 dark:text-zinc-200 group-hover:text-zinc-950 dark:group-hover:text-white"
                        }`}
                      >
                        {article.headline}
                      </span>
                      {article.is_corrected && (
                        <span className="px-1.5 py-0.5 text-[9px] font-mono rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 shrink-0">
                          CORRECTED
                        </span>
                      )}
                      {article.syndicated_from_id && (
                        <span className="px-1.5 py-0.5 text-[9px] font-mono rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 shrink-0">
                          WIRE
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Category */}
                  <td className="py-2.5 px-3 whitespace-nowrap hidden md:table-cell">
                    <span
                      className={`inline-block px-1.5 py-0.5 text-[10px] font-mono font-medium rounded border ${catStyle.bg} ${catStyle.text} ${catStyle.border}`}
                    >
                      {primaryCategory}
                    </span>
                  </td>

                  {/* Linked Entities */}
                  <td className="py-2.5 px-3 hidden lg:table-cell">
                    <div className="flex flex-wrap items-center gap-1">
                      {article.linked_entities.slice(0, 2).map((entity) => {
                        const isCentralBank = entity.entity_type === "CENTRAL_BANK";
                        return (
                          <button
                            key={entity.entity_id}
                            onClick={(e) => {
                              e.stopPropagation();
                              if (onNavigateEntity) {
                                onNavigateEntity(entity.entity_id, entity.entity_type, entity.ticker);
                              }
                            }}
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 transition-colors"
                          >
                            {isCentralBank ? (
                              <Landmark className="w-2.5 h-2.5 text-zinc-500" />
                            ) : (
                              <Building2 className="w-2.5 h-2.5 text-zinc-500" />
                            )}
                            <span className="font-semibold">{entity.ticker || entity.canonical_name}</span>
                          </button>
                        );
                      })}
                      {article.linked_entities.length > 2 && (
                        <span className="text-[10px] text-zinc-400 font-mono">
                          +{article.linked_entities.length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between py-3 px-1 text-xs text-zinc-500 dark:text-zinc-400">
        <span className="font-mono text-[11px]">
          Showing {articles.length} of {totalCount} verified articles
        </span>
        {hasMore && (
          <button
            onClick={onLoadMore}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors text-xs font-medium disabled:opacity-50"
          >
            <span>{isLoading ? "Loading..." : "Load More Headlines"}</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
