"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { ATLAS_MODULES_LIST, getActiveAtlasModule } from "@/config/atlas-modules";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, HelpCircle } from "lucide-react";

export function Sidebar() {
  const { sidebarCollapsed, setSidebarCollapsed } = useShellState();
  const pathname = usePathname();
  
  // Resolve active module safely
  const activeModule = getActiveAtlasModule(pathname);
  const activeId = activeModule?.id;

  return (
    <div
      className={`flex h-full flex-col border-r border-atlas-border-default bg-atlas-surface-1 transition-all duration-200 ${
        sidebarCollapsed ? "w-[56px]" : "w-[160px]"
      }`}
    >
      {/* Collapse Toggle Area */}
      <div className="flex h-10 items-center justify-end px-2 border-b border-atlas-border-default">
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="p-1 text-atlas-text-muted hover:text-atlas-text-primary focus:outline-none focus:ring-1 focus:ring-atlas-accent rounded-sm"
          title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          aria-label={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {sidebarCollapsed ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-2 custom-scrollbar" aria-label="Main Navigation">
        {ATLAS_MODULES_LIST.map((module) => {
          const isActive = activeId === module.id;
          return (
            <Link
              key={module.id}
              href={module.route}
              title={sidebarCollapsed ? `${module.label}\n${module.description}` : undefined}
              aria-current={isActive ? "page" : undefined}
              className={`flex items-center px-3 py-1.5 mx-1 mb-0.5 rounded-sm text-sm transition-colors focus:outline-none focus:ring-1 focus:ring-atlas-accent ${
                isActive
                  ? "bg-atlas-surface-selected text-atlas-accent"
                  : "text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
              }`}
            >
              <module.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
              {!sidebarCollapsed && (
                <span className="ml-3 truncate">{module.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Settings / Utilities bottom area */}
      <div className="border-t border-atlas-border-default p-2" aria-label="Utility Navigation">
        <Link
          href="/settings"
          title={sidebarCollapsed ? "Settings" : undefined}
          className="flex items-center px-1.5 py-1.5 rounded-sm text-sm text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary focus:outline-none focus:ring-1 focus:ring-atlas-accent"
        >
          <Settings className="h-4 w-4 shrink-0" aria-hidden="true" />
          {!sidebarCollapsed && <span className="ml-3">Settings</span>}
        </Link>
        <Link
          href="/help"
          title={sidebarCollapsed ? "Help" : undefined}
          className="flex items-center px-1.5 py-1.5 rounded-sm text-sm text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary focus:outline-none focus:ring-1 focus:ring-atlas-accent"
        >
          <HelpCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
          {!sidebarCollapsed && <span className="ml-3">Help</span>}
        </Link>
      </div>
    </div>
  );
}
