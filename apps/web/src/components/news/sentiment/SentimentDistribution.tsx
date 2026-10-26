"use client";

import React from "react";
import { EntitySentimentAggregateDTO } from "@/lib/news/types";
import { AlertCircle, CheckCircle2, MinusCircle, HelpCircle, Shuffle } from "lucide-react";

interface SentimentDistributionProps {
  aggregate: EntitySentimentAggregateDTO | null;
  isLoading?: boolean;
}

export function SentimentDistribution({ aggregate, isLoading }: SentimentDistributionProps) {
  if (isLoading || !aggregate) {
    return (
      <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 animate-pulse">
        <div className="h-4 w-48 bg-zinc-200 dark:bg-zinc-800 rounded mb-4" />
        <div className="h-20 bg-zinc-100 dark:bg-zinc-800/40 rounded" />
      </div>
    );
  }

  const {
    eligible_count,
    positive_count,
    negative_count,
    neutral_count,
    mixed_count,
    insufficient_evidence_count,
    net_sentiment,
    unique_story_count,
    independent_publisher_count,
    coverage_completeness,
  } = aggregate;

  const total = eligible_count > 0 ? eligible_count : 1;
  const posPct = Math.round((positive_count / total) * 100);
  const negPct = Math.round((negative_count / total) * 100);
  const neuPct = Math.round((neutral_count / total) * 100);
  const mixPct = Math.round((mixed_count / total) * 100);
  const insPct = Math.round((insufficient_evidence_count / total) * 100);

  // Net sentiment color
  const netColor =
    net_sentiment > 0.05
      ? "text-emerald-500"
      : net_sentiment < -0.05
      ? "text-rose-500"
      : "text-zinc-400";

  return (
    <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 font-mono">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <h3 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Sentiment Distribution & Net Score
          </h3>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            Eligible Cohort: {eligible_count} verified article revisions across {unique_story_count} story threads
          </p>
        </div>
        <div className="flex items-center space-x-3 text-right">
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Coverage</div>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                coverage_completeness === "HIGH"
                  ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/30"
                  : coverage_completeness === "MODERATE"
                  ? "bg-cyan-500/10 text-cyan-500 border border-cyan-500/30"
                  : "bg-amber-500/10 text-amber-500 border border-amber-500/30"
              }`}
            >
              {coverage_completeness}
            </span>
          </div>
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Net Sentiment</div>
            <div className={`text-base font-bold tabular-nums ${netColor}`}>
              {net_sentiment > 0 ? `+${net_sentiment.toFixed(2)}` : net_sentiment.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Visual Stacked Progress Bar */}
      <div className="mt-4">
        <div className="h-3 w-full bg-zinc-100 dark:bg-zinc-800 rounded-sm overflow-hidden flex">
          {posPct > 0 && (
            <div
              style={{ width: `${posPct}%` }}
              className="bg-emerald-500 transition-all duration-300"
              title={`Positive: ${positive_count} (${posPct}%)`}
            />
          )}
          {negPct > 0 && (
            <div
              style={{ width: `${negPct}%` }}
              className="bg-rose-500 transition-all duration-300"
              title={`Negative: ${negative_count} (${negPct}%)`}
            />
          )}
          {neuPct > 0 && (
            <div
              style={{ width: `${neuPct}%` }}
              className="bg-zinc-400 transition-all duration-300"
              title={`Neutral: ${neutral_count} (${neuPct}%)`}
            />
          )}
          {mixPct > 0 && (
            <div
              style={{ width: `${mixPct}%` }}
              className="bg-purple-500 transition-all duration-300"
              title={`Mixed: ${mixed_count} (${mixPct}%)`}
            />
          )}
          {insPct > 0 && (
            <div
              style={{ width: `${insPct}%` }}
              className="bg-amber-500/60 transition-all duration-300"
              title={`Insufficient: ${insufficient_evidence_count} (${insPct}%)`}
            />
          )}
        </div>
      </div>

      {/* Breakdown Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mt-4 text-xs">
        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center space-x-1.5 text-emerald-500 font-semibold mb-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Positive</span>
          </div>
          <div className="text-base font-bold tabular-nums text-zinc-900 dark:text-zinc-100">
            {positive_count} <span className="text-[10px] text-zinc-500 font-normal">({posPct}%)</span>
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center space-x-1.5 text-rose-500 font-semibold mb-1">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Negative</span>
          </div>
          <div className="text-base font-bold tabular-nums text-zinc-900 dark:text-zinc-100">
            {negative_count} <span className="text-[10px] text-zinc-500 font-normal">({negPct}%)</span>
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center space-x-1.5 text-zinc-400 font-semibold mb-1">
            <MinusCircle className="w-3.5 h-3.5" />
            <span>Neutral</span>
          </div>
          <div className="text-base font-bold tabular-nums text-zinc-900 dark:text-zinc-100">
            {neutral_count} <span className="text-[10px] text-zinc-500 font-normal">({neuPct}%)</span>
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center space-x-1.5 text-purple-400 font-semibold mb-1">
            <Shuffle className="w-3.5 h-3.5" />
            <span>Mixed</span>
          </div>
          <div className="text-base font-bold tabular-nums text-zinc-900 dark:text-zinc-100">
            {mixed_count} <span className="text-[10px] text-zinc-500 font-normal">({mixPct}%)</span>
          </div>
        </div>

        <div className="p-2 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center space-x-1.5 text-amber-500 font-semibold mb-1">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Insufficient</span>
          </div>
          <div className="text-base font-bold tabular-nums text-zinc-900 dark:text-zinc-100">
            {insufficient_evidence_count} <span className="text-[10px] text-zinc-500 font-normal">({insPct}%)</span>
          </div>
        </div>
      </div>

      {/* Footnote Disclaimers */}
      <div className="mt-3 pt-2 border-t border-zinc-200 dark:border-zinc-800 text-[10px] text-zinc-500 flex flex-wrap items-center justify-between gap-2">
        <span>
          Independent newsrooms: <strong className="text-zinc-700 dark:text-zinc-300">{independent_publisher_count}</strong> (syndications deduplicated)
        </span>
        <span className="italic text-zinc-400">
          Tone is analytical language framing, not an investment recommendation.
        </span>
      </div>
    </div>
  );
}
