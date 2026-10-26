"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useNewsDiscovery } from "@/hooks/news/useNewsDiscovery";
import { NewsHeader } from "./NewsHeader";
import { NewsCategoryTabs } from "./NewsCategoryTabs";
import { NewsSearchSuggestions } from "./NewsSearchSuggestions";
import { NewsFilterSidebar } from "./NewsFilterSidebar";
import { NewsFeedTable } from "./NewsFeedTable";
import { NewsTimeline } from "./NewsTimeline";
import { NewsArticlePreview } from "./NewsArticlePreview";
import { NewsCoverageModal } from "./NewsCoverageModal";
import { NewsEmptyState } from "./NewsEmptyState";
import { LayoutList, Clock, SlidersHorizontal } from "lucide-react";

export function NewsWorkspace() {
  const router = useRouter();
  const [isCoverageOpen, setIsCoverageOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const {
    mode,
    setMode,
    view,
    setView,
    articles,
    selectedArticle,
    setSelectedArticle,
    totalCount,
    hasMore,
    isLoading,
    isRefreshing,
    error,
    searchQuery,
    setSearchQuery,
    selectedTopic,
    setSelectedTopic,
    selectedIndustry,
    setSelectedIndustry,
    selectedSource,
    setSelectedSource,
    selectedPublisher,
    setSelectedPublisher,
    selectedCountry,
    setSelectedCountry,
    selectedCategory,
    setSelectedCategory,
    datePreset,
    setDatePreset,
    sortOrder,
    setSortOrder,
    timelineInterval,
    setTimelineInterval,
    timelineTimezone,
    setTimelineTimezone,
    timelineData,
    facets,
    topics,
    sources,
    publishers,
    coverage,
    status,
    suggestions,
    isSuggestionsLoading,
    fetchSuggestions,
    loadNextPage,
    refresh,
    clearFilters,
    hasActiveFilters,
  } = useNewsDiscovery();

  const handleNavigateEntity = (entityId: string, entityType: string, ticker?: string | null) => {
    if (entityType === "COMPANY") {
      router.push(`/companies?entity=${encodeURIComponent(entityId)}`);
    } else if (entityType === "INSTRUMENT" && ticker) {
      router.push(`/markets?symbol=${encodeURIComponent(ticker)}`);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50/50 dark:bg-zinc-950 p-3 sm:p-5 lg:p-6 space-y-3.5 max-w-[1920px] mx-auto font-sans">
      {/* Top Header */}
      <NewsHeader
        status={status}
        totalArticles={coverage?.total_articles ?? totalCount}
        isRefreshing={isRefreshing}
        onRefresh={refresh}
        onOpenCoverage={() => setIsCoverageOpen(true)}
      />

      {/* Discovery Mode Switcher */}
      <NewsCategoryTabs activeTab={mode} onTabChange={setMode} />

      {/* Discovery Control Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
        {/* Left: Search with Autocomplete */}
        <div className="w-full sm:w-96 md:w-[450px]">
          <NewsSearchSuggestions
            query={searchQuery}
            onQueryChange={(q) => {
              setSearchQuery(q);
              fetchSuggestions(q);
            }}
            suggestions={suggestions}
            isLoading={isSuggestionsLoading}
            onSelectSuggestion={(s) => {
              if (s.suggestion_type === "TOPIC") {
                setSelectedTopic(s.key);
                setSearchQuery("");
              } else if (s.suggestion_type === "PUBLISHER") {
                setSelectedPublisher(s.key);
                setSearchQuery("");
              } else if (s.suggestion_type === "CATEGORY") {
                setSelectedCategory(s.key);
                setSearchQuery("");
              } else {
                setSearchQuery(s.label);
              }
            }}
          />
        </div>

        {/* Right: View Toggle (Feed vs Timeline) & Sidebar Toggle */}
        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center rounded border border-zinc-200 dark:border-zinc-800 p-0.5 bg-zinc-50 dark:bg-zinc-950 text-xs font-mono">
            <button
              onClick={() => setView("FEED")}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded transition-colors ${
                view === "FEED"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <LayoutList className="w-3.5 h-3.5" />
              <span>Feed Table</span>
            </button>
            <button
              onClick={() => setView("TIMELINE")}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded transition-colors ${
                view === "TIMELINE"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Chronological Timeline</span>
            </button>
          </div>

          {/* Sidebar Toggle */}
          <button
            onClick={() => setIsSidebarOpen((prev) => !prev)}
            className={`flex items-center space-x-1 px-2.5 py-1 text-xs font-mono rounded border transition-colors ${
              isSidebarOpen
                ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 border-zinc-300 dark:border-zinc-700"
                : "bg-white dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800/60"
            }`}
            title="Toggle Filter Sidebar"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Filters</span>
            {hasActiveFilters && (
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
            )}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {error ? (
        <NewsEmptyState isError={true} errorMessage={error} onRetry={refresh} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
          {/* Left: Filter Sidebar (Optional / Responsive) */}
          {isSidebarOpen && (
            <div className="lg:col-span-3 xl:col-span-3 sticky top-4">
              <NewsFilterSidebar
                facets={facets}
                topics={topics}
                sources={sources}
                publishers={publishers}
                selectedTopic={selectedTopic}
                onTopicChange={setSelectedTopic}
                selectedIndustry={selectedIndustry}
                onIndustryChange={setSelectedIndustry}
                selectedSource={selectedSource}
                onSourceChange={setSelectedSource}
                selectedPublisher={selectedPublisher}
                onPublisherChange={setSelectedPublisher}
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
                selectedCountry={selectedCountry}
                onCountryChange={setSelectedCountry}
                datePreset={datePreset}
                onDatePresetChange={setDatePreset}
                sortOrder={sortOrder}
                onSortOrderChange={setSortOrder}
                timelineTimezone={timelineTimezone}
                onTimelineTimezoneChange={setTimelineTimezone}
                onClearFilters={clearFilters}
                hasActiveFilters={hasActiveFilters}
              />
            </div>
          )}

          {/* Middle: Results (Feed Table or Timeline) */}
          <div
            className={`${
              isSidebarOpen
                ? "lg:col-span-5 xl:col-span-5"
                : "lg:col-span-7 xl:col-span-8"
            } flex flex-col min-w-0`}
          >
            {view === "FEED" ? (
              articles.length === 0 && !isLoading ? (
                <NewsEmptyState
                  hasFilters={hasActiveFilters}
                  onClearFilters={clearFilters}
                />
              ) : (
                <NewsFeedTable
                  articles={articles}
                  selectedArticle={selectedArticle}
                  onSelectArticle={setSelectedArticle}
                  totalCount={totalCount}
                  hasMore={hasMore}
                  isLoading={isLoading}
                  onLoadMore={loadNextPage}
                  onNavigateEntity={handleNavigateEntity}
                />
              )
            ) : (
              <NewsTimeline
                timelineData={timelineData}
                selectedArticle={selectedArticle}
                onSelectArticle={setSelectedArticle}
                interval={timelineInterval}
                onIntervalChange={setTimelineInterval}
                timezone={timelineTimezone}
                isLoading={isLoading}
                onNavigateEntity={handleNavigateEntity}
              />
            )}
          </div>

          {/* Right: Article Inspector */}
          <div
            className={`${
              isSidebarOpen
                ? "lg:col-span-4 xl:col-span-4"
                : "lg:col-span-5 xl:col-span-4"
            } sticky top-4`}
          >
            <NewsArticlePreview
              article={selectedArticle}
              onNavigateEntity={handleNavigateEntity}
            />
          </div>
        </div>
      )}

      {/* Coverage Modal */}
      <NewsCoverageModal
        isOpen={isCoverageOpen}
        onClose={() => setIsCoverageOpen(false)}
        coverage={coverage}
        sources={sources}
        publishers={publishers}
      />
    </div>
  );
}
