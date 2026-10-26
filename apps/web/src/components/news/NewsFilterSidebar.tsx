"use client";

import React, { useState } from "react";
import {
  NewsDatePreset,
  NewsFacetsResponseDTO,
  NewsPublisherDTO,
  NewsSortOrder,
  NewsSourceDTO,
  NewsTopicDTO,
} from "@/lib/news/types";

interface NewsFilterSidebarProps {
  facets: NewsFacetsResponseDTO | null;
  topics: NewsTopicDTO[];
  sources: NewsSourceDTO[];
  publishers: NewsPublisherDTO[];
  selectedTopic: string;
  onTopicChange: (topic: string) => void;
  selectedIndustry: string;
  onIndustryChange: (ind: string) => void;
  selectedSource: string;
  onSourceChange: (src: string) => void;
  selectedPublisher: string;
  onPublisherChange: (pub: string) => void;
  selectedCategory: string;
  onCategoryChange: (cat: string) => void;
  selectedCountry: string;
  onCountryChange: (country: string) => void;
  datePreset: NewsDatePreset;
  onDatePresetChange: (preset: NewsDatePreset) => void;
  sortOrder: NewsSortOrder;
  onSortOrderChange: (sort: NewsSortOrder) => void;
  timelineTimezone: string;
  onTimelineTimezoneChange: (tz: string) => void;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
}

const TIMEZONES = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "America/New_York", label: "EST / EDT (New York)" },
  { value: "America/Chicago", label: "CST / CDT (Chicago)" },
  { value: "America/Los_Angeles", label: "PST / PDT (Los Angeles)" },
  { value: "Europe/London", label: "GMT / BST (London)" },
  { value: "Europe/Frankfurt", label: "CET / CEST (Frankfurt)" },
  { value: "Asia/Kolkata", label: "IST (India - Mumbai)" },
  { value: "Asia/Tokyo", label: "JST (Tokyo)" },
  { value: "Asia/Singapore", label: "SGT (Singapore)" },
  { value: "Asia/Hong_Kong", label: "HKT (Hong Kong)" },
];

export function NewsFilterSidebar({
  facets,
  topics,
  sources,
  publishers,
  selectedTopic,
  onTopicChange,
  selectedIndustry,
  onIndustryChange,
  selectedSource,
  onSourceChange,
  selectedPublisher,
  onPublisherChange,
  selectedCategory,
  onCategoryChange,
  selectedCountry,
  onCountryChange,
  datePreset,
  onDatePresetChange,
  sortOrder,
  onSortOrderChange,
  timelineTimezone,
  onTimelineTimezoneChange,
  onClearFilters,
  hasActiveFilters,
}: NewsFilterSidebarProps) {
  const [openSections, setOpenSections] = useState({
    sort: true,
    date: true,
    topics: true,
    publishers: true,
    categories: false,
    sources: false,
    countries: false,
  });

  const toggleSection = (key: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="flex flex-col space-y-3 font-mono text-xs bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded p-3 shadow-sm select-none">
      {/* Header & Reset */}
      <div className="flex items-center justify-between pb-2 border-b border-zinc-200 dark:border-zinc-800">
        <span className="font-semibold uppercase tracking-wider text-[11px] text-zinc-900 dark:text-zinc-100 flex items-center space-x-1.5">
          <svg className="w-3.5 h-3.5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span>Discovery Filters</span>
        </span>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="text-[10px] text-cyan-600 dark:text-cyan-400 hover:underline flex items-center space-x-1"
          >
            <span>Reset All</span>
          </button>
        )}
      </div>

      {/* 1. Sort Order */}
      <div className="space-y-1">
        <button
          onClick={() => toggleSection("sort")}
          className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
        >
          <span>Sort Relevance & Order</span>
          <span>{openSections.sort ? "−" : "+"}</span>
        </button>
        {openSections.sort && (
          <div className="pt-1 space-y-1">
            <select
              value={sortOrder}
              onChange={(e) => onSortOrderChange(e.target.value as NewsSortOrder)}
              className="w-full px-2 py-1 bg-zinc-50 dark:bg-zinc-800/70 border border-zinc-200 dark:border-zinc-700/60 rounded text-[11px] text-zinc-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            >
              <option value="PUBLISHED_DESC">Published Date (Newest First)</option>
              <option value="PUBLISHED_ASC">Published Date (Oldest First)</option>
              <option value="RELEVANCE_DESC">Search Relevance (Term Match)</option>
            </select>
          </div>
        )}
      </div>

      {/* 2. Publication Date & Timezone */}
      <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800/70 space-y-1">
        <button
          onClick={() => toggleSection("date")}
          className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
        >
          <span>Date Period & Timezone</span>
          <span>{openSections.date ? "−" : "+"}</span>
        </button>
        {openSections.date && (
          <div className="pt-1 space-y-2">
            <div className="grid grid-cols-3 gap-1 text-[10px]">
              {(
                [
                  ["ALL_TIME", "All Time"],
                  ["TODAY", "Today"],
                  ["PAST_24H", "24 Hours"],
                  ["PAST_7D", "7 Days"],
                  ["PAST_30D", "30 Days"],
                ] as const
              ).map(([presetKey, label]) => (
                <button
                  key={presetKey}
                  onClick={() => onDatePresetChange(presetKey)}
                  className={`px-1.5 py-1 text-center rounded border transition-colors ${
                    datePreset === presetKey
                      ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/30 font-semibold"
                      : "bg-zinc-50 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700/50 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Timezone Selection */}
            <div className="pt-1">
              <label className="text-[10px] text-zinc-400 uppercase block mb-0.5">Display Timezone</label>
              <select
                value={timelineTimezone}
                onChange={(e) => onTimelineTimezoneChange(e.target.value)}
                className="w-full px-2 py-1 bg-zinc-50 dark:bg-zinc-800/70 border border-zinc-200 dark:border-zinc-700/60 rounded text-[10px] text-zinc-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz.value} value={tz.value}>
                    {tz.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* 3. Topics Facet */}
      <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800/70 space-y-1">
        <button
          onClick={() => toggleSection("topics")}
          className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
        >
          <span>Canonical Topics {facets?.topics?.length ? `(${facets.topics.length})` : ""}</span>
          <span>{openSections.topics ? "−" : "+"}</span>
        </button>
        {openSections.topics && (
          <div className="pt-1 space-y-1 max-h-48 overflow-y-auto pr-1">
            <div
              onClick={() => onTopicChange("")}
              className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                !selectedTopic
                  ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                  : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
              }`}
            >
              <span>All Topics</span>
            </div>
            {facets?.topics && facets.topics.length > 0
              ? facets.topics.map((t) => (
                  <div
                    key={t.key}
                    onClick={() => onTopicChange(selectedTopic === t.key ? "" : t.key)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedTopic === t.key
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{t.label}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono">
                      {t.count}
                    </span>
                  </div>
                ))
              : topics.map((t) => (
                  <div
                    key={t.topic_id}
                    onClick={() => onTopicChange(selectedTopic === t.topic_id ? "" : t.topic_id)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedTopic === t.topic_id
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{t.name}</span>
                  </div>
                ))}
          </div>
        )}
      </div>

      {/* 4. Publishers Facet */}
      <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800/70 space-y-1">
        <button
          onClick={() => toggleSection("publishers")}
          className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
        >
          <span>Publishers {facets?.publishers?.length ? `(${facets.publishers.length})` : ""}</span>
          <span>{openSections.publishers ? "−" : "+"}</span>
        </button>
        {openSections.publishers && (
          <div className="pt-1 space-y-1 max-h-40 overflow-y-auto pr-1">
            <div
              onClick={() => onPublisherChange("")}
              className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                !selectedPublisher
                  ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                  : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
              }`}
            >
              <span>All Publishers</span>
            </div>
            {facets?.publishers && facets.publishers.length > 0
              ? facets.publishers.map((p) => (
                  <div
                    key={p.key}
                    onClick={() => onPublisherChange(selectedPublisher === p.key ? "" : p.key)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedPublisher === p.key
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{p.label}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono">
                      {p.count}
                    </span>
                  </div>
                ))
              : publishers.map((p) => (
                  <div
                    key={p.publisher_id}
                    onClick={() => onPublisherChange(selectedPublisher === p.publisher_id ? "" : p.publisher_id)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedPublisher === p.publisher_id
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{p.canonical_name}</span>
                  </div>
                ))}
          </div>
        )}
      </div>

      {/* 5. Sources Facet */}
      <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800/70 space-y-1">
        <button
          onClick={() => toggleSection("sources")}
          className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
        >
          <span>Source Providers {facets?.sources?.length ? `(${facets.sources.length})` : ""}</span>
          <span>{openSections.sources ? "−" : "+"}</span>
        </button>
        {openSections.sources && (
          <div className="pt-1 space-y-1 max-h-36 overflow-y-auto pr-1">
            <div
              onClick={() => onSourceChange("")}
              className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                !selectedSource
                  ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                  : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
              }`}
            >
              <span>All Sources</span>
            </div>
            {facets?.sources && facets.sources.length > 0
              ? facets.sources.map((s) => (
                  <div
                    key={s.key}
                    onClick={() => onSourceChange(selectedSource === s.key ? "" : s.key)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedSource === s.key
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{s.label}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono">
                      {s.count}
                    </span>
                  </div>
                ))
              : sources.map((s) => (
                  <div
                    key={s.source_id}
                    onClick={() => onSourceChange(selectedSource === s.source_id ? "" : s.source_id)}
                    className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                      selectedSource === s.source_id
                        ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                    }`}
                  >
                    <span className="truncate pr-2">{s.provider_name}</span>
                  </div>
                ))}
          </div>
        )}
      </div>

      {/* 6. Geographic Regions Facet */}
      {facets?.countries && facets.countries.length > 0 && (
        <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800/70 space-y-1">
          <button
            onClick={() => toggleSection("countries")}
            className="w-full flex items-center justify-between text-zinc-500 dark:text-zinc-400 uppercase text-[10px] font-semibold tracking-wider hover:text-zinc-800 dark:hover:text-zinc-200"
          >
            <span>Geographic Regions ({facets.countries.length})</span>
            <span>{openSections.countries ? "−" : "+"}</span>
          </button>
          {openSections.countries && (
            <div className="pt-1 space-y-1 max-h-36 overflow-y-auto pr-1">
              <div
                onClick={() => onCountryChange("")}
                className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                  !selectedCountry
                    ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                    : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                }`}
              >
                <span>All Countries</span>
              </div>
              {facets.countries.map((c) => (
                <div
                  key={c.key}
                  onClick={() => onCountryChange(selectedCountry === c.key ? "" : c.key)}
                  className={`flex items-center justify-between px-2 py-1 rounded cursor-pointer transition-colors text-[11px] ${
                    selectedCountry === c.key
                      ? "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold"
                      : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/60"
                  }`}
                >
                  <span className="truncate pr-2">{c.label}</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-200 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 font-mono">
                    {c.count}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
