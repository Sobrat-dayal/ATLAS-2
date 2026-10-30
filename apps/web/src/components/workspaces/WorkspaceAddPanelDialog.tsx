"use client";

import React, { useState } from "react";
import { Plus, Search, X } from "lucide-react";
import { Button } from "@/design-system";
import { PanelTypeId } from "@/lib/workspaces/types";

interface WorkspaceAddPanelDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onAddPanel: (
    panelTypeId: PanelTypeId,
    titleOverride?: string,
    configuration?: Record<string, unknown>,
    dockPosition?: "right" | "bottom" | "tab"
  ) => Promise<void>;
}

interface PanelOption {
  typeId: PanelTypeId;
  title: string;
  category: string;
  description: string;
  sourceModule: string;
}

const REGISTERED_PANEL_OPTIONS: PanelOption[] = [
  { typeId: "MARKET_OVERVIEW", title: "Market Overview", category: "Markets", description: "Global equity indices, top gainers, and benchmark movers.", sourceModule: "markets" },
  { typeId: "INSTRUMENT_CHART", title: "Candlestick Chart", category: "Charts", description: "TradingView Lightweight Chart with technical indicators & volume.", sourceModule: "charts" },
  { typeId: "WATCHLIST", title: "Streaming Watchlist", category: "Markets", description: "Multi-column securities watchlist with real-time price changes.", sourceModule: "watchlists" },
  { typeId: "COMPANY_OVERVIEW", title: "Company Financials", category: "Fundamentals", description: "Balance sheet, income statement, cash flow, and ratios.", sourceModule: "companies" },
  { typeId: "ECONOMIC_SERIES", title: "Macro Indicators", category: "Macro", description: "Central bank rates, inflation, GDP, and yield curve series.", sourceModule: "economics" },
  { typeId: "NEWS_FEED", title: "Headlines Feed", category: "News", description: "Institutional breaking financial wire filtered by ticker or macro topic.", sourceModule: "news" },
  { typeId: "PORTFOLIO_SUMMARY", title: "Portfolio Holdings", category: "Portfolios", description: "Security positions, asset allocation, and cash weights.", sourceModule: "portfolios" },
  { typeId: "RISK_OVERVIEW", title: "Risk & Volatility", category: "Risk", description: "Portfolio volatility, beta, Value at Risk, and drawdowns.", sourceModule: "risk" },
  { typeId: "SCREENER", title: "Stock Screener", category: "Research", description: "Multi-factor equity screener with custom universe filtering.", sourceModule: "screeners" },
  { typeId: "RESEARCH_DOCUMENT", title: "Research Report", category: "Research", description: "Institutional research analysis and thesis document reader.", sourceModule: "research" },
  { typeId: "DATA_TABLE", title: "Data Explorer", category: "Data", description: "Custom financial dataset explorer table.", sourceModule: "data" },
  { typeId: "MAP_VIEW", title: "2D World Map", category: "Maps", description: "PostGIS & MapLibre institutional financial geography and monetary centers.", sourceModule: "maps" },
];

export function WorkspaceAddPanelDialog({
  isOpen,
  onClose,
  onAddPanel,
}: WorkspaceAddPanelDialogProps) {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedPanelType, setSelectedPanelType] = useState<PanelTypeId>("INSTRUMENT_CHART");
  const [dockPosition, setDockPosition] = useState<"right" | "bottom" | "tab">("right");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const categories = ["ALL", "Markets", "Charts", "Fundamentals", "Macro", "News", "Portfolios", "Risk", "Research", "Data", "Maps"];

  const filtered = REGISTERED_PANEL_OPTIONS.filter((p) => {
    const matchesSearch =
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "ALL" || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAdd = async () => {
    const option = REGISTERED_PANEL_OPTIONS.find((p) => p.typeId === selectedPanelType);
    setIsSubmitting(true);
    try {
      await onAddPanel(selectedPanelType, option?.title, {}, dockPosition);
      onClose();
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-xl bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">Add Panel to Workspace</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search available financial panels..."
              className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded-sm pl-8 pr-3 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-border-focus focus:outline-none"
            />
          </div>

          {/* Category Chips */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 custom-scrollbar">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-sm text-[10px] font-semibold transition-colors shrink-0 ${
                  selectedCategory === cat
                    ? "bg-blue-600 text-white"
                    : "bg-atlas-surface-2 text-atlas-text-muted hover:text-atlas-text-primary border border-atlas-border-subtle"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Panels List */}
          <div className="grid grid-cols-1 gap-2 max-h-56 overflow-auto custom-scrollbar p-0.5">
            {filtered.map((item) => {
              const isSelected = selectedPanelType === item.typeId;
              return (
                <div
                  key={item.typeId}
                  onClick={() => setSelectedPanelType(item.typeId)}
                  className={`p-2.5 rounded-sm border cursor-pointer transition-colors flex flex-col gap-1 ${
                    isSelected
                      ? "border-blue-500 bg-blue-500/10 text-atlas-text-primary"
                      : "border-atlas-border-default bg-atlas-surface-0 hover:bg-atlas-surface-hover text-atlas-text-primary"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs">{item.title}</span>
                    <span className="text-[10px] text-atlas-text-muted font-mono uppercase bg-atlas-surface-2 px-1.5 py-0.5 rounded">
                      {item.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-atlas-text-muted font-sans leading-tight">
                    {item.description}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Dock Position Selection */}
          <div className="pt-2 border-t border-atlas-border-default">
            <span className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1.5">
              Placement Position
            </span>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: "right", label: "Split Right" },
                { id: "bottom", label: "Split Bottom" },
                { id: "tab", label: "Tab Stack" },
              ].map((pos) => (
                <button
                  key={pos.id}
                  type="button"
                  onClick={() => setDockPosition(pos.id as any)}
                  className={`py-1.5 px-2 rounded-sm border text-center text-xs font-semibold ${
                    dockPosition === pos.id
                      ? "border-blue-500 bg-blue-500/15 text-blue-400"
                      : "border-atlas-border-default bg-atlas-surface-0 text-atlas-text-muted hover:text-atlas-text-primary"
                  }`}
                >
                  {pos.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-4 py-2.5 border-t border-atlas-border-default bg-atlas-surface-2">
          <Button variant="ghost" size="xs" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button variant="primary" size="xs" onClick={handleAdd} disabled={isSubmitting}>
            {isSubmitting ? "Adding..." : "Add to Workspace"}
          </Button>
        </div>
      </div>
    </div>
  );
}

