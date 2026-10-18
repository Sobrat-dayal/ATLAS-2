"use client";

/**
 * Saved Layouts Control & Dropdown Menu for ATLAS Charts Workspace (Stage 74).
 *
 * Implements:
 * - Clear distinction between Chart Arrangement and Named Saved Workspace
 * - Interactive Saved Layouts dropdown with fast search & switching
 * - One-click Quick Save with dirty-state indicator
 * - Safe unsaved-changes navigation warnings
 * - Modals integration: Save, Save As, Conflict Resolution, Import, Manager
 */

import React, { useState, useRef, useEffect } from "react";
import {
  Bookmark,
  ChevronDown,
  Copy,
  Download,
  FolderKanban,
  Plus,
  Save,
  Search,
  Star,
  Upload,
  Check,
  AlertTriangle,
} from "lucide-react";
import {
  useSavedLayouts,
  useLayoutDirtyState,
} from "@/hooks/charts";
import { SaveLayoutDialog } from "./SaveLayoutDialog";
import { LayoutConflictDialog } from "./LayoutConflictDialog";
import { LayoutImportDialog } from "./LayoutImportDialog";
import { SavedLayoutsManagerDialog } from "./SavedLayoutsManagerDialog";
import { LayoutRestoreStatus } from "./LayoutRestoreStatus";

export function SavedLayoutsMenu() {
  const {
    layouts,
    currentLayout,
    savedSnapshot,
    isLoading,
    isSaving,
    error,
    conflictState,
    restorationReport,
    loadLayout,
    saveCurrentLayout,
    saveAsLayout,
    renameLayout,
    setDefaultLayout,
    duplicateLayout,
    deleteLayout,
    exportLayout,
    importLayout,
    clearConflictState,
  } = useSavedLayouts();

  const { isDirty } = useLayoutDirtyState(savedSnapshot);

  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [isSaveAsMode, setIsSaveAsMode] = useState(false);
  const [showManagerDialog, setShowManagerDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [pendingSwitchLayoutId, setPendingSwitchLayoutId] = useState<string | null>(null);
  const [showUnsavedWarning, setShowUnsavedWarning] = useState(false);
  const [saveSuccessNotice, setSaveSuccessNotice] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Handle Quick Save button
  const handleQuickSave = async () => {
    if (!currentLayout) {
      setIsSaveAsMode(true);
      setShowSaveDialog(true);
      return;
    }

    const success = await saveCurrentLayout();
    if (success) {
      setSaveSuccessNotice(true);
      setTimeout(() => setSaveSuccessNotice(false), 2000);
    }
  };

  // Handle layout selection from menu
  const handleSelectLayout = (layoutId: string) => {
    if (currentLayout?.id === layoutId) {
      setIsOpen(false);
      return;
    }

    if (isDirty) {
      setPendingSwitchLayoutId(layoutId);
      setShowUnsavedWarning(true);
      setIsOpen(false);
      return;
    }

    loadLayout(layoutId);
    setIsOpen(false);
  };

  const confirmSwitchDiscard = () => {
    if (pendingSwitchLayoutId) {
      loadLayout(pendingSwitchLayoutId);
      setPendingSwitchLayoutId(null);
    }
    setShowUnsavedWarning(false);
  };

  const confirmSwitchSaveFirst = async () => {
    if (currentLayout) {
      await saveCurrentLayout();
    }
    if (pendingSwitchLayoutId) {
      loadLayout(pendingSwitchLayoutId);
      setPendingSwitchLayoutId(null);
    }
    setShowUnsavedWarning(false);
  };

  const filteredLayouts = layouts.filter((l) =>
    l.name.toLowerCase().includes(searchTerm.toLowerCase().trim())
  );

  const currentDisplayName = currentLayout?.name || "Workspace";

  return (
    <div className="relative flex items-center gap-1.5" ref={menuRef}>
      {/* 1. Main Saved Layout Dropdown Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
          isOpen
            ? "bg-zinc-800 border-cyan-500 text-zinc-100"
            : "bg-zinc-900 border-zinc-800 text-zinc-200 hover:border-zinc-700 hover:text-white"
        }`}
        title="Saved Chart Layouts"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <Bookmark className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
        <span className="max-w-[140px] truncate">{currentDisplayName}</span>
        {isDirty && (
          <span
            className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0"
            title="Unsaved changes"
          />
        )}
        <ChevronDown className={`w-3 h-3 text-zinc-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {/* 2. Quick Save Button */}
      <button
        onClick={handleQuickSave}
        disabled={isSaving || (currentLayout !== null && !isDirty)}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-semibold transition-colors border ${
          isDirty
            ? "bg-cyan-600 hover:bg-cyan-500 text-black border-cyan-500 shadow-sm"
            : saveSuccessNotice
            ? "bg-emerald-600 text-black border-emerald-500"
            : "bg-zinc-900 border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed"
        }`}
        title={isDirty ? "Save changes to layout" : saveSuccessNotice ? "Saved!" : "Workspace is up to date"}
      >
        {saveSuccessNotice ? (
          <>
            <Check className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Saved</span>
          </>
        ) : (
          <>
            <Save className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{isSaving ? "Saving..." : "Save"}</span>
          </>
        )}
      </button>

      {/* 3. Dropdown Menu Card */}
      {isOpen && (
        <div className="absolute left-0 top-full mt-1.5 w-72 bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl z-50 overflow-hidden font-sans text-xs animate-in fade-in-50 zoom-in-95 duration-100">
          {/* Search box */}
          <div className="p-2 border-b border-zinc-800/80 bg-zinc-900/40">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search layouts..."
                className="w-full pl-8 pr-3 py-1 bg-zinc-900 border border-zinc-800 rounded text-xs text-zinc-100 placeholder:text-zinc-500 font-mono focus:outline-none focus:border-cyan-500"
                autoFocus
              />
            </div>
          </div>

          {/* Layout List */}
          <div className="max-h-56 overflow-y-auto py-1 divide-y divide-zinc-900">
            {isLoading ? (
              <div className="py-6 text-center text-zinc-500 font-mono text-[11px]">
                Loading workspaces...
              </div>
            ) : filteredLayouts.length === 0 ? (
              <div className="py-6 text-center text-zinc-500 font-mono text-[11px]">
                {layouts.length === 0 ? "No saved layouts found" : "No matches"}
              </div>
            ) : (
              filteredLayouts.map((layout) => {
                const isSelected = layout.id === currentLayout?.id;
                return (
                  <button
                    key={layout.id}
                    onClick={() => handleSelectLayout(layout.id)}
                    className={`w-full text-left px-3 py-2 flex items-center justify-between gap-2 hover:bg-zinc-900/80 transition-colors ${
                      isSelected ? "bg-cyan-950/20 text-cyan-300" : "text-zinc-200"
                    }`}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs font-semibold truncate">
                          {layout.name}
                        </span>
                        {layout.is_default && (
                          <Star className="w-2.5 h-2.5 text-amber-400 fill-amber-400 shrink-0" />
                        )}
                      </div>
                      <div className="text-[10px] text-zinc-500 font-mono flex items-center gap-2 mt-0.5">
                        <span>{layout.layout_type}</span>
                        <span>•</span>
                        <span>{layout.chart_count} charts</span>
                        <span>•</span>
                        <span>{new Date(layout.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    {isSelected && (
                      <span className="text-[10px] font-mono text-cyan-400 border border-cyan-500/30 px-1 py-0.2 rounded bg-cyan-500/10 shrink-0">
                        OPEN
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* Action Menu Items */}
          <div className="p-1 border-t border-zinc-800 bg-zinc-900/30 space-y-0.5 font-mono text-xs">
            {currentLayout && (
              <button
                onClick={() => {
                  setIsOpen(false);
                  handleQuickSave();
                }}
                disabled={!isDirty || isSaving}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-zinc-300 hover:text-white hover:bg-zinc-800/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Save className="w-3.5 h-3.5 text-cyan-400" />
                <span>Save Current</span>
                {isDirty && <span className="ml-auto text-[10px] text-amber-400">• Unsaved</span>}
              </button>
            )}

            <button
              onClick={() => {
                setIsOpen(false);
                setIsSaveAsMode(true);
                setShowSaveDialog(true);
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-zinc-300 hover:text-white hover:bg-zinc-800/80 transition-colors"
            >
              <Copy className="w-3.5 h-3.5 text-emerald-400" />
              <span>Save As...</span>
            </button>

            <button
              onClick={() => {
                setIsOpen(false);
                setShowImportDialog(true);
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-zinc-300 hover:text-white hover:bg-zinc-800/80 transition-colors"
            >
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
              <span>Import Layout...</span>
            </button>

            <button
              onClick={() => {
                setIsOpen(false);
                exportLayout();
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-zinc-300 hover:text-white hover:bg-zinc-800/80 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-amber-400" />
              <span>Export Layout JSON</span>
            </button>

            <button
              onClick={() => {
                setIsOpen(false);
                setShowManagerDialog(true);
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded text-zinc-300 hover:text-white hover:bg-zinc-800/80 transition-colors border-t border-zinc-800/60 mt-1 pt-1"
            >
              <FolderKanban className="w-3.5 h-3.5 text-zinc-400" />
              <span>Manage Workspaces ({layouts.length})</span>
            </button>
          </div>
        </div>
      )}

      {/* 4. Modals */}
      <SaveLayoutDialog
        isOpen={showSaveDialog}
        isSaveAs={isSaveAsMode}
        initialName={currentLayout?.name || ""}
        initialDescription={currentLayout?.description || ""}
        initialIsDefault={currentLayout?.is_default || false}
        isSaving={isSaving}
        error={error}
        onSave={async (name, desc, isDef) => {
          const res = await saveAsLayout(name, desc, isDef);
          return res !== null;
        }}
        onClose={() => setShowSaveDialog(false)}
      />

      <SavedLayoutsManagerDialog
        isOpen={showManagerDialog}
        layouts={layouts}
        currentLayoutId={currentLayout?.id}
        onOpenLayout={(id) => handleSelectLayout(id)}
        onRenameLayout={renameLayout}
        onSetDefaultLayout={setDefaultLayout}
        onDuplicateLayout={duplicateLayout}
        onExportLayout={(id) => exportLayout(id)}
        onDeleteLayout={deleteLayout}
        onClose={() => setShowManagerDialog(false)}
      />

      <LayoutImportDialog
        isOpen={showImportDialog}
        onImport={importLayout}
        onClose={() => setShowImportDialog(false)}
      />

      <LayoutConflictDialog
        conflictState={conflictState}
        onSaveAsNew={() => {
          clearConflictState();
          setIsSaveAsMode(true);
          setShowSaveDialog(true);
        }}
        onReloadServer={(layoutId) => {
          clearConflictState();
          loadLayout(layoutId);
        }}
        onDismiss={clearConflictState}
      />

      <LayoutRestoreStatus
        report={restorationReport}
        onDismiss={() => {}}
      />

      {/* 5. Unsaved Navigation Confirmation Alert */}
      {showUnsavedWarning && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-100"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-sm bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl p-4 font-sans text-zinc-100 space-y-3">
            <div className="flex items-center gap-2 text-amber-400">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <h3 className="text-sm font-semibold font-mono">UNSAVED WORKSPACE EDITS</h3>
            </div>
            <p className="text-xs text-zinc-300 leading-relaxed">
              You have unsaved changes in your active chart workspace. Do you want to save them before opening another layout?
            </p>
            <div className="flex flex-col gap-1.5 pt-2">
              <button
                onClick={confirmSwitchSaveFirst}
                className="w-full py-1.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-black font-mono font-semibold text-xs transition-colors"
              >
                Save & Open
              </button>
              <button
                onClick={confirmSwitchDiscard}
                className="w-full py-1.5 px-3 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-mono text-xs transition-colors"
              >
                Discard & Open
              </button>
              <button
                onClick={() => {
                  setShowUnsavedWarning(false);
                  setPendingSwitchLayoutId(null);
                }}
                className="w-full py-1 rounded text-zinc-400 hover:text-zinc-200 font-mono text-xs transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
