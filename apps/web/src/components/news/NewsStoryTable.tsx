"use client";

import { formatRelativeTime } from "@/lib/news/formatting";
import {
  GitMerge,
  Layers,
  Building2,
  ExternalLink,
  CheckCircle2,
  Clock,
  Archive,
  AlertCircle,
} from "lucide-react";
import { NewsStoryThreadDTO, NewsStoryStatus } from "@/lib/news/types";

interface NewsStoryTableProps {
  stories: NewsStoryThreadDTO[];
  selectedStory: NewsStoryThreadDTO | null;
  onSelectStory: (story: NewsStoryThreadDTO) => void;
  isLoading: boolean;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
}

export function NewsStoryTable({
  stories,
  selectedStory,
  onSelectStory,
  isLoading,
  onNavigateEntity,
}: NewsStoryTableProps) {
  if (isLoading && stories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center">
        <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-mono text-zinc-500 dark:text-zinc-400">
          Clustering multi-source coverage threads...
        </p>
      </div>
    );
  }

  if (stories.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded">
        <Layers className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">
          No Story Threads Found
        </h3>
        <p className="text-xs text-zinc-500 mt-1">
          No developing story threads match the active filters or time boundary.
        </p>
      </div>
    );
  }

  const getStatusBadge = (status: NewsStoryStatus) => {
    switch (status) {
      case "ACTIVE":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1 animate-pulse" />
            ACTIVE
          </span>
        );
      case "DEVELOPING":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
            <Clock className="w-2.5 h-2.5 mr-1" />
            DEVELOPING
          </span>
        );
      case "QUIET":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border border-zinc-500/20">
            QUIET
          </span>
        );
      case "MERGED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <GitMerge className="w-2.5 h-2.5 mr-1" />
            MERGED
          </span>
        );
      case "ARCHIVED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-500/10 text-zinc-500 border border-zinc-500/20">
            <Archive className="w-2.5 h-2.5 mr-1" />
            ARCHIVED
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="overflow-x-auto bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/80 dark:bg-zinc-900/80 text-[11px] font-mono text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            <th className="py-2.5 px-3 font-semibold">Story Thread / Lead Headline</th>
            <th className="py-2.5 px-3 font-semibold w-48">Primary Subject</th>
            <th className="py-2.5 px-3 font-semibold w-28 text-center">Coverage</th>
            <th className="py-2.5 px-3 font-semibold w-28 text-center">Independent</th>
            <th className="py-2.5 px-3 font-semibold w-32">Latest Update</th>
            <th className="py-2.5 px-3 font-semibold w-24 text-right">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/60 text-xs font-sans">
          {stories.map((story) => {
            const isSelected = selectedStory?.story_id === story.story_id;
            const timeAgo = formatRelativeTime(story.latest_source_published_at);

            return (
              <tr
                key={story.story_id}
                onClick={() => onSelectStory(story)}
                className={`cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-cyan-50/70 dark:bg-cyan-950/30 border-l-2 border-l-cyan-500"
                    : "hover:bg-zinc-50/70 dark:hover:bg-zinc-800/40"
                }`}
              >
                {/* Title & Topic Tag */}
                <td className="py-3 px-3">
                  <div className="flex flex-col space-y-1">
                    <span className="font-medium text-zinc-900 dark:text-zinc-100 line-clamp-2 leading-snug">
                      {story.display_title}
                    </span>
                    <div className="flex items-center space-x-2 text-[10px] font-mono text-zinc-500 dark:text-zinc-400">
                      <span className="text-zinc-400 dark:text-zinc-500">{story.story_id}</span>
                      {story.canonical_topic_label && (
                        <>
                          <span>•</span>
                          <span className="text-cyan-600 dark:text-cyan-400 font-medium">
                            {story.canonical_topic_label.replace(/_/g, " ")}
                          </span>
                        </>
                      )}
                      {story.linked_event_ids.length > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-amber-600 dark:text-amber-400 font-semibold">
                            {story.linked_event_ids.length} Linked Event
                            {story.linked_event_ids.length > 1 ? "s" : ""}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </td>

                {/* Primary Subject */}
                <td className="py-3 px-3">
                  {story.primary_entity_name ? (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (story.primary_entity_id && onNavigateEntity) {
                          onNavigateEntity(story.primary_entity_id, "COMPANY");
                        }
                      }}
                      className="inline-flex items-center space-x-1.5 text-zinc-800 dark:text-zinc-200 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors font-medium text-left"
                    >
                      <Building2 className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                      <span className="truncate max-w-[150px]">{story.primary_entity_name}</span>
                    </button>
                  ) : (
                    <span className="text-zinc-400 font-mono text-[11px]">—</span>
                  )}
                </td>

                {/* Article Count */}
                <td className="py-3 px-3 text-center">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                    {story.article_count} {story.article_count === 1 ? "report" : "reports"}
                  </span>
                </td>

                {/* Independent Publisher Count */}
                <td className="py-3 px-3 text-center">
                  <span
                    className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 border border-cyan-500/20"
                    title={`${story.independent_publisher_count} verified independent publishing newsrooms`}
                  >
                    {story.independent_publisher_count} source
                    {story.independent_publisher_count > 1 ? "s" : ""}
                  </span>
                </td>

                {/* Latest Update Time */}
                <td className="py-3 px-3 font-mono text-[11px] text-zinc-600 dark:text-zinc-400 whitespace-nowrap">
                  {timeAgo}
                </td>

                {/* Status */}
                <td className="py-3 px-3 text-right">{getStatusBadge(story.story_status)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
