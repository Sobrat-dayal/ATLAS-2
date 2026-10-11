"use client";

import React, {
  useEffect,
  useRef,
  useState,
  useId,
  useMemo,
  useCallback,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  Search,
  CornerDownLeft,
  X,
  Compass,
} from "lucide-react";
import { getActiveAtlasModule } from "@/config/atlas-modules";
import { useSelectedEntity } from "@/hooks/entity";
import { useSectionSettingsDrawer } from "@/hooks/settings/useSectionSettings";
import { useShellState } from "@/hooks/shell/useShellState";
import { useAuthorization } from "@/hooks/authorization";
import {
  useCommandPalette,
  usePlatformShortcut,
} from "@/hooks/commands/useCommandPalette";
import {
  filterCommands,
  executeCommand,
  CommandDefinition,
  CommandContext,
  CommandExecutionHelpers,
} from "@/lib/commands";

export function CommandPalette() {
  const { isOpen, closeCommandPalette, triggerSearchFocus } = useCommandPalette();
  const { shortcutLabel } = usePlatformShortcut();

  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);
  const listboxId = useId();

  const router = useRouter();
  const pathname = usePathname();
  const { selectedEntityId, clearSelectedEntity } = useSelectedEntity();
  const { openDrawer: openSectionSettings } = useSectionSettingsDrawer();
  const {
    sidebarCollapsed,
    setSidebarCollapsed,
    agentDockOpen,
    setAgentDockOpen,
  } = useShellState();

  // Route & permission authorization
  const { canViewModule, hasPermission } = useAuthorization();
  const activeModule = getActiveAtlasModule(pathname);

  // Build command context
  const context: CommandContext = useMemo(
    () => ({
      pathname,
      currentModuleId: activeModule?.id,
      selectedEntityId: selectedEntityId || null,
      canViewModule,
      hasPermission,
    }),
    [pathname, activeModule, selectedEntityId, canViewModule, hasPermission]
  );

  // Execution helpers
  const helpers: CommandExecutionHelpers = useMemo(
    () => ({
      navigate: (route: string) => {
        closeCommandPalette();
        router.push(route);
      },
      clearSelectedEntity: () => {
        clearSelectedEntity();
        closeCommandPalette();
      },
      focusGlobalSearch: () => {
        closeCommandPalette();
        triggerSearchFocus();
      },
      openSectionSettings: (moduleId) => {
        closeCommandPalette();
        openSectionSettings(moduleId);
      },
      closePalette: () => {
        closeCommandPalette();
      },
      toggleSidebar: () => {
        closeCommandPalette();
        setSidebarCollapsed(!sidebarCollapsed);
      },
      toggleAgentDock: () => {
        closeCommandPalette();
        setAgentDockOpen(!agentDockOpen);
      },
    }),
    [
      closeCommandPalette,
      router,
      clearSelectedEntity,
      triggerSearchFocus,
      openSectionSettings,
      sidebarCollapsed,
      setSidebarCollapsed,
      agentDockOpen,
      setAgentDockOpen,
    ]
  );

  // Filter commands deterministically
  const filteredCommands = useMemo(() => {
    return filterCommands(query, context);
  }, [query, context]);

  // Keep active index in bounds whenever filtered list changes
  useEffect(() => {
    setActiveIndex(0);
  }, [filteredCommands.length, query]);

  // Handle dialog opening & closing focus restoration
  useEffect(() => {
    if (isOpen) {
      previouslyFocusedElementRef.current =
        document.activeElement as HTMLElement | null;
      setQuery("");
      setActiveIndex(0);

      // Focus input on next frame
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    } else {
      // Restore previous focus when closing
      if (
        previouslyFocusedElementRef.current &&
        typeof previouslyFocusedElementRef.current.focus === "function"
      ) {
        previouslyFocusedElementRef.current.focus();
      }
    }
  }, [isOpen]);

  // Scroll active item into view
  useEffect(() => {
    if (!isOpen || filteredCommands.length === 0) return;
    const activeItemEl = listRef.current?.querySelector(
      `[data-command-index="${activeIndex}"]`
    );
    if (activeItemEl && typeof activeItemEl.scrollIntoView === "function") {
      activeItemEl.scrollIntoView({ block: "nearest" });
    }
  }, [activeIndex, isOpen, filteredCommands.length]);

  const handleSelect = useCallback(
    async (command: CommandDefinition) => {
      try {
        await executeCommand(command, context, helpers);
      } catch (err) {
        console.error("[CommandPalette] Command execution error:", err);
      }
    },
    [context, helpers]
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      closeCommandPalette();
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (filteredCommands.length === 0) return;
      setActiveIndex((prev) => (prev + 1) % filteredCommands.length);
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (filteredCommands.length === 0) return;
      setActiveIndex((prev) =>
        prev <= 0 ? filteredCommands.length - 1 : prev - 1
      );
      return;
    }

    if (e.key === "Home") {
      e.preventDefault();
      setActiveIndex(0);
      return;
    }

    if (e.key === "End") {
      e.preventDefault();
      if (filteredCommands.length > 0) {
        setActiveIndex(filteredCommands.length - 1);
      }
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      if (filteredCommands.length > 0 && activeIndex >= 0 && activeIndex < filteredCommands.length) {
        const selected = filteredCommands[activeIndex];
        handleSelect(selected);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Command Palette"
      className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4 bg-black/60 backdrop-blur-xs"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          closeCommandPalette();
        }
      }}
    >
      <div className="w-full max-w-2xl overflow-hidden rounded-md border border-atlas-border-default bg-atlas-surface-1 shadow-2xl transition-all duration-150 animate-in fade-in zoom-in-95">
        {/* Search Input Bar */}
        <div className="flex items-center border-b border-atlas-border-default px-3 py-2.5 bg-atlas-surface-2/60">
          <Search className="h-4 w-4 text-atlas-text-secondary shrink-0 mr-2.5" />
          <input
            ref={inputRef}
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-autocomplete="list"
            aria-controls={listboxId}
            aria-activedescendant={
              filteredCommands.length > 0
                ? `command-option-${filteredCommands[activeIndex]?.id}`
                : undefined
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or jump to module..."
            className="flex-1 bg-transparent text-sm text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="p-1 text-atlas-text-muted hover:text-atlas-text-primary transition-colors mr-1"
              aria-label="Clear query"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
          <span className="hidden sm:inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-mono font-medium text-atlas-text-muted bg-atlas-surface-2 border border-atlas-border-default">
            {shortcutLabel}
          </span>
        </div>

        {/* Command List Area */}
        <div
          ref={listRef}
          role="listbox"
          id={listboxId}
          aria-label="Commands"
          className="max-h-[50vh] overflow-y-auto p-1.5 scrollbar-thin scrollbar-thumb-atlas-border-default"
        >
          {filteredCommands.length === 0 ? (
            <div className="py-8 text-center text-xs text-atlas-text-muted">
              No matching commands
            </div>
          ) : (
            filteredCommands.map((command, idx) => {
              const isSelected = idx === activeIndex;
              const IconComponent = command.icon || Compass;

              return (
                <div
                  key={command.id}
                  id={`command-option-${command.id}`}
                  data-command-index={idx}
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleSelect(command)}
                  onMouseEnter={() => setActiveIndex(idx)}
                  className={`group flex items-center justify-between rounded px-2.5 py-2 text-xs cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-atlas-surface-selected text-atlas-text-primary"
                      : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-3">
                    <IconComponent
                      className={`h-4 w-4 shrink-0 transition-colors ${
                        isSelected
                          ? "text-atlas-accent"
                          : "text-atlas-text-secondary group-hover:text-atlas-text-primary"
                      }`}
                    />
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium truncate text-atlas-text-primary">
                          {command.label}
                        </span>
                        <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider font-mono">
                          {command.category}
                        </span>
                      </div>
                      {command.description && (
                        <span className="text-[11px] text-atlas-text-muted truncate mt-0.5">
                          {command.description}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {command.shortcut && (
                      <kbd className="hidden sm:inline-block font-mono text-[10px] text-atlas-text-muted bg-atlas-surface-2 px-1.5 py-0.5 rounded border border-atlas-border-default">
                        {command.shortcut}
                      </kbd>
                    )}
                    {isSelected && (
                      <CornerDownLeft className="h-3.5 w-3.5 text-atlas-accent shrink-0" />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Hints */}
        <div className="flex items-center justify-between border-t border-atlas-border-default px-3 py-1.5 bg-atlas-surface-2/40 text-[10px] text-atlas-text-muted">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="font-mono bg-atlas-surface-2 px-1 py-0.5 rounded border border-atlas-border-default mr-1">
                ↑
              </kbd>
              <kbd className="font-mono bg-atlas-surface-2 px-1 py-0.5 rounded border border-atlas-border-default mr-1">
                ↓
              </kbd>
              Navigate
            </span>
            <span>
              <kbd className="font-mono bg-atlas-surface-2 px-1 py-0.5 rounded border border-atlas-border-default mr-1">
                ↵
              </kbd>
              Run
            </span>
            <span>
              <kbd className="font-mono bg-atlas-surface-2 px-1 py-0.5 rounded border border-atlas-border-default mr-1">
                Esc
              </kbd>
              Close
            </span>
          </div>
          <span className="font-mono">ATLAS Command Registry</span>
        </div>
      </div>
    </div>
  );
}
