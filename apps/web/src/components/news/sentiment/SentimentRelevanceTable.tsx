"use client";

import React from "react";
import { NewsEntityRelevanceDTO } from "@/lib/news/types";
import { formatUtcTimestamp } from "@/lib/news/formatting";
import { FileText, Target, ExternalLink } from "lucide-react";

interface SentimentRelevanceTableProps {
  relevanceList: NewsEntityRelevanceDTO[];
  selectedArticleId?: string | null;
  onSelectArticle: (articleId: string) => void;
  isLoading?: boolean;
}

export function SentimentRelevanceTable({
  relevanceList,
  selectedArticleId,
  onSelectArticle,
  isLoading,
}: SentimentRelevanceTableProps) {
  if (isLoading) {
    return (
      <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono animate-pulse">
        <div className="h-4 w-48 bg-zinc-200 dark:bg-zinc-800 rounded mb-4" />
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-10 bg-zinc-100 dark:bg-zinc-800/40 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (relevanceList.length === 0) {
    return (
      <div className="p-8 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono text-center">
        <Target className="w-8 h-8 text-zinc-400 mx-auto mb-2 opacity-50" />
        <p className="text-xs text-zinc-500">No canonical entity relevance records found for this target.</p>
      </div>
    );
  }

  const getRelevanceBadge = (relClass: string) => {
    switch (relClass) {
      case "PRIMARY_SUBJECT":
        return "bg-cyan-500/10 text-cyan-500 border-cyan-500/30";
      case "DIRECT_PARTICIPANT":
        return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
      case "VERIFIED_MENTION":
        return "bg-zinc-500/10 text-zinc-400 border-zinc-500/30";
      case "VERIFIED_RELATED_ENTITY":
        return "bg-amber-500/10 text-amber-500 border-amber-500/30";
      default:
        return "bg-zinc-500/10 text-zinc-500 border-zinc-500/20";
    }
  };

  return (
    <div className="rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono overflow-hidden">
      <div className="p-3 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-cyan-500" />
          <h3 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Canonical Relevance & Entity Coverage Records ({relevanceList.length})
          </h3>
        </div>
        <span className="text-[10px] text-zinc-500">Click article row to inspect grounded sentiment & evidence</span>
      </div>

      <div className="overflow-x-auto max-h-[360px] overflow-y-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 text-[10px] text-zinc-500 uppercase tracking-wider sticky top-0 z-10">
              <th className="py-2 px-3">Published</th>
              <th className="py-2 px-3">Article Reference</th>
              <th className="py-2 px-3">Relevance Class</th>
              <th className="py-2 px-3">Score</th>
              <th className="py-2 px-3">Evidence Source</th>
              <th className="py-2 px-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {relevanceList.map((rel) => {
              const isSelected = selectedArticleId === rel.article_id;
              return (
                <tr
                  key={rel.relevance_id}
                  onClick={() => onSelectArticle(rel.article_id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-cyan-500/10 text-zinc-900 dark:text-zinc-100 font-medium"
                      : "hover:bg-zinc-50 dark:hover:bg-zinc-800/40 text-zinc-600 dark:text-zinc-300"
                  }`}
                >
                  <td className="py-2.5 px-3 text-[11px] text-zinc-500 whitespace-nowrap">
                    {formatUtcTimestamp(rel.source_published_at)}
                  </td>
                  <td className="py-2.5 px-3 font-semibold text-zinc-900 dark:text-zinc-100">
                    <div className="truncate max-w-[280px]" title={rel.article_id}>
                      {rel.article_id}
                    </div>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${getRelevanceBadge(
                        rel.relevance_class
                      )}`}
                    >
                      {rel.relevance_class.replace("_", " ")}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 tabular-nums font-bold text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
                    {rel.relevance_score.toFixed(2)}
                  </td>
                  <td className="py-2.5 px-3 text-[11px] text-zinc-500 whitespace-nowrap">
                    {rel.evidence_source}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectArticle(rel.article_id);
                      }}
                      className="text-[10px] text-cyan-500 hover:text-cyan-400 flex items-center space-x-1"
                    >
                      <span>Inspect</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
