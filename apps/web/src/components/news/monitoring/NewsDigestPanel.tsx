"use client";

import React, { useState } from "react";
import {
  CreateNewsDigestSubscriptionDTO,
  NewsDigestCadence,
  NewsDigestRunDTO,
  NewsDigestSubscriptionDTO,
} from "@/lib/news/types";
import { formatFullUtcTime, formatRelativeTime } from "@/lib/news/formatting";
import {
  Calendar,
  Plus,
  Play,
  Eye,
  Trash2,
  CheckCircle2,
  Clock,
  Mail,
  Bell,
  Sparkles,
  Layers,
  X,
  ShieldCheck,
} from "lucide-react";

interface NewsDigestPanelProps {
  digests: NewsDigestSubscriptionDTO[];
  selectedDigest: NewsDigestSubscriptionDTO | null;
  digestPreview: NewsDigestRunDTO | null;
  digestHistory: NewsDigestRunDTO[];
  isLoading: boolean;
  onSelectDigest: (digest: NewsDigestSubscriptionDTO) => void;
  onCreateDigest: (dto: CreateNewsDigestSubscriptionDTO) => Promise<NewsDigestSubscriptionDTO>;
  onDeleteDigest: (digestId: string) => Promise<void>;
  onPreviewDigest: (digestId: string) => Promise<NewsDigestRunDTO>;
  onTriggerDigest: (digestId: string) => Promise<NewsDigestRunDTO>;
  onLoadHistory: (digestId: string) => Promise<void>;
}

export function NewsDigestPanel({
  digests,
  selectedDigest,
  digestPreview,
  digestHistory,
  isLoading,
  onSelectDigest,
  onCreateDigest,
  onDeleteDigest,
  onPreviewDigest,
  onTriggerDigest,
  onLoadHistory,
}: NewsDigestPanelProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [isTriggering, setIsTriggering] = useState<string | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [cadence, setCadence] = useState<NewsDigestCadence>("DAILY");
  const [scheduleTime, setScheduleTime] = useState("07:00");
  const [timezone, setTimezone] = useState("America/New_York");
  const [topStoriesLimit, setTopStoriesLimit] = useState(10);
  const [includeEventHighlights, setIncludeEventHighlights] = useState(true);
  const [includeSentimentSummary, setIncludeSentimentSummary] = useState(true);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await onCreateDigest({
        title,
        cadence,
        schedule_cron_or_time: scheduleTime,
        timezone,
        top_stories_limit: topStoriesLimit,
        include_event_highlights: includeEventHighlights,
        include_sentiment_summary: includeSentimentSummary,
        delivery_channels: ["IN_APP", "DURABLE_NOTIFICATION"],
      });
      setIsCreateOpen(false);
      setTitle("");
    } catch {
      // create error
    }
  };

  const handlePreview = async (digestId: string) => {
    await onPreviewDigest(digestId);
    setIsPreviewOpen(true);
  };

  const handleTrigger = async (digestId: string) => {
    setIsTriggering(digestId);
    try {
      await onTriggerDigest(digestId);
    } finally {
      setIsTriggering(null);
    }
  };

  const handleDelete = async (e: React.MouseEvent, digestId: string) => {
    e.stopPropagation();
    if (confirm("Delete this scheduled news digest subscription?")) {
      await onDeleteDigest(digestId);
    }
  };

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Top Header */}
      <div className="p-3.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-violet-500" />
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider">
            Scheduled Institutional News Digests
          </h2>
          <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[11px] text-zinc-600 dark:text-zinc-400">
            {digests.length} subscriptions
          </span>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-violet-600 hover:bg-violet-500 text-white font-semibold transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Digest</span>
        </button>
      </div>

      {/* Main Grid: Digest Cards & Run History */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* Left: Digests (6 cols) */}
        <div className="lg:col-span-6 space-y-3">
          {digests.length === 0 ? (
            <div className="p-8 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center text-zinc-500">
              <p>No news digest subscriptions configured.</p>
            </div>
          ) : (
            digests.map((digest) => {
              const isSelected = selectedDigest?.digest_id === digest.digest_id;
              const isBusy = isTriggering === digest.digest_id;
              return (
                <div
                  key={digest.digest_id}
                  onClick={() => {
                    onSelectDigest(digest);
                    onLoadHistory(digest.digest_id);
                  }}
                  className={`p-4 rounded border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-violet-50/20 dark:bg-violet-950/20 border-violet-500/50 shadow-sm"
                      : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-zinc-900 dark:text-zinc-100 text-sm">
                          {digest.title}
                        </span>
                        <span className="px-1.5 py-0.2 rounded bg-violet-500/10 text-violet-600 dark:text-violet-400 border border-violet-500/20 text-[10px] font-semibold">
                          {digest.cadence}
                        </span>
                      </div>
                      <div className="text-[11px] text-zinc-500 mt-1 flex items-center space-x-2">
                        <Clock className="w-3 h-3 text-zinc-400" />
                        <span>
                          {digest.schedule_cron_or_time} ({digest.timezone})
                        </span>
                        <span>•</span>
                        <span>Top {digest.top_stories_limit} stories</span>
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDelete(e, digest.digest_id)}
                      className="p-1 rounded text-zinc-400 hover:text-rose-500 transition-colors"
                      title="Delete Digest"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Highlights and Options */}
                  <div className="flex flex-wrap gap-2 mt-3 pt-2 border-t border-zinc-100 dark:border-zinc-800 text-[11px] text-zinc-600 dark:text-zinc-400">
                    {digest.include_event_highlights && (
                      <span className="flex items-center space-x-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                        <span>Events</span>
                      </span>
                    )}
                    {digest.include_sentiment_summary && (
                      <span className="flex items-center space-x-1">
                        <Sparkles className="w-3 h-3 text-purple-500" />
                        <span>Sentiment</span>
                      </span>
                    )}
                    <span className="ml-auto text-[10px] text-zinc-400">
                      Dispatched {digest.total_runs_count} times
                    </span>
                  </div>

                  {/* Actions Bar */}
                  <div className="flex items-center justify-end space-x-2 mt-3 pt-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreview(digest.digest_id);
                      }}
                      className="flex items-center space-x-1 px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold transition-colors"
                    >
                      <Eye className="w-3 h-3 text-violet-500" />
                      <span>Preview</span>
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTrigger(digest.digest_id);
                      }}
                      disabled={isBusy}
                      className="flex items-center space-x-1 px-3 py-1 rounded bg-violet-600 hover:bg-violet-500 text-white font-bold transition-colors disabled:opacity-50"
                    >
                      <Play className="w-3 h-3 fill-current" />
                      <span>{isBusy ? "Dispatching..." : "Trigger Now"}</span>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: Selected Digest Run History (6 cols) */}
        <div className="lg:col-span-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
            <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">
              {selectedDigest
                ? `Dispatch History: ${selectedDigest.title}`
                : "Select a Digest to view History"}
            </h3>
            {selectedDigest && (
              <button
                onClick={() => onLoadHistory(selectedDigest.digest_id)}
                className="text-[11px] text-violet-500 hover:underline"
              >
                Refresh History
              </button>
            )}
          </div>

          {digestHistory.length === 0 ? (
            <div className="p-8 text-center text-zinc-500">
              <p>No dispatch runs recorded for this digest yet.</p>
            </div>
          ) : (
            <div className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {digestHistory.map((run) => (
                <div key={run.run_id} className="py-2.5 flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                        {formatFullUtcTime(run.started_at)}
                      </span>
                      <span
                        className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                          run.status === "DISPATCHED"
                            ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20"
                            : "bg-zinc-200 dark:bg-zinc-800 text-zinc-600"
                        }`}
                      >
                        {run.status}
                      </span>
                    </div>
                    <div className="text-[10px] text-zinc-500 flex items-center space-x-2">
                      <span>{run.total_articles_included} articles</span>
                      <span>•</span>
                      <span>Idempotency: {run.idempotency_token.slice(0, 16)}...</span>
                    </div>
                  </div>

                  <span className="text-[10px] text-zinc-400">
                    {formatRelativeTime(run.started_at)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {isPreviewOpen && digestPreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[85vh] p-5 flex flex-col overflow-hidden space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 uppercase">
                News Digest Preview (Non-Dispatch Mode)
              </h3>
              <button
                onClick={() => setIsPreviewOpen(false)}
                className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 bg-violet-50/30 dark:bg-violet-950/30 border border-violet-500/20 rounded flex items-center justify-between text-xs">
              <span>
                Total Eligible Articles: <strong>{digestPreview.total_articles_included}</strong>
              </span>
              <span>
                Top Stories: <strong>{digestPreview.top_stories_included.length}</strong>
              </span>
              <span>
                Status: <strong>{digestPreview.status}</strong>
              </span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3">
              <h4 className="font-semibold text-zinc-900 dark:text-zinc-100 text-xs">
                Top Story Inclusions
              </h4>
              {digestPreview.top_stories_included.map((story: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 space-y-1"
                >
                  <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                    {story.title || story.headline}
                  </div>
                  {story.summary && (
                    <p className="text-[11px] text-zinc-600 dark:text-zinc-400">
                      {story.summary}
                    </p>
                  )}
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800 flex justify-end">
              <button
                onClick={() => setIsPreviewOpen(false)}
                className="px-4 py-1.5 rounded bg-zinc-200 dark:bg-zinc-800 hover:bg-zinc-300 dark:hover:bg-zinc-700 font-semibold"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-xl w-full max-w-lg p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 uppercase">
                Create Scheduled News Digest
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
                <label className="block font-semibold mb-1">Digest Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Daily Markets & Tech Morning Intelligence"
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1">Cadence</label>
                  <select
                    value={cadence}
                    onChange={(e) => setCadence(e.target.value as NewsDigestCadence)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  >
                    <option value="DAILY">DAILY</option>
                    <option value="WEEKLY">WEEKLY</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1">Schedule Time</label>
                  <input
                    type="time"
                    value={scheduleTime}
                    onChange={(e) => setScheduleTime(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1">Timezone</label>
                  <select
                    value={timezone}
                    onChange={(e) => setTimezone(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  >
                    <option value="America/New_York">America/New_York (ET)</option>
                    <option value="Europe/London">Europe/London (GMT/BST)</option>
                    <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1">Top Stories Limit</label>
                  <input
                    type="number"
                    min="3"
                    max="50"
                    value={topStoriesLimit}
                    onChange={(e) => setTopStoriesLimit(parseInt(e.target.value) || 10)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  />
                </div>
              </div>

              <div className="space-y-1.5 pt-1">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={includeEventHighlights}
                    onChange={(e) => setIncludeEventHighlights(e.target.checked)}
                    className="rounded text-violet-600"
                  />
                  <span>Include Financial Event Highlights</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={includeSentimentSummary}
                    onChange={(e) => setIncludeSentimentSummary(e.target.checked)}
                    className="rounded text-violet-600"
                  />
                  <span>Include Target-Aware Sentiment Summary</span>
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
                  className="px-4 py-1.5 rounded bg-violet-600 hover:bg-violet-500 text-white font-bold transition-colors"
                >
                  Subscribe Digest
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
