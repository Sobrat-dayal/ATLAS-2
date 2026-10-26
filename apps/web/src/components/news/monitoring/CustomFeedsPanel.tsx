"use client";

import React, { useState } from "react";
import {
  CreateCustomNewsFeedDTO,
  CustomNewsFeedDTO,
  NewsArticleDTO,
} from "@/lib/news/types";
import { formatRelativeTime } from "@/lib/news/formatting";
import {
  Filter,
  Plus,
  Trash2,
  Play,
  Layers,
  Sparkles,
  ExternalLink,
  X,
  Save,
  Search,
} from "lucide-react";

interface CustomFeedsPanelProps {
  customFeeds: CustomNewsFeedDTO[];
  selectedFeed: CustomNewsFeedDTO | null;
  feedArticles: NewsArticleDTO[];
  isLoading: boolean;
  onSelectFeed: (feed: CustomNewsFeedDTO) => void;
  onCreateFeed: (dto: CreateCustomNewsFeedDTO) => Promise<CustomNewsFeedDTO>;
  onDeleteFeed: (feedId: string) => Promise<void>;
  onExecuteFeed: (feedId: string) => Promise<void>;
}

export function CustomFeedsPanel({
  customFeeds,
  selectedFeed,
  feedArticles,
  isLoading,
  onSelectFeed,
  onCreateFeed,
  onDeleteFeed,
  onExecuteFeed,
}: CustomFeedsPanelProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [category, setCategory] = useState("TECHNOLOGY");
  const [isAlertEnabled, setIsAlertEnabled] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreateFeed({
        title,
        description: description || null,
        query_config: {
          q: searchQuery || undefined,
          category: category || undefined,
        },
        is_alert_enabled: isAlertEnabled,
        priority: "HIGH",
      });
      setIsCreateOpen(false);
      setTitle("");
      setDescription("");
      setSearchQuery("");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, feedId: string) => {
    e.stopPropagation();
    if (confirm("Delete this custom news feed?")) {
      await onDeleteFeed(feedId);
    }
  };

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Top Bar */}
      <div className="p-3.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-indigo-500" />
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Custom News Feeds
          </h2>
          <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[11px] text-zinc-600 dark:text-zinc-400">
            {customFeeds.length} saved
          </span>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Custom Feed</span>
        </button>
      </div>

      {/* Main Grid: Feeds Cards & Active Feed Articles */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Left: Feeds Cards (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          {customFeeds.length === 0 ? (
            <div className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center text-zinc-500">
              <p>No custom feeds configured yet.</p>
            </div>
          ) : (
            customFeeds.map((feed) => {
              const isSelected = selectedFeed?.feed_id === feed.feed_id;
              const qConfig = feed.query_config as Record<string, string>;
              return (
                <div
                  key={feed.feed_id}
                  onClick={() => {
                    onSelectFeed(feed);
                    onExecuteFeed(feed.feed_id);
                  }}
                  className={`p-3.5 rounded border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-indigo-50/20 dark:bg-indigo-950/20 border-indigo-500/50 shadow-sm"
                      : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-zinc-900 dark:text-zinc-100 text-sm">
                          {feed.title}
                        </span>
                        {feed.is_alert_enabled && (
                          <span className="px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 text-[10px]">
                            Alerts Active
                          </span>
                        )}
                      </div>
                      {feed.description && (
                        <p className="text-[11px] text-zinc-500 dark:text-zinc-400">
                          {feed.description}
                        </p>
                      )}
                    </div>

                    <button
                      onClick={(e) => handleDelete(e, feed.feed_id)}
                      className="p-1 rounded text-zinc-400 hover:text-rose-500 transition-colors"
                      title="Delete Feed"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Query Criteria Chips */}
                  <div className="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-zinc-100 dark:border-zinc-800 text-[11px]">
                    {qConfig.q && (
                      <span className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                        q: &ldquo;{qConfig.q}&rdquo;
                      </span>
                    )}
                    {qConfig.category && (
                      <span className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                        cat: {qConfig.category}
                      </span>
                    )}
                    <span className="ml-auto text-[10px] text-zinc-400">
                      Updated {formatRelativeTime(feed.updated_at)}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Executed Feed Articles (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-500" />
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
                {selectedFeed ? `Articles for: ${selectedFeed.title}` : "Select a Custom Feed"}
              </h3>
            </div>
            {selectedFeed && (
              <button
                onClick={() => onExecuteFeed(selectedFeed.feed_id)}
                className="flex items-center space-x-1 px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300"
              >
                <Play className="w-3 h-3 text-emerald-500 fill-current" />
                <span>Re-query</span>
              </button>
            )}
          </div>

          {feedArticles.length === 0 ? (
            <div className="p-8 text-center text-zinc-500">
              <p>Select a feed on the left to inspect currently matching articles.</p>
            </div>
          ) : (
            <div className="divide-y divide-zinc-200 dark:divide-zinc-800 max-h-[600px] overflow-y-auto">
              {feedArticles.map((art) => (
                <div key={art.article_id} className="py-3 space-y-1">
                  <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                    <a
                      href={art.canonical_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-indigo-600 dark:hover:text-indigo-400 flex items-center space-x-1"
                    >
                      <span>{art.headline}</span>
                      <ExternalLink className="w-3 h-3 inline ml-1 opacity-70" />
                    </a>
                  </div>
                  <div className="text-[10px] text-zinc-500 flex items-center space-x-2">
                    <span className="font-medium text-zinc-700 dark:text-zinc-300">
                      {art.publisher_name}
                    </span>
                    <span>•</span>
                    <span>{formatRelativeTime(art.published_at)}</span>
                    <span>•</span>
                    <span>{art.article_type}</span>
                  </div>
                  {art.permitted_excerpt && (
                    <p className="text-[11px] text-zinc-600 dark:text-zinc-400 line-clamp-2">
                      {art.permitted_excerpt}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl w-full max-w-lg p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 uppercase">
                Create Custom News Feed
              </h3>
              <button
                onClick={() => setIsCreateOpen(false)}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block font-semibold mb-1">Feed Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Semiconductor Supply Chain"
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Dedicated feed tracking TSMC, ASML, and semiconductor manufacturing"
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Search Keywords (q)</label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="semiconductor chips foundry"
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                />
              </div>

              <div>
                <label className="block font-semibold mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                >
                  <option value="TECHNOLOGY">TECHNOLOGY</option>
                  <option value="COMPANY">COMPANY</option>
                  <option value="EQUITIES">EQUITIES</option>
                  <option value="ECONOMICS">ECONOMICS</option>
                  <option value="GENERAL_FINANCIAL">GENERAL_FINANCIAL</option>
                </select>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="feed-alert-toggle"
                  checked={isAlertEnabled}
                  onChange={(e) => setIsAlertEnabled(e.target.checked)}
                  className="rounded text-indigo-600"
                />
                <label htmlFor="feed-alert-toggle" className="font-semibold">
                  Enable Rule & Alert Integration for this Feed
                </label>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-zinc-200 dark:border-zinc-800">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-3 py-1.5 rounded border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Creating..." : "Save Feed"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
