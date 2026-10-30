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
  Terminal,
  AlertCircle,
  HelpCircle,
  Clock,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import { getActiveAtlasModule, ATLAS_MODULES } from "@/config/atlas-modules";
import { useSelectedEntity } from "@/hooks/entity";
import { useActivityRecorder } from "@/hooks/home/useActivityRecorder";
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
  getCommandById,
  CommandDefinition,
  CommandContext,
  CommandExecutionHelpers,
  looksLikeAtlasStructuredCommand,
  parseAtlasCommand,
  AtlasCommandParseResult,
  AmbiguityCandidate,
  interpretAtlasCommand,
  NaturalLanguageCommandInterpretation,
} from "@/lib/commands";

export function CommandPalette() {
  const { isOpen, closeCommandPalette, triggerSearchFocus } = useCommandPalette();
  const { shortcutLabel } = usePlatformShortcut();

  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  // Structured command parsing state
  const isStructuredQuery = useMemo(() => looksLikeAtlasStructuredCommand(query), [query]);
  const [parseResult, setParseResult] = useState<AtlasCommandParseResult | null>(null);
  const [parseLoading, setParseLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Natural-Language Command Interpretation state (Stage 48)
  const [interpretationResult, setInterpretationResult] = useState<NaturalLanguageCommandInterpretation | null>(null);
  const [isInterpreting, setIsInterpreting] = useState(false);
  const interpretAbortRef = useRef<AbortController | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);
  const listboxId = useId();

  const router = useRouter();
  const pathname = usePathname();
  const { selectedEntityId, clearSelectedEntity, selectEntity } = useSelectedEntity();
  const { openDrawer: openSectionSettings } = useSectionSettingsDrawer();
  const {
    sidebarCollapsed,
    setSidebarCollapsed,
    agentDockOpen,
    setAgentDockOpen,
    toggleBottomPanel,
  } = useShellState();

  // Route & permission authorization
  const { canViewModule, hasPermission } = useAuthorization();
  const activeModule = getActiveAtlasModule(pathname);
  const { recordModuleOpened, recordEntitySelected } = useActivityRecorder();

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
        const modKey = route.replace(/^\//, "");
        if (modKey in ATLAS_MODULES) {
          recordModuleOpened(modKey);
        }
        router.push(route);
      },
      selectEntity: (entityId: string) => {
        selectEntity(entityId);
        recordEntitySelected(entityId);
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
      toggleTerminal: () => {
        closeCommandPalette();
        toggleBottomPanel("terminal");
      },
    }),
    [
      closeCommandPalette,
      router,
      selectEntity,
      clearSelectedEntity,
      triggerSearchFocus,
      openSectionSettings,
      sidebarCollapsed,
      setSidebarCollapsed,
      agentDockOpen,
      setAgentDockOpen,
      toggleBottomPanel,
      recordModuleOpened,
      recordEntitySelected,
    ]
  );

  // Filter local commands deterministically when not structured mode
  const filteredCommands = useMemo(() => {
    if (isStructuredQuery) return [];
    return filterCommands(query, context);
  }, [query, context, isStructuredQuery]);

  // Keep active index in bounds
  useEffect(() => {
    setActiveIndex(0);
  }, [filteredCommands.length, parseResult, query]);

  // Debounced Structured Command Parsing with cancellation & stale response protection
  useEffect(() => {
    if (!isStructuredQuery || !query.trim()) {
      setParseResult(null);
      setParseLoading(false);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      return;
    }

    setParseLoading(true);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(async () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const currentInput = query.trim();

      try {
        const result = await parseAtlasCommand({
          text: currentInput,
          signal: controller.signal,
        });

        // Stale response protection: verify query has not changed
        if (inputRef.current?.value.trim() === currentInput) {
          setParseResult(result);
          setParseLoading(false);
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        // Backend outage/network error fallback: safe invalid state without crash
        if (inputRef.current?.value.trim() === currentInput) {
          setParseResult({
            command_language_version: 1,
            status: "INVALID",
            normalized_command: currentInput,
            error_code: "COMMAND_PARSER_UNAVAILABLE",
            error_message: "Command parser service is temporarily unavailable.",
          });
          setParseLoading(false);
        }
      }
    }, 150);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, isStructuredQuery]);

  // Handle dialog opening & closing focus restoration
  useEffect(() => {
    if (isOpen) {
      previouslyFocusedElementRef.current =
        document.activeElement as HTMLElement | null;
      setQuery("");
      setActiveIndex(0);
      setParseResult(null);
      setParseLoading(false);
      setInterpretationResult(null);
      setIsInterpreting(false);

      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    } else {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (interpretAbortRef.current) {
        interpretAbortRef.current.abort();
      }
      setInterpretationResult(null);
      setIsInterpreting(false);
      if (
        previouslyFocusedElementRef.current &&
        typeof previouslyFocusedElementRef.current.focus === "function"
      ) {
        previouslyFocusedElementRef.current.focus();
      }
    }
  }, [isOpen]);

  const handleSelectLocal = useCallback(
    async (command: CommandDefinition) => {
      try {
        await executeCommand(command, context, helpers);
      } catch (err) {
        console.error("[CommandPalette] Command execution error:", err);
      }
    },
    [context, helpers]
  );

  const handleExecuteParsed = useCallback(
    async (result: AtlasCommandParseResult, explicitArgs?: Record<string, unknown>) => {
      if (!result.command_id) return;

      const commandDef = getCommandById(result.command_id);
      if (!commandDef) {
        console.error(`[CommandPalette] Unknown command ID returned by parser: "${result.command_id}"`);
        return;
      }

      const argsToPass = explicitArgs || (result.arguments as Record<string, unknown> | undefined);

      try {
        await executeCommand(commandDef, context, helpers, argsToPass);
      } catch (err) {
        console.error("[CommandPalette] Parsed command execution error:", err);
      }
    },
    [context, helpers]
  );

  const handleCandidateSelect = useCallback(
    (candidate: AmbiguityCandidate) => {
      if (!parseResult || !parseResult.command_id) return;
      handleExecuteParsed(parseResult, { entityId: candidate.entity_id });
    },
    [parseResult, handleExecuteParsed]
  );

  // Stage 48: Explicit trigger for Natural-Language Command Interpretation
  const handleTriggerInterpret = useCallback(async () => {
    const text = query.trim();
    if (!text) return;

    if (interpretAbortRef.current) {
      interpretAbortRef.current.abort();
    }
    const controller = new AbortController();
    interpretAbortRef.current = controller;

    setIsInterpreting(true);
    setInterpretationResult(null);

    try {
      const result = await interpretAtlasCommand({
        text,
        signal: controller.signal,
      });

      // Stale response protection
      if (inputRef.current?.value.trim() === text) {
        setInterpretationResult(result);
        setIsInterpreting(false);
        setActiveIndex(0);
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        return;
      }
      if (inputRef.current?.value.trim() === text) {
        setInterpretationResult({
          interpreter_version: 1,
          prompt_version: 1,
          model_output_schema_version: 1,
          status: "INTERPRETER_UNAVAILABLE",
          input_fingerprint: "",
          intent: "AMBIGUOUS",
          clarification_question:
            "Natural-language command interpretation is temporarily unavailable. Structured commands still work.",
        });
        setIsInterpreting(false);
        setActiveIndex(0);
      }
    }
  }, [query]);

  // Stage 48: Candidate disambiguation selection for natural language
  const handleInterpretationCandidateSelect = useCallback(
    (candidate: AmbiguityCandidate) => {
      if (!interpretationResult?.structured_parse_result) return;
      handleExecuteParsed(interpretationResult.structured_parse_result, {
        entityId: candidate.entity_id,
      });
    },
    [interpretationResult, handleExecuteParsed]
  );

  const totalLocalItems = useMemo(() => {
    if (isStructuredQuery) return 0;
    const hasInterpretOption = query.trim().length > 0;
    return filteredCommands.length + (hasInterpretOption ? 1 : 0);
  }, [isStructuredQuery, query, filteredCommands.length]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      closeCommandPalette();
      return;
    }

    // 1. Structured query navigation
    if (isStructuredQuery) {
      const candidates = parseResult?.ambiguity_candidates || [];

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (candidates.length > 0) {
          setActiveIndex((prev) => (prev + 1) % candidates.length);
        }
        return;
      }

      if (e.key === "ArrowUp") {
        e.preventDefault();
        if (candidates.length > 0) {
          setActiveIndex((prev) => (prev <= 0 ? candidates.length - 1 : prev - 1));
        }
        return;
      }

      if (e.key === "Enter") {
        e.preventDefault();
        if (parseResult?.status === "READY") {
          handleExecuteParsed(parseResult);
        } else if (parseResult?.status === "AMBIGUOUS" && candidates.length > 0) {
          const selected = candidates[activeIndex] || candidates[0];
          handleCandidateSelect(selected);
        }
      }
      return;
    }

    // 2. Active Interpretation Result navigation
    if (interpretationResult) {
      const candidates = interpretationResult.structured_parse_result?.ambiguity_candidates || [];

      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (candidates.length > 0) {
          setActiveIndex((prev) => (prev + 1) % candidates.length);
        }
        return;
      }

      if (e.key === "ArrowUp") {
        e.preventDefault();
        if (candidates.length > 0) {
          setActiveIndex((prev) => (prev <= 0 ? candidates.length - 1 : prev - 1));
        }
        return;
      }

      if (e.key === "Enter") {
        e.preventDefault();
        if (interpretationResult.status === "READY" && interpretationResult.structured_parse_result) {
          handleExecuteParsed(interpretationResult.structured_parse_result);
        } else if (interpretationResult.status === "AMBIGUOUS" && candidates.length > 0) {
          const selected = candidates[activeIndex] || candidates[0];
          handleInterpretationCandidateSelect(selected);
        }
      }
      return;
    }

    // 3. Local commands keyboard navigation (including explicit interpret option)
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (totalLocalItems === 0) return;
      setActiveIndex((prev) => (prev + 1) % totalLocalItems);
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (totalLocalItems === 0) return;
      setActiveIndex((prev) => (prev <= 0 ? totalLocalItems - 1 : prev - 1));
      return;
    }

    if (e.key === "Home") {
      e.preventDefault();
      setActiveIndex(0);
      return;
    }

    if (e.key === "End") {
      e.preventDefault();
      if (totalLocalItems > 0) {
        setActiveIndex(totalLocalItems - 1);
      }
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      if (activeIndex < filteredCommands.length && activeIndex >= 0) {
        const selected = filteredCommands[activeIndex];
        handleSelectLocal(selected);
      } else if (activeIndex === filteredCommands.length && query.trim().length > 0) {
        handleTriggerInterpret();
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
          {isStructuredQuery ? (
            <Terminal className="h-4 w-4 text-atlas-accent shrink-0 mr-2.5" />
          ) : (
            <Search className="h-4 w-4 text-atlas-text-secondary shrink-0 mr-2.5" />
          )}
          <input
            ref={inputRef}
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-autocomplete="list"
            aria-controls={listboxId}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (interpretationResult) {
                setInterpretationResult(null);
              }
              if (isInterpreting) {
                if (interpretAbortRef.current) {
                  interpretAbortRef.current.abort();
                }
                setIsInterpreting(false);
              }
            }}
            onKeyDown={handleKeyDown}
            placeholder={
              isStructuredQuery
                ? "ATLAS Command (e.g. /charts NVDA or NVDA CHART)..."
                : "Type a command, jump to module, or ask natural instructions..."
            }
            className="flex-1 bg-transparent text-sm text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
          />
          {query && (
            <button
              onClick={() => {
                setQuery("");
                setInterpretationResult(null);
                setIsInterpreting(false);
              }}
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

        {/* Content Area */}
        <div
          ref={listRef}
          role="listbox"
          id={listboxId}
          aria-label="Commands"
          className="max-h-[50vh] overflow-y-auto p-1.5 scrollbar-thin scrollbar-thumb-atlas-border-default"
        >
          {isStructuredQuery ? (
            /* Structured Command Parsing Render Mode */
            <div className="p-2 space-y-2">
              {parseLoading && !parseResult && (
                <div className="flex items-center gap-2 py-4 px-2 text-xs text-atlas-text-muted">
                  <div className="h-3 w-3 animate-spin rounded-full border-2 border-atlas-accent border-t-transparent" />
                  <span>Parsing command language v1...</span>
                </div>
              )}

              {parseResult && (
                <>
                  {/* READY Status: Actionable Command Preview */}
                  {parseResult.status === "READY" && (
                    <div
                      role="option"
                      aria-selected={true}
                      onClick={() => handleExecuteParsed(parseResult)}
                      className="group flex items-center justify-between rounded p-3 bg-atlas-surface-selected border border-atlas-accent/40 cursor-pointer transition-colors hover:bg-atlas-surface-hover"
                    >
                      <div className="flex items-center gap-3 min-w-0 flex-1 pr-3">
                        <CheckCircle2 className="h-5 w-5 text-atlas-accent shrink-0" />
                        <div className="flex flex-col min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-sm text-atlas-text-primary truncate">
                              {parseResult.execution_summary || "Execute Command"}
                            </span>
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-atlas-accent/20 text-atlas-accent font-mono uppercase font-semibold">
                              READY
                            </span>
                          </div>
                          {parseResult.resolved_target && (
                            <div className="text-[11px] text-atlas-text-secondary mt-1 flex items-center gap-2">
                              <span className="font-medium text-atlas-text-primary">
                                {parseResult.resolved_target.display_name}
                              </span>
                              <span className="text-atlas-text-muted font-mono">
                                ({parseResult.resolved_target.entity_type}: {parseResult.resolved_target.matched_value})
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <kbd className="hidden sm:inline-block font-mono text-[10px] text-atlas-accent bg-atlas-surface-2 px-2 py-1 rounded border border-atlas-accent/30 font-medium">
                          Press ↵ to run
                        </kbd>
                        <CornerDownLeft className="h-4 w-4 text-atlas-accent shrink-0" />
                      </div>
                    </div>
                  )}

                  {/* AMBIGUOUS Status: Bounded Candidate Disambiguation List */}
                  {parseResult.status === "AMBIGUOUS" && (
                    <div className="space-y-1">
                      <div className="px-2 py-1 text-[11px] font-medium text-amber-400 flex items-center gap-1.5">
                        <HelpCircle className="h-3.5 w-3.5" />
                        <span>
                          Ambiguous target &quot;{parseResult.raw_target}&quot; — select entity to proceed:
                        </span>
                      </div>
                      <div className="divide-y divide-atlas-border-default/50 rounded border border-atlas-border-default bg-atlas-surface-2/40">
                        {(parseResult.ambiguity_candidates || []).map((cand, idx) => {
                          const isCandSelected = idx === activeIndex;
                          return (
                            <div
                              key={cand.entity_id}
                              role="option"
                              aria-selected={isCandSelected}
                              onClick={() => handleCandidateSelect(cand)}
                              onMouseEnter={() => setActiveIndex(idx)}
                              className={`flex items-center justify-between p-2.5 text-xs cursor-pointer transition-colors ${
                                isCandSelected
                                  ? "bg-atlas-surface-selected text-atlas-text-primary"
                                  : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                              }`}
                            >
                              <div className="flex flex-col min-w-0 pr-3">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium truncate text-atlas-text-primary">
                                    {cand.display_name}
                                  </span>
                                  <span className="text-[10px] text-atlas-text-muted font-mono uppercase">
                                    {cand.entity_type}
                                  </span>
                                </div>
                                <span className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                                  Matched: {cand.matched_value} ({cand.match_kind})
                                </span>
                              </div>
                              {isCandSelected && (
                                <CornerDownLeft className="h-3.5 w-3.5 text-atlas-accent shrink-0" />
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* UNAVAILABLE Status: Recognized but not implemented yet */}
                  {parseResult.status === "UNAVAILABLE" && (
                    <div className="flex items-start gap-2.5 p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
                      <Clock className="h-4 w-4 shrink-0 mt-0.5 text-amber-400" />
                      <div className="flex flex-col gap-1">
                        <span className="font-semibold text-amber-200">
                          Command Recognized (Unavailable in v1)
                        </span>
                        <span className="text-amber-300/90 text-[11px]">
                          {parseResult.error_message || "This command is not available in the current version of ATLAS."}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* INVALID Status: Syntax, type mismatch, or target not found */}
                  {parseResult.status === "INVALID" && (
                    <div className="flex items-start gap-2.5 p-3 rounded bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
                      <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
                      <div className="flex flex-col gap-1">
                        <span className="font-semibold text-red-200">Invalid Command</span>
                        <span className="text-red-300/90 text-[11px]">
                          {parseResult.error_message || "Command syntax or target is invalid."}
                        </span>
                        {parseResult.error_code && (
                          <span className="text-[10px] font-mono text-red-400/80">
                            Code: {parseResult.error_code}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* INCOMPLETE Status */}
                  {parseResult.status === "INCOMPLETE" && (
                    <div className="flex items-start gap-2.5 p-3 rounded bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs">
                      <HelpCircle className="h-4 w-4 shrink-0 mt-0.5 text-blue-400" />
                      <div className="flex flex-col gap-1">
                        <span className="font-semibold text-blue-200">Incomplete Command</span>
                        <span className="text-blue-300/90 text-[11px]">
                          {parseResult.error_message || "Additional target or parameters required."}
                        </span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : isInterpreting ? (
            /* Stage 48: Compact Interpreting State */
            <div className="flex items-center gap-2.5 py-8 px-4 justify-center text-xs text-atlas-text-secondary" aria-live="polite">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-atlas-accent border-t-transparent shrink-0" />
              <span>Interpreting natural-language command...</span>
            </div>
          ) : interpretationResult ? (
            /* Stage 48: Natural-Language Interpretation Result */
            <div className="p-2 space-y-2">
              {/* READY Status: Preview and explicit execute */}
              {interpretationResult.status === "READY" && interpretationResult.structured_parse_result && (
                <div
                  role="option"
                  aria-selected={true}
                  onClick={() => handleExecuteParsed(interpretationResult.structured_parse_result!)}
                  className="group flex items-center justify-between rounded p-3 bg-atlas-surface-selected border border-atlas-accent/40 cursor-pointer transition-colors hover:bg-atlas-surface-hover"
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1 pr-3">
                    <Sparkles className="h-5 w-5 text-atlas-accent shrink-0" />
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-atlas-text-primary truncate">
                          {interpretationResult.structured_parse_result.execution_summary ||
                            `Run: ${interpretationResult.canonical_command}`}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-atlas-accent/20 text-atlas-accent font-mono uppercase font-semibold">
                          READY
                        </span>
                      </div>
                      {interpretationResult.structured_parse_result.resolved_target && (
                        <div className="text-[11px] text-atlas-text-secondary mt-1 flex items-center gap-2">
                          <span className="font-medium text-atlas-text-primary">
                            {interpretationResult.structured_parse_result.resolved_target.display_name}
                          </span>
                          <span className="text-atlas-text-muted font-mono">
                            ({interpretationResult.structured_parse_result.resolved_target.entity_type}:{" "}
                            {interpretationResult.structured_parse_result.resolved_target.matched_value})
                          </span>
                        </div>
                      )}
                      <div className="text-[10px] font-mono text-atlas-text-muted mt-1">
                        Compiled: {interpretationResult.canonical_command}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <kbd className="hidden sm:inline-block font-mono text-[10px] text-atlas-accent bg-atlas-surface-2 px-2 py-1 rounded border border-atlas-accent/30 font-medium">
                      Press ↵ to run
                    </kbd>
                    <CornerDownLeft className="h-4 w-4 text-atlas-accent shrink-0" />
                  </div>
                </div>
              )}

              {/* AMBIGUOUS Status */}
              {interpretationResult.status === "AMBIGUOUS" && (
                <>
                  {interpretationResult.structured_parse_result?.ambiguity_candidates &&
                  interpretationResult.structured_parse_result.ambiguity_candidates.length > 0 ? (
                    <div className="space-y-1">
                      <div className="px-2 py-1 text-[11px] font-medium text-amber-400 flex items-center gap-1.5">
                        <HelpCircle className="h-3.5 w-3.5" />
                        <span>
                          {interpretationResult.clarification_question ||
                            `Ambiguous target "${interpretationResult.target_text}" — select entity to proceed:`}
                        </span>
                      </div>
                      <div className="divide-y divide-atlas-border-default/50 rounded border border-atlas-border-default bg-atlas-surface-2/40">
                        {interpretationResult.structured_parse_result.ambiguity_candidates.map(
                          (cand, idx) => {
                            const isCandSelected = idx === activeIndex;
                            return (
                              <div
                                key={cand.entity_id}
                                role="option"
                                aria-selected={isCandSelected}
                                onClick={() => handleInterpretationCandidateSelect(cand)}
                                onMouseEnter={() => setActiveIndex(idx)}
                                className={`flex items-center justify-between p-2.5 text-xs cursor-pointer transition-colors ${
                                  isCandSelected
                                    ? "bg-atlas-surface-selected text-atlas-text-primary"
                                    : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                                }`}
                              >
                                <div className="flex flex-col min-w-0 pr-3">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium truncate text-atlas-text-primary">
                                      {cand.display_name}
                                    </span>
                                    <span className="text-[10px] text-atlas-text-muted font-mono uppercase">
                                      {cand.entity_type}
                                    </span>
                                  </div>
                                  <span className="text-[10px] text-atlas-text-muted font-mono mt-0.5">
                                    Matched: {cand.matched_value} ({cand.match_kind})
                                  </span>
                                </div>
                                {isCandSelected && (
                                  <CornerDownLeft className="h-3.5 w-3.5 text-atlas-accent shrink-0" />
                                )}
                              </div>
                            );
                          }
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2.5 p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
                      <HelpCircle className="h-4 w-4 shrink-0 mt-0.5 text-amber-400" />
                      <div className="flex flex-col gap-1">
                        <span className="font-semibold text-amber-200">Ambiguous Command</span>
                        <span className="text-amber-300/90 text-[11px]">
                          {interpretationResult.clarification_question ||
                            "Which ATLAS module or entity should be opened?"}
                        </span>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* NOT_COMMAND Status */}
              {interpretationResult.status === "NOT_COMMAND" && (
                <div className="flex items-start gap-2.5 p-3 rounded bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs">
                  <HelpCircle className="h-4 w-4 shrink-0 mt-0.5 text-blue-400" />
                  <div className="flex flex-col gap-1">
                    <span className="font-semibold text-blue-200">Informational Question</span>
                    <span className="text-blue-300/90 text-[11px]">
                      This looks like a question rather than an ATLAS command. Natural-language command interpretation converts instructions into navigation and application commands.
                    </span>
                  </div>
                </div>
              )}

              {/* UNSUPPORTED Status */}
              {interpretationResult.status === "UNSUPPORTED" && (
                <div className="flex items-start gap-2.5 p-3 rounded bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-purple-400" />
                  <div className="flex flex-col gap-1">
                    <span className="font-semibold text-purple-200">Unsupported Action</span>
                    <span className="text-purple-300/90 text-[11px]">
                      {interpretationResult.clarification_question ||
                        "This action is outside supported ATLAS command capabilities."}
                    </span>
                    {interpretationResult.unsupported_reason && (
                      <span className="text-[10px] font-mono text-purple-400/80">
                        Reason: {interpretationResult.unsupported_reason}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* INVALID_MODEL_OUTPUT Status */}
              {interpretationResult.status === "INVALID_MODEL_OUTPUT" && (
                <div className="flex items-start gap-2.5 p-3 rounded bg-red-500/10 border border-red-500/30 text-red-300 text-xs">
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
                  <div className="flex flex-col gap-1">
                    <span className="font-semibold text-red-200">Interpretation Error</span>
                    <span className="text-red-300/90 text-[11px]">
                      ATLAS could not safely interpret this command.
                    </span>
                  </div>
                </div>
              )}

              {/* INTERPRETER_UNAVAILABLE Status */}
              {interpretationResult.status === "INTERPRETER_UNAVAILABLE" && (
                <div className="flex items-start gap-2.5 p-3 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
                  <Clock className="h-4 w-4 shrink-0 mt-0.5 text-amber-400" />
                  <div className="flex flex-col gap-1">
                    <span className="font-semibold text-amber-200">Interpreter Unavailable</span>
                    <span className="text-amber-300/90 text-[11px]">
                      Natural-language command interpretation is temporarily unavailable. Structured commands still work.
                    </span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Standard Stage 46 Local Command Matching + Stage 48 Interpret Option */
            <>
              {filteredCommands.length === 0 && query.trim().length === 0 ? (
                <div className="py-8 text-center text-xs text-atlas-text-muted">
                  No matching commands
                </div>
              ) : (
                <>
                  {filteredCommands.map((command, idx) => {
                    const isSelected = idx === activeIndex;
                    const IconComponent = command.icon || Compass;

                    return (
                      <div
                        key={command.id}
                        id={`command-option-${command.id}`}
                        data-command-index={idx}
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => handleSelectLocal(command)}
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
                  })}

                  {/* Stage 48: Explicit Interpret as ATLAS command row */}
                  {query.trim().length > 0 && (
                    <div
                      role="option"
                      aria-selected={activeIndex === filteredCommands.length}
                      onClick={handleTriggerInterpret}
                      onMouseEnter={() => setActiveIndex(filteredCommands.length)}
                      className={`group flex items-center justify-between rounded px-2.5 py-2.5 text-xs cursor-pointer transition-colors border-t border-atlas-border-default/40 mt-1 ${
                        activeIndex === filteredCommands.length
                          ? "bg-atlas-surface-selected text-atlas-text-primary"
                          : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-3">
                        <Sparkles
                          className={`h-4 w-4 shrink-0 transition-colors ${
                            activeIndex === filteredCommands.length
                              ? "text-atlas-accent"
                              : "text-atlas-text-secondary group-hover:text-atlas-text-primary"
                          }`}
                        />
                        <div className="flex flex-col min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium truncate text-atlas-text-primary">
                              Interpret as ATLAS command
                            </span>
                            <span className="text-[10px] px-1.5 py-0.2 rounded bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-muted font-mono">
                              NL
                            </span>
                          </div>
                          <span className="text-[11px] text-atlas-text-muted truncate mt-0.5">
                            Interpret &quot;{query.trim()}&quot; via ATLAS command interpreter
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {activeIndex === filteredCommands.length && (
                          <CornerDownLeft className="h-3.5 w-3.5 text-atlas-accent shrink-0" />
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
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
          <span className="font-mono">
            {isStructuredQuery ? "ATLAS Command Language v1" : "ATLAS Command Registry"}
          </span>
        </div>
      </div>
    </div>
  );
}
