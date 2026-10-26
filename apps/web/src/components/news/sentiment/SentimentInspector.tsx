"use client";

import React from "react";
import { NewsSentimentAnnotationDTO } from "@/lib/news/types";
import { formatUtcTimestamp } from "@/lib/news/formatting";
import {
  Tag,
  Quote,
  ShieldCheck,
  TrendingUp,
  Cpu,
  Info,
} from "lucide-react";

interface SentimentInspectorProps {
  annotation: NewsSentimentAnnotationDTO | null;
  onTriggerMarketReaction?: (articleId: string, publishedAt: string, ticker: string) => void;
  isLoading?: boolean;
}

export function SentimentInspector({
  annotation,
  onTriggerMarketReaction,
  isLoading,
}: SentimentInspectorProps) {
  if (isLoading) {
    return (
      <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono animate-pulse">
        <div className="h-4 w-40 bg-zinc-200 dark:bg-zinc-800 rounded mb-4" />
        <div className="h-24 bg-zinc-100 dark:bg-zinc-800/40 rounded" />
      </div>
    );
  }

  if (!annotation) {
    return (
      <div className="p-6 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono text-center">
        <Info className="w-8 h-8 text-zinc-400 mx-auto mb-2 opacity-50" />
        <h4 className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">No Article Selected</h4>
        <p className="text-[11px] text-zinc-500 mt-1">
          Select an article from the relevance table to inspect grounded sentiment evidence and aspects.
        </p>
      </div>
    );
  }

  const {
    target_canonical_name,
    target_ticker,
    target_entity_id,
    sentiment_label,
    sentiment_score,
    confidence_score,
    sentiment_aspect,
    analysis_method,
    model_or_rule_version,
    source_published_at,
    evidence,
    explanation,
    article_id,
  } = annotation;

  const labelBadge =
    sentiment_label === "POSITIVE"
      ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
      : sentiment_label === "NEGATIVE"
      ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
      : sentiment_label === "NEUTRAL"
      ? "bg-zinc-500/10 text-zinc-400 border-zinc-500/30"
      : sentiment_label === "MIXED"
      ? "bg-purple-500/10 text-purple-400 border-purple-500/30"
      : "bg-amber-500/10 text-amber-500 border-amber-500/30";

  return (
    <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono space-y-4">
      {/* Target & Sentiment Polarity Header */}
      <div className="flex items-start justify-between pb-3 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-zinc-900 dark:text-zinc-100">
              {target_canonical_name || target_entity_id}
            </span>
            {target_ticker && (
              <span className="text-[10px] px-1 py-0.2 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 rounded">
                {target_ticker}
              </span>
            )}
          </div>
          <div className="text-[10px] text-zinc-500 mt-0.5">
            Published: {formatUtcTimestamp(source_published_at)}
          </div>
        </div>

        <div className="text-right">
          <span className={`text-[11px] px-2 py-0.5 rounded border font-bold uppercase ${labelBadge}`}>
            {sentiment_label.replace("_", " ")}
          </span>
          <div className="text-[10px] text-zinc-500 mt-1 tabular-nums">
            Score: {sentiment_score > 0 ? `+${sentiment_score.toFixed(2)}` : sentiment_score.toFixed(2)} | Conf: {Math.round(confidence_score * 100)}%
          </div>
        </div>
      </div>

      {/* Financial Aspect */}
      <div>
        <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1 flex items-center space-x-1">
          <Tag className="w-3 h-3 text-cyan-500" />
          <span>Financial Aspect</span>
        </div>
        <div className="inline-block text-[11px] px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 font-semibold border border-zinc-200 dark:border-zinc-700">
          {sentiment_aspect.replace("_", " ")}
        </div>
      </div>

      {/* Grounded Evidence Citations */}
      <div>
        <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1 flex items-center space-x-1">
          <Quote className="w-3 h-3 text-cyan-500" />
          <span>Grounded Source Evidence ({evidence.length})</span>
        </div>
        {evidence.length === 0 ? (
          <p className="text-[11px] text-zinc-500 italic">No explicit text span cited for this annotation.</p>
        ) : (
          <div className="space-y-2">
            {evidence.map((ev, i) => (
              <div
                key={i}
                className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-xs"
              >
                <div className="flex items-center justify-between text-[10px] text-zinc-500 mb-1">
                  <span className="font-semibold text-zinc-400">[{ev.evidence_scope}]</span>
                  <span>{ev.rationale_code}</span>
                </div>
                <div className="text-zinc-800 dark:text-zinc-200 italic font-sans text-xs">
                  &ldquo;{ev.text_span}&rdquo;
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Explanation Rationale */}
      {explanation && (
        <div className="p-2.5 rounded bg-zinc-50/50 dark:bg-zinc-950/50 border border-zinc-200/80 dark:border-zinc-800/80 text-[11px] text-zinc-600 dark:text-zinc-400">
          <span className="font-semibold text-zinc-900 dark:text-zinc-200">Analysis Rationale: </span>
          {explanation}
        </div>
      )}

      {/* Methodology & Version */}
      <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between text-[10px] text-zinc-500">
        <div className="flex items-center space-x-1">
          <Cpu className="w-3 h-3 text-zinc-400" />
          <span>Method: {analysis_method}</span>
        </div>
        <div className="flex items-center space-x-1">
          <ShieldCheck className="w-3 h-3 text-emerald-500" />
          <span>v{model_or_rule_version}</span>
        </div>
      </div>

      {/* Trigger Market Reaction Button */}
      {onTriggerMarketReaction && target_ticker && (
        <button
          onClick={() => onTriggerMarketReaction(article_id, source_published_at, target_ticker)}
          className="w-full py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center justify-center space-x-1.5 transition-colors shadow-sm"
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span>Observe Market Context for {target_ticker}</span>
        </button>
      )}
    </div>
  );
}
