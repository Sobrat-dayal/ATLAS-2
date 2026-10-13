"use client";

import React from "react";
import Link from "next/link";
import { Search, Terminal, Sparkles, LineChart, BookOpen, Map } from "lucide-react";
import { useCommandPalette, usePlatformShortcut } from "@/hooks/commands";

export function HomeQuickActions() {
  const { triggerSearchFocus, openCommandPalette } = useCommandPalette();
  const { shortcutLabel } = usePlatformShortcut();

  return (
    <div
      role="group"
      aria-label="Global quick actions"
      className="flex flex-wrap items-center gap-2"
    >
      {/* Search Entities Button */}
      <button
        type="button"
        onClick={() => triggerSearchFocus()}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label="Search entities across ATLAS"
      >
        <Search className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
        <span>Search Entities</span>
      </button>

      {/* Command Palette Button */}
      <button
        type="button"
        onClick={() => openCommandPalette()}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label={`Open Command Palette (${shortcutLabel})`}
      >
        <Terminal className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
        <span>Commands</span>
        <kbd className="hidden sm:inline-block px-1 py-0.2 text-[10px] font-mono text-atlas-text-muted bg-atlas-surface-3 rounded border border-atlas-border-subtle">
          {shortcutLabel}
        </kbd>
      </button>

      {/* AI Assistant Link */}
      <Link
        href="/ai"
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label="Open AI Assistant workspace"
      >
        <Sparkles className="h-3.5 w-3.5 text-atlas-accent" aria-hidden="true" />
        <span>AI Assistant</span>
      </Link>

      {/* Markets Link */}
      <Link
        href="/markets"
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label="Open Markets workspace"
      >
        <LineChart className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
        <span>Markets</span>
      </Link>

      {/* Research Link */}
      <Link
        href="/research"
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label="Open Research workspace"
      >
        <BookOpen className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
        <span>Research</span>
      </Link>

      {/* Maps Link */}
      <Link
        href="/maps"
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-sm border border-atlas-border-default bg-atlas-surface-2 text-atlas-text-primary hover:bg-atlas-surface-hover hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
        aria-label="Open Maps geospatial workspace"
      >
        <Map className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
        <span>Maps</span>
      </Link>
    </div>
  );
}
