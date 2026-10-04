"use client";

import React, { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { SETTINGS_CATEGORIES, SettingsCategory } from "@/config/settings-registry";
import { Search, ChevronRight } from "lucide-react";

export function SettingsSidebar() {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return SETTINGS_CATEGORIES;
    const query = searchQuery.toLowerCase();
    
    return SETTINGS_CATEGORIES.filter((cat) => {
      const matchLabel = cat.label.toLowerCase().includes(query);
      const matchDesc = cat.description.toLowerCase().includes(query);
      const matchKeyword = cat.keywords.some((k) => k.toLowerCase().includes(query));
      return matchLabel || matchDesc || matchKeyword;
    });
  }, [searchQuery]);

  // Handle grouping categories by logic
  const groups = [
    {
      title: "Application",
      items: ["general", "appearance", "notifications", "keyboard", "accessibility"],
    },
    {
      title: "Account",
      items: ["account", "security", "privacy", "billing"],
    },
    {
      title: "AI & Automation",
      items: ["ai", "models", "agents", "mcp"],
    },
    {
      title: "Data & Trading",
      items: ["apiKeys", "dataProviders", "marketData", "trading", "brokers"],
    },
    {
      title: "System",
      items: ["storage", "integrations", "developer", "terminal", "advanced"],
    },
  ];

  return (
    <div className="flex flex-col w-[280px] h-full border-r border-atlas-border-default bg-atlas-surface-1 shrink-0">
      <div className="p-4 border-b border-atlas-border-default">
        <h2 className="text-lg font-semibold text-atlas-text-primary mb-4 tracking-tight">Settings</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-atlas-text-muted" />
          <input
            type="text"
            placeholder="Search settings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-atlas-bg-1 border border-atlas-border-default rounded-md py-1.5 pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-atlas-accent text-atlas-text-primary placeholder:text-atlas-text-muted"
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        {searchQuery.trim() ? (
          <div className="space-y-1">
            <h3 className="px-2 text-xs font-semibold text-atlas-text-muted uppercase tracking-wider mb-2 mt-2">
              Search Results
            </h3>
            {filteredCategories.length === 0 ? (
              <div className="px-2 py-4 text-sm text-atlas-text-muted text-center">
                No settings found.
              </div>
            ) : (
              filteredCategories.map((cat) => (
                <SidebarItem key={cat.id} category={cat} isActive={pathname === cat.route} />
              ))
            )}
          </div>
        ) : (
          groups.map((group) => {
            const groupCats = group.items
              .map((id) => SETTINGS_CATEGORIES.find((c) => c.id === id))
              .filter(Boolean) as SettingsCategory[];
            
            return (
              <div key={group.title} className="mb-6 last:mb-2">
                <h3 className="px-2 text-xs font-semibold text-atlas-text-muted uppercase tracking-wider mb-2">
                  {group.title}
                </h3>
                <div className="space-y-[1px]">
                  {groupCats.map((cat) => (
                    <SidebarItem key={cat.id} category={cat} isActive={pathname === cat.route} />
                  ))}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function SidebarItem({ category, isActive }: { category: SettingsCategory; isActive: boolean }) {
  return (
    <Link
      href={category.route}
      className={`flex items-center w-full px-2 py-1.5 rounded-sm text-sm transition-colors group ${
        isActive
          ? "bg-atlas-surface-selected text-atlas-accent font-medium"
          : "text-atlas-text-primary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
      }`}
    >
      <category.icon 
        className={`h-4 w-4 shrink-0 mr-3 ${isActive ? 'text-atlas-accent' : 'text-atlas-text-muted group-hover:text-atlas-text-primary'}`} 
      />
      <span className="truncate flex-1">{category.label}</span>
      {isActive && (
        <ChevronRight className="h-4 w-4 shrink-0 ml-2 opacity-50" />
      )}
    </Link>
  );
}
