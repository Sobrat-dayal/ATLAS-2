"use client";

import React from "react";
import {
  CalendarViewPreset,
  EconomicCalendarCoverageDTO,
  UserEventAlertDTO,
} from "@/lib/economics/calendar";
import {
  Calendar,
  Globe,
  Filter,
  Search,
  Bell,
  Clock,
  ShieldCheck,
  RefreshCw,
  Landmark,
  Layers,
  ChevronDown,
} from "lucide-react";

interface EconomicCalendarToolbarProps {
  viewPreset: CalendarViewPreset;
  onSelectPreset: (preset: CalendarViewPreset) => void;
  selectedTimezone: string;
  onSelectTimezone: (tz: string) => void;
  selectedGeography: string | null;
  onSelectGeography: (geo: string | null) => void;
  selectedCategory: string | null;
  onSelectCategory: (cat: string | null) => void;
  selectedImportance: string | null;
  onSelectImportance: (imp: string | null) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  categories: string[];
  supportedGeographies: string[];
  totalAlertsCount: number;
  onOpenAlerts: () => void;
  isCoverageOpen: boolean;
  onToggleCoverage: () => void;
  isLoading: boolean;
  onRefresh: () => void;
}

const TIMEZONES = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "America/New_York", label: "New York (ET)" },
  { value: "Europe/London", label: "London (GMT/BST)" },
  { value: "Europe/Frankfurt", label: "Frankfurt (CET/CEST)" },
  { value: "Asia/Kolkata", label: "India (IST)" },
  { value: "Asia/Tokyo", label: "Tokyo (JST)" },
  { value: "Asia/Shanghai", label: "Shanghai (CST)" },
];

const PRESETS: { id: CalendarViewPreset; label: string }[] = [
  { id: "all", label: "All Events" },
  { id: "today", label: "Today" },
  { id: "tomorrow", label: "Tomorrow" },
  { id: "this_week", label: "This Week" },
  { id: "next_week", label: "Next Week" },
  { id: "upcoming", label: "Upcoming" },
  { id: "released", label: "Released" },
  { id: "central_bank", label: "Central Banks" },
  { id: "my_alerts", label: "My Alerts" },
];

export function EconomicCalendarToolbar({
  viewPreset,
  onSelectPreset,
  selectedTimezone,
  onSelectTimezone,
  selectedGeography,
  onSelectGeography,
  selectedCategory,
  onSelectCategory,
  selectedImportance,
  onSelectImportance,
  searchQuery,
  onSearchChange,
  categories,
  supportedGeographies,
  totalAlertsCount,
  onOpenAlerts,
  isCoverageOpen,
  onToggleCoverage,
  isLoading,
  onRefresh,
}: EconomicCalendarToolbarProps) {
  return (
    <div className="flex flex-col gap-3 mb-4">
      {/* Row 1: View Presets & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-atlas-surface/60 border border-atlas-border-subtle rounded p-2">
        {/* Preset Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0 scrollbar-none text-xs">
          {PRESETS.map((p) => {
            const isActive = viewPreset === p.id;
            return (
              <button
                key={p.id}
                onClick={() => onSelectPreset(p.id)}
                className={`px-2.5 py-1.5 rounded whitespace-nowrap font-medium transition-colors flex items-center gap-1.5 ${
                  isActive
                    ? "bg-atlas-accent text-white shadow-xs"
                    : "text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface"
                }`}
              >
                {p.id === "central_bank" && <Landmark className="w-3 h-3" />}
                {p.id === "my_alerts" && <Bell className="w-3 h-3" />}
                <span>{p.label}</span>
                {p.id === "my_alerts" && totalAlertsCount > 0 && (
                  <span
                    className={`text-[10px] px-1 rounded-full font-mono ${
                      isActive ? "bg-white/20 text-white" : "bg-amber-500/20 text-amber-400"
                    }`}
                  >
                    {totalAlertsCount}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Right Toolbar Actions */}
        <div className="flex items-center gap-2 self-end md:self-auto shrink-0">
          {/* Timezone Selector */}
          <div className="flex items-center gap-1.5 bg-atlas-background border border-atlas-border-subtle rounded px-2 py-1 text-xs text-atlas-text-secondary">
            <Clock className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
            <select
              value={selectedTimezone}
              onChange={(e) => onSelectTimezone(e.target.value)}
              className="bg-transparent border-none text-xs text-atlas-text-primary focus:outline-none cursor-pointer pr-1"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz.value} value={tz.value} className="bg-atlas-surface text-atlas-text-primary">
                  {tz.label}
                </option>
              ))}
            </select>
          </div>

          {/* Manage Alerts Button */}
          <button
            onClick={onOpenAlerts}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-atlas-background hover:bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
            title="Configure Event Reminders & Notification Intents"
          >
            <Bell className="w-3.5 h-3.5 text-amber-400" />
            <span>Alerts</span>
            {totalAlertsCount > 0 && (
              <span className="text-[10px] bg-amber-500/20 text-amber-400 px-1 rounded font-mono">
                {totalAlertsCount}
              </span>
            )}
          </button>

          {/* Coverage & Verification Details */}
          <button
            onClick={onToggleCoverage}
            className={`flex items-center gap-1.5 px-2.5 py-1 border rounded text-xs transition-colors ${
              isCoverageOpen
                ? "bg-atlas-accent/15 border-atlas-accent text-atlas-accent"
                : "bg-atlas-background hover:bg-atlas-surface border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary"
            }`}
            title="View Official Source Registry & Schedule Precision Matrix"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Coverage</span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="p-1.5 bg-atlas-background hover:bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary transition-colors"
            title="Refresh verified releases"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Row 2: Secondary Dropdown Filters & Search */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search economic releases, FOMC, CPI, NFP..."
            className="w-full pl-8 pr-3 py-1.5 bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none focus:border-atlas-accent"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-atlas-text-muted hover:text-atlas-text-primary text-[10px]"
            >
              Clear
            </button>
          )}
        </div>

        {/* Country / Area Filter */}
        <div className="flex items-center gap-1 bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1">
          <Globe className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
          <select
            value={selectedGeography || ""}
            onChange={(e) => onSelectGeography(e.target.value || null)}
            className="bg-transparent border-none text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
          >
            <option value="" className="bg-atlas-surface text-atlas-text-primary">
              All Jurisdictions
            </option>
            {supportedGeographies.map((geo) => (
              <option key={geo} value={geo} className="bg-atlas-surface text-atlas-text-primary">
                {geo}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-1 bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1">
          <Layers className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
          <select
            value={selectedCategory || ""}
            onChange={(e) => onSelectCategory(e.target.value || null)}
            className="bg-transparent border-none text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
          >
            <option value="" className="bg-atlas-surface text-atlas-text-primary">
              All Categories
            </option>
            {categories.map((cat) => (
              <option key={cat} value={cat} className="bg-atlas-surface text-atlas-text-primary">
                {cat.replace("_", " ")}
              </option>
            ))}
          </select>
        </div>

        {/* Importance Filter */}
        <div className="flex items-center gap-1 bg-atlas-surface border border-atlas-border-subtle rounded px-2 py-1">
          <Filter className="w-3.5 h-3.5 text-atlas-text-muted shrink-0" />
          <select
            value={selectedImportance || ""}
            onChange={(e) => onSelectImportance(e.target.value || null)}
            className="bg-transparent border-none text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
          >
            <option value="" className="bg-atlas-surface text-atlas-text-primary">
              All Importance
            </option>
            <option value="HIGH" className="bg-atlas-surface text-rose-400">
              High Impact Only
            </option>
            <option value="MEDIUM" className="bg-atlas-surface text-amber-400">
              Medium Impact
            </option>
            <option value="LOW" className="bg-atlas-surface text-emerald-400">
              Low Impact
            </option>
          </select>
        </div>
      </div>
    </div>
  );
}
