"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useNewsDiscovery } from "@/hooks/news/useNewsDiscovery";
import { useNewsStories } from "@/hooks/news/useNewsStories";
import { useFinancialEvents } from "@/hooks/news/useFinancialEvents";
import { NewsHeader } from "./NewsHeader";
import { NewsCategoryTabs } from "./NewsCategoryTabs";
import { NewsSearchSuggestions } from "./NewsSearchSuggestions";
import { NewsFilterSidebar } from "./NewsFilterSidebar";
import { NewsFeedTable } from "./NewsFeedTable";
import { NewsTimeline } from "./NewsTimeline";
import { NewsArticlePreview } from "./NewsArticlePreview";
import { NewsCoverageModal } from "./NewsCoverageModal";
import { NewsEmptyState } from "./NewsEmptyState";
import { NewsStoryTable } from "./NewsStoryTable";
import { NewsStoryInspector } from "./NewsStoryInspector";
import { NewsFinancialEventTable } from "./NewsFinancialEventTable";
import { NewsEventInspector } from "./NewsEventInspector";
import { NewsSentimentWorkspace } from "./sentiment/NewsSentimentWorkspace";
import { LayoutList, Clock, SlidersHorizontal, Layers, ShieldCheck, BarChart3 } from "lucide-react";

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

  // Stage 101 Story & Event hooks
  const storyHook = useNewsStories();
  const eventHook = useFinancialEvents();

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
        onRefresh={() => {
          refresh();
          storyHook.refresh();
          eventHook.refresh();
        }}
        onOpenCoverage={() => setIsCoverageOpen(true)}
      />

      {/* Discovery Mode Switcher */}
      <NewsCategoryTabs activeTab={mode} onTabChange={setMode} />

      {/* Discovery Control Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
        {/* Left: Search with Autocomplete */}
        <div className="w-full sm:w-80 md:w-[420px]">
          <NewsSearchSuggestions
            query={searchQuery}
            onQueryChange={(q) => {
              setSearchQuery(q);
              fetchSuggestions(q);
              storyHook.setSearchQuery(q);
              eventHook.setSearchQuery(q);
            }}
            suggestions={suggestions}
            isLoading={isSuggestionsLoading}
            onSelectSuggestion={(s) => {
              if (s.suggestion_type === "TOPIC") {
                setSelectedTopic(s.key);
                storyHook.setTopicFilter(s.key);
                setSearchQuery("");
              } else if (s.suggestion_type === "PUBLISHER") {
                setSelectedPublisher(s.key);
                storyHook.setPublisherFilter(s.key);
                setSearchQuery("");
              } else if (s.suggestion_type === "CATEGORY") {
                setSelectedCategory(s.key);
                setSearchQuery("");
              } else {
                setSearchQuery(s.label);
                storyHook.setSearchQuery(s.label);
                eventHook.setSearchQuery(s.label);
              }
            }}
          />
        </div>

        {/* Right: View Toggle (Feed vs Stories vs Events vs Timeline) & Sidebar Toggle */}
        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center rounded border border-zinc-200 dark:border-zinc-800 p-0.5 bg-zinc-50 dark:bg-zinc-950 text-xs font-mono">
            <button
              onClick={() => setView("FEED")}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded transition-colors ${
                view === "FEED"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <LayoutList className="w-3.5 h-3.5" />
              <span>Headlines</span>
            </button>
            <button
              onClick={() => setView("STORIES")}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded transition-colors ${
                view === "STORIES"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Story Threads</span>
            </button>
            <button
              onClick={() => setView("EVENTS")}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded transition-colors ${
                view === "EVENTS"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Financial Events</span>
            </button>
            <button
              onClick={() => setView("SENTIMENT")}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded transition-colors ${
                view === "SENTIMENT"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Sentiment & Reactions</span>
            </button>
            <button
              onClick={() => setView("TIMELINE")}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded transition-colors ${
                view === "TIMELINE"
                  ? "bg-cyan-500 text-white font-semibold shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>Timelines</span>
            </button>
          </div>

          {/* Sidebar Toggle (visible in Feed and Timeline modes) */}
          {(view === "FEED" || view === "TIMELINE") && (
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
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {error ? (
        <NewsEmptyState isError={true} errorMessage={error} onRetry={refresh} />
      ) : view === "SENTIMENT" ? (
        <NewsSentimentWorkspace />
      ) : view === "STORIES" ? (
        /* Story Threads View */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
          <div className="lg:col-span-7 xl:col-span-7 flex flex-col min-w-0">
            <NewsStoryTable
              stories={storyHook.stories}
              selectedStory={storyHook.selectedStory}
              onSelectStory={(s) => storyHook.selectStory(s.story_id)}
              isLoading={storyHook.isLoading}
              onNavigateEntity={handleNavigateEntity}
            />
          </div>
          <div className="lg:col-span-5 xl:col-span-5 sticky top-4">
            <NewsStoryInspector
              story={storyHook.selectedStory}
              articles={storyHook.storyArticles}
              events={storyHook.storyEvents}
              isLoading={storyHook.isDetailLoading}
              onNavigateEntity={handleNavigateEntity}
              onSelectEvent={(ev) => {
                eventHook.selectEvent(ev.event_id);
                setView("EVENTS");
              }}
            />
          </div>
        </div>
      ) : view === "EVENTS" ? (
        /* Financial Events View */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
          <div className="lg:col-span-7 xl:col-span-7 flex flex-col min-w-0">
            <NewsFinancialEventTable
              events={eventHook.events}
              selectedEvent={eventHook.selectedEvent}
              onSelectEvent={(e) => eventHook.selectEvent(e.event_id)}
              isLoading={eventHook.isLoading}
              onNavigateEntity={handleNavigateEntity}
            />
          </div>
          <div className="lg:col-span-5 xl:col-span-5 sticky top-4">
            <NewsEventInspector
              event={eventHook.selectedEvent}
              evidence={eventHook.eventEvidence}
              isLoading={eventHook.isDetailLoading}
              onNavigateEntity={handleNavigateEntity}
              onNavigateStory={(storyId) => {
                storyHook.selectStory(storyId);
                setView("STORIES");
              }}
            />
          </div>
        </div>
      ) : (
        /* Headlines & Timeline Views */
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
