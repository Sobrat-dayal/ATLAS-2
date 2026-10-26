"use client";

import React from "react";
import {
  ExternalLink,
  ShieldCheck,
  Clock,
  Building2,
  Landmark,
  FileText,
  AlertCircle,
  Tag,
  Globe2,
} from "lucide-react";
import { NewsArticleDTO } from "@/lib/news/types";
import {
  formatFullUtcTime,
  formatPublishedTime,
  formatRelativeTime,
  getCategoryBadgeStyle,
  isSafeExternalUrl,
} from "@/lib/news/formatting";

interface NewsArticlePreviewProps {
  article: NewsArticleDTO | null;
  onClose?: () => void;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
}

export function NewsArticlePreview({
  article,
  onClose,
  onNavigateEntity,
}: NewsArticlePreviewProps) {
  if (!article) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-zinc-400 dark:text-zinc-500 border border-zinc-200 dark:border-zinc-800 rounded bg-white dark:bg-zinc-900 h-full min-h-[300px]">
        <FileText className="w-8 h-8 stroke-[1.5] mb-2 text-zinc-300 dark:text-zinc-600" />
        <p className="text-xs font-medium">Select an article from the feed to view verified source details.</p>
      </div>
    );
  }

  const primaryCategory = article.categories[0] || "GENERAL_FINANCIAL";
  const catStyle = getCategoryBadgeStyle(primaryCategory);
  const destinationUrl = article.original_url || article.canonical_url;
  const isUrlSafe = isSafeExternalUrl(destinationUrl);

  return (
    <div className="flex flex-col border border-zinc-200 dark:border-zinc-800 rounded bg-white dark:bg-zinc-900 shadow-sm p-4 sm:p-5 h-full overflow-y-auto">
      {/* Publisher Attribution & Category Bar */}
      <div className="flex items-center justify-between gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-zinc-900 dark:text-zinc-50 font-mono">
            {article.publisher_name}
          </span>
          <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 dark:text-emerald-400 font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verified Source</span>
          </span>
        </div>

        <span
          className={`px-2 py-0.5 text-[10px] font-mono font-medium rounded border ${catStyle.bg} ${catStyle.text} ${catStyle.border}`}
        >
          {primaryCategory}
        </span>
      </div>

      {/* Headline */}
      <h2 className="text-base sm:text-lg font-bold text-zinc-900 dark:text-zinc-50 leading-snug tracking-tight mb-3">
        {article.headline}
      </h2>

      {/* Timestamps Provenance */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-zinc-500 dark:text-zinc-400 py-2 mb-3 bg-zinc-50 dark:bg-zinc-800/40 px-3 rounded border border-zinc-100 dark:border-zinc-800 font-mono text-[11px]">
        <div className="flex items-center gap-1.5" title={`Published at ${article.published_at}`}>
          <Clock className="w-3.5 h-3.5 text-zinc-400" />
          <span>Published: {formatFullUtcTime(article.published_at)}</span>
          <span className="text-zinc-400 font-sans">({formatRelativeTime(article.published_at)})</span>
        </div>

        {article.source_updated_at && (
          <div className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
            <span>Updated: {formatPublishedTime(article.source_updated_at)}</span>
          </div>
        )}
      </div>

      {/* Permitted Excerpt */}
      <div className="my-2">
        <div className="text-[11px] font-mono uppercase text-zinc-400 tracking-wider mb-1.5">
          Authorized Excerpt
        </div>
        {article.permitted_excerpt ? (
          <p className="text-xs sm:text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed bg-zinc-50/50 dark:bg-zinc-800/20 p-3 rounded border border-zinc-100 dark:border-zinc-800">
            {article.permitted_excerpt}
          </p>
        ) : (
          <div className="p-3 rounded bg-zinc-50 dark:bg-zinc-800/20 text-xs text-zinc-400 italic border border-zinc-100 dark:border-zinc-800">
            Excerpt unavailable under publisher licensing tier. Read full story at publisher site.
          </div>
        )}
      </div>

      {/* Linked Canonical Entities */}
      {article.linked_entities.length > 0 && (
        <div className="my-3">
          <div className="text-[11px] font-mono uppercase text-zinc-400 tracking-wider mb-2">
            Linked Companies & Instruments
          </div>
          <div className="flex flex-wrap gap-2">
            {article.linked_entities.map((entity) => {
              const isCentralBank = entity.entity_type === "CENTRAL_BANK";
              return (
                <button
                  key={entity.entity_id}
                  onClick={() => {
                    if (onNavigateEntity) {
                      onNavigateEntity(entity.entity_id, entity.entity_type, entity.ticker);
                    }
                  }}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-800 dark:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors shadow-sm"
                >
                  {isCentralBank ? (
                    <Landmark className="w-3.5 h-3.5 text-zinc-500" />
                  ) : (
                    <Building2 className="w-3.5 h-3.5 text-zinc-500" />
                  )}
                  <span className="font-bold">{entity.ticker || entity.canonical_name}</span>
                  {entity.exchange && (
                    <span className="text-[10px] text-zinc-400 font-sans">
                      ({entity.exchange})
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Geographies & Metadata */}
      {article.geographies.length > 0 && (
        <div className="flex items-center gap-2 my-2 text-xs text-zinc-500 font-mono">
          <Globe2 className="w-3.5 h-3.5 text-zinc-400" />
          <span>Regions: {article.geographies.join(", ")}</span>
        </div>
      )}

      {/* Action: Read Original Article at Publisher */}
      <div className="mt-auto pt-4 border-t border-zinc-100 dark:border-zinc-800">
        {isUrlSafe ? (
          <a
            href={destinationUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-2 px-3 rounded text-xs font-medium bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors shadow-sm"
          >
            <span>Read Original Article on {article.publisher_name}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        ) : (
          <div className="flex items-center gap-2 text-xs text-amber-600 bg-amber-500/10 p-2 rounded border border-amber-500/20">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>External link destination withheld due to destination verification policy.</span>
          </div>
        )}
        <p className="text-[10px] text-zinc-400 dark:text-zinc-500 text-center mt-2">
          Copyright belongs to {article.publisher_name}. ATLAS provides verified source metadata & licensed excerpts.
        </p>
      </div>
    </div>
  );
}
