"use client";

import React, { useEffect, useState } from "react";
import { ExternalLink, Newspaper } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface NewsPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

interface NewsItem {
  id: string;
  symbol: string;
  headline: string;
  source: string;
  timeAgo: string;
}

const DEFAULT_NEWS: NewsItem[] = [
  { id: "n1", symbol: "AAPL", headline: "Apple expands custom silicon roadmap with next-generation M5 architecture", source: "Bloomberg", timeAgo: "14m ago" },
  { id: "n2", symbol: "MSFT", headline: "Microsoft reports 29% Azure growth amidst enterprise generative AI adoption", source: "Reuters", timeAgo: "32m ago" },
  { id: "n3", symbol: "NVDA", headline: "NVIDIA announces Blackwell volume shipments commencing ahead of schedule", source: "WSJ", timeAgo: "1h ago" },
  { id: "n4", symbol: "SPY", headline: "Federal Reserve holds benchmark rate steady as core PCE inflation cools", source: "Financial Times", timeAgo: "2h ago" },
  { id: "n5", symbol: "AAPL", headline: "Supply chain checks confirm strong holiday quarter demand across Asia", source: "Morgan Stanley", timeAgo: "3h ago" },
  { id: "n6", symbol: "TSLA", headline: "Tesla files regulatory approval for unsupervised Full Self-Driving in Europe", source: "Reuters", timeAgo: "4h ago" },
];

export function NewsPanelAdapter({
  panel,
  context,
}: NewsPanelAdapterProps) {
  const symbol =
    (!panel.independent_mode && ((context.COMPANY as string) || (context.INSTRUMENT as string))) ||
    "ALL";

  const filteredNews = symbol === "ALL"
    ? DEFAULT_NEWS
    : DEFAULT_NEWS.filter((n) => n.symbol === symbol || n.symbol === "SPY");

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <Newspaper className="w-3.5 h-3.5 text-blue-400" />
          <span>Headlines {symbol !== "ALL" ? `(${symbol})` : ""}</span>
        </div>
        <span className="text-[10px] text-atlas-text-muted">Real-Time Wire</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar divide-y divide-atlas-border-subtle p-1">
        {filteredNews.length === 0 ? (
          <div className="p-4 text-center text-atlas-text-muted italic">No breaking wire headlines for {symbol}.</div>
        ) : (
          filteredNews.map((n) => (
            <div key={n.id} className="p-2 hover:bg-atlas-surface-hover transition-colors">
              <div className="flex items-center justify-between text-[10px] text-atlas-text-muted mb-1">
                <span className="font-bold text-blue-400">{n.symbol}</span>
                <div className="flex items-center gap-2">
                  <span>{n.source}</span>
                  <span>•</span>
                  <span>{n.timeAgo}</span>
                </div>
              </div>
              <p className="text-xs text-atlas-text-primary font-sans leading-snug line-clamp-2">
                {n.headline}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

