"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useNews } from "@/hooks/news/useNews";
import { NewsHeader } from "./NewsHeader";
import { NewsCategoryTabs } from "./NewsCategoryTabs";
import { NewsFilterBar } from "./NewsFilterBar";
import { NewsFeedTable } from "./NewsFeedTable";
import { NewsArticlePreview } from "./NewsArticlePreview";
import { NewsCoverageModal } from "./NewsCoverageModal";
import { NewsEmptyState } from "./NewsEmptyState";

export function NewsWorkspace() {
  const router = useRouter();
  const [isCoverageOpen, setIsCoverageOpen] = useState(false);

  const {
    activeTab,
    setActiveTab,
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
    selectedSource,
    setSelectedSource,
    selectedPublisher,
    setSelectedPublisher,
    selectedGeography,
    setSelectedGeography,
    sources,
    publishers,
    coverage,
    status,
    refresh,
    loadNextPage,
    clearFilters,
  } = useNews();

  const hasFilters =
    Boolean(searchQuery) ||
    Boolean(selectedSource) ||
    Boolean(selectedPublisher) ||
    Boolean(selectedGeography);

  const handleNavigateEntity = (entityId: string, entityType: string, ticker?: string | null) => {
    if (entityType === "COMPANY") {
      router.push(`/companies?entity=${encodeURIComponent(entityId)}`);
    } else if (entityType === "INSTRUMENT" && ticker) {
      router.push(`/markets?symbol=${encodeURIComponent(ticker)}`);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50/50 dark:bg-zinc-950 p-4 sm:p-6 lg:p-8 space-y-4 max-w-[1920px] mx-auto">
      {/* News Top Header */}
      <NewsHeader
        status={status}
        totalArticles={coverage?.total_articles ?? totalCount}
        isRefreshing={isRefreshing}
        onRefresh={refresh}
        onOpenCoverage={() => setIsCoverageOpen(true)}
      />

      {/* Category Tabs */}
      <NewsCategoryTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Filter & Search Bar */}
      <NewsFilterBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedSource={selectedSource}
        onSourceChange={setSelectedSource}
        selectedPublisher={selectedPublisher}
        onPublisherChange={setSelectedPublisher}
        selectedGeography={selectedGeography}
        onGeographyChange={setSelectedGeography}
        sources={sources}
        publishers={publishers}
        onClearFilters={clearFilters}
      />

      {/* Main Workspace Body */}
      {error ? (
        <NewsEmptyState
          isError={true}
          errorMessage={error}
          onRetry={refresh}
        />
      ) : articles.length === 0 && !isLoading ? (
        <NewsEmptyState
          hasFilters={hasFilters}
          onClearFilters={clearFilters}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Column: High-Density Feed Table (lg: 7 or 8 cols) */}
          <div className="lg:col-span-7 xl:col-span-8 flex flex-col min-w-0">
            {isLoading && articles.length === 0 ? (
              <div className="flex items-center justify-center p-16 text-zinc-400 font-mono text-xs border border-zinc-200 dark:border-zinc-800 rounded bg-white dark:bg-zinc-900 shadow-sm">
                <span className="animate-pulse">Loading verified financial headlines...</span>
              </div>
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
            )}
          </div>

          {/* Right Column: Source-Qualified Article Preview (lg: 5 or 4 cols) */}
          <div className="lg:col-span-5 xl:col-span-4 sticky top-6">
            <NewsArticlePreview
              article={selectedArticle}
              onNavigateEntity={handleNavigateEntity}
            />
          </div>
        </div>
      )}

      {/* Coverage & Sources Modal */}
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
