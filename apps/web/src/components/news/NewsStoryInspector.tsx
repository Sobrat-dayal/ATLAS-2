"use client";

import React from "react";
import {
  Layers,
  Building2,
  ExternalLink,
  Clock,
  ShieldCheck,
  Newspaper,
  Calendar,
  AlertCircle,
  Tag,
  ArrowRight,
} from "lucide-react";
import {
  NewsStoryThreadDTO,
  NewsArticleDTO,
  NewsFinancialEventDTO,
} from "@/lib/news/types";
import { formatShortUtcDateTime } from "@/lib/news/formatting";

interface NewsStoryInspectorProps {
  story: NewsStoryThreadDTO | null;
  articles: NewsArticleDTO[];
  events: NewsFinancialEventDTO[];
  isLoading: boolean;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
  onSelectEvent?: (event: NewsFinancialEventDTO) => void;
}

export function NewsStoryInspector({
  story,
  articles,
  events,
  isLoading,
  onNavigateEntity,
  onSelectEvent,
}: NewsStoryInspectorProps) {
  if (!story) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center h-full min-h-[400px]">
        <Layers className="w-10 h-10 text-zinc-300 dark:text-zinc-700 mb-3" />
        <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
          No Story Thread Selected
        </h3>
        <p className="text-xs text-zinc-500 max-w-xs mt-1">
          Select a developing story thread from the table to inspect multi-source coverage chronology and linked financial events.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm overflow-hidden font-sans">
      {/* Header */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/60 dark:bg-zinc-950/40">
        <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 dark:text-zinc-400 mb-1.5">
          <span className="flex items-center space-x-1.5 text-cyan-600 dark:text-cyan-400 font-semibold">
            <Layers className="w-3.5 h-3.5" />
            <span>{story.story_id}</span>
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            {story.story_status}
          </span>
        </div>

        <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 leading-snug">
          {story.display_title}
        </h2>

        {/* Primary Entity / Subject */}
        {story.primary_entity_name && (
          <div className="mt-2.5 flex items-center justify-between pt-2 border-t border-zinc-200/60 dark:border-zinc-800/60">
            <div className="flex items-center space-x-1.5">
              <Building2 className="w-4 h-4 text-zinc-400" />
              <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
                {story.primary_entity_name}
              </span>
            </div>
            {story.primary_entity_id && onNavigateEntity && (
              <button
                type="button"
                onClick={() => onNavigateEntity(story.primary_entity_id!, "COMPANY")}
                className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 hover:underline inline-flex items-center space-x-1"
              >
                <span>Open Profile</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Story Metadata & Coverage Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-3 bg-zinc-50/40 dark:bg-zinc-900/40 border-b border-zinc-200 dark:border-zinc-800 text-[11px] font-mono">
        <div>
          <span className="text-zinc-400 block text-[10px]">TOTAL REPORTS</span>
          <span className="font-semibold text-zinc-800 dark:text-zinc-200">
            {story.article_count}
          </span>
        </div>
        <div>
          <span className="text-zinc-400 block text-[10px]">INDEPENDENT</span>
          <span className="font-semibold text-cyan-600 dark:text-cyan-400">
            {story.independent_publisher_count} sources
          </span>
        </div>
        <div>
          <span className="text-zinc-400 block text-[10px]">FIRST OBSERVED</span>
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            {formatShortUtcDateTime(story.first_source_published_at)}
          </span>
        </div>
        <div>
          <span className="text-zinc-400 block text-[10px]">LATEST ACTIVITY</span>
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            {formatShortUtcDateTime(story.latest_source_published_at)}
          </span>
        </div>
      </div>

      {/* Publishers Represented */}
      <div className="px-4 py-2.5 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] font-mono text-zinc-500 mr-1 flex items-center space-x-1">
          <Newspaper className="w-3 h-3" />
          <span>Newsrooms:</span>
        </span>
        {story.publishers.map((pub, idx) => (
          <span
            key={idx}
            className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700"
          >
            {pub}
          </span>
        ))}
      </div>

      {/* Main Body: Chronological Articles & Linked Events */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Linked Financial Events */}
        {events.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-mono font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wide flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Verified Financial Events ({events.length})</span>
              </h4>
            </div>
            <div className="space-y-2">
              {events.map((ev) => (
                <div
                  key={ev.event_id}
                  onClick={() => onSelectEvent && onSelectEvent(ev)}
                  className="p-2.5 rounded border border-amber-200 dark:border-amber-900/40 bg-amber-50/50 dark:bg-amber-950/20 hover:bg-amber-50 dark:hover:bg-amber-950/40 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                    <span className="font-semibold text-amber-700 dark:text-amber-300">
                      {ev.event_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-zinc-500">{ev.event_id}</span>
                  </div>
                  <p className="text-xs font-medium text-zinc-900 dark:text-zinc-100 line-clamp-1">
                    {ev.event_title}
                  </p>
                  <div className="flex items-center space-x-2 mt-1.5 text-[10px] font-mono text-zinc-500">
                    <span>Status: <strong className="text-zinc-700 dark:text-zinc-300">{ev.lifecycle_status}</strong></span>
                    <span>•</span>
                    <span>Assertion: <strong className="text-zinc-700 dark:text-zinc-300">{ev.assertion_status}</strong></span>
                    {ev.amounts.length > 0 && (
                      <>
                        <span>•</span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                          ${ev.amounts[0].amount_value.toLocaleString()} {ev.amounts[0].currency}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Member Articles Chronology */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wide flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              <span>Coverage Progression ({articles.length} Reports)</span>
            </h4>
          </div>

          {isLoading ? (
            <div className="py-6 text-center text-xs font-mono text-zinc-400">
              Loading member coverage...
            </div>
          ) : articles.length === 0 ? (
            <div className="py-4 text-center text-xs text-zinc-500">
              No individual member articles available.
            </div>
          ) : (
            <div className="space-y-3 relative before:absolute before:inset-0 before:left-3 before:w-0.5 before:bg-zinc-200 dark:before:bg-zinc-800">
              {articles.map((art) => {
                const isAnchor = art.article_id === story.representative_article_id;

                return (
                  <div key={art.article_id} className="relative pl-7 group">
                    {/* Timeline Node Icon */}
                    <div
                      className={`absolute left-1.5 top-1.5 w-3 h-3 rounded-full border-2 transform -translate-x-1/2 ${
                        isAnchor
                          ? "bg-cyan-500 border-white dark:border-zinc-900 shadow-sm"
                          : "bg-zinc-300 dark:bg-zinc-700 border-white dark:border-zinc-900"
                      }`}
                    />

                    <div className="p-3 rounded border border-zinc-200 dark:border-zinc-800/80 bg-zinc-50/50 dark:bg-zinc-900/50 hover:bg-white dark:hover:bg-zinc-800/60 transition-colors">
                      <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 mb-1">
                        <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                          {art.publisher_name}
                        </span>
                        <span>{formatShortUtcDateTime(art.published_at)}</span>
                      </div>

                      <h5 className="text-xs font-semibold text-zinc-900 dark:text-zinc-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                        {art.headline}
                      </h5>

                      {art.permitted_excerpt && (
                        <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-1 line-clamp-2 leading-relaxed">
                          {art.permitted_excerpt}
                        </p>
                      )}

                      <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-zinc-100 dark:border-zinc-800 text-[10px] font-mono text-zinc-500">
                        <span>{art.article_type}</span>
                        {art.canonical_url && (
                          <a
                            href={art.canonical_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-cyan-600 dark:text-cyan-400 hover:underline"
                          >
                            <span>Original Sourced Report</span>
                            <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
