"use client";

/**
 * Portable Layout JSON Import Dialog for ATLAS Charts (Stage 74).
 *
 * Implements:
 * - File picker and drag-and-drop JSON file upload
 * - Pre-import structural verification & preview summary
 * - Rejection of oversized payloads (> 512 KiB) and invalid schemas
 * - Name conflict resolution option
 */

import React, { useState } from "react";
import { Upload, X, Check, AlertCircle, FileText } from "lucide-react";
import { ImportPreviewSummary, parseAndValidateImportJson } from "@/lib/charts";

interface LayoutImportDialogProps {
  isOpen: boolean;
  onImport: (jsonContent: string, customName?: string) => Promise<any>;
  onClose: () => void;
}

export function LayoutImportDialog({
  isOpen,
  onImport,
  onClose,
}: LayoutImportDialogProps) {
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [preview, setPreview] = useState<ImportPreviewSummary | null>(null);
  const [customName, setCustomName] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 512 * 1024) {
      setError("File exceeds maximum allowed size of 512 KiB.");
      setFileContent(null);
      setPreview(null);
      return;
    }

    setFileName(file.name);
    setError(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setFileContent(text);
      try {
        const parsed = parseAndValidateImportJson(text);
        setPreview(parsed);
        setCustomName(parsed.layoutName);
      } catch (err: any) {
        setError(err.message || "Failed to validate imported layout file.");
        setPreview(null);
      }
    };
    reader.onerror = () => {
      setError("Failed to read selected file.");
    };
    reader.readAsText(file);
  };

  const handleImportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileContent || !preview) return;

    setIsImporting(true);
    setError(null);
    try {
      const res = await onImport(fileContent, customName.trim() || undefined);
      if (res) {
        onClose();
      }
    } catch (err: any) {
      setError(err.message || "Import failed.");
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="import-layout-dialog-title"
    >
      <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-sans text-zinc-100">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
          <div className="flex items-center gap-2">
            <Upload className="w-4 h-4 text-cyan-400" />
            <h2 id="import-layout-dialog-title" className="text-sm font-semibold tracking-tight font-mono text-zinc-100">
              IMPORT CHART LAYOUT
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close import dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleImportSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* File input */}
          <div>
            <label className="block text-xs font-mono text-zinc-400 mb-1.5 font-medium">
              Select ATLAS Layout JSON File
            </label>
            <input
              type="file"
              accept=".json,application/json"
              onChange={handleFileChange}
              className="w-full text-xs text-zinc-300 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-mono file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700 cursor-pointer"
            />
            <p className="text-[11px] text-zinc-500 font-mono mt-1">
              Supports files created via "Export Layout" (atlas_chart_layout v1).
            </p>
          </div>

          {/* Preview card */}
          {preview && (
            <div className="p-3 bg-zinc-900 border border-zinc-800 rounded space-y-2 text-xs font-mono">
              <div className="flex items-center gap-2 text-cyan-300 font-semibold border-b border-zinc-800 pb-1.5">
                <FileText className="w-3.5 h-3.5" />
                <span>Layout Preview</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-zinc-300 text-[11px]">
                <div>
                  <span className="text-zinc-500">Preset: </span>
                  <span className="text-zinc-200">{preview.layoutId}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Panels: </span>
                  <span className="text-zinc-200">{preview.panelCount}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Indicators: </span>
                  <span className="text-zinc-200">{preview.indicatorCount}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Drawings: </span>
                  <span className="text-zinc-200">{preview.drawingCount}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Sync Groups: </span>
                  <span className="text-zinc-200">{preview.syncGroupCount}</span>
                </div>
              </div>

              <div className="pt-2">
                <label className="block text-[11px] text-zinc-400 mb-1">
                  Import as Name:
                </label>
                <input
                  type="text"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  maxLength={100}
                  className="w-full px-2.5 py-1.5 bg-zinc-950 border border-zinc-700 rounded text-xs text-zinc-100 font-mono focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800/80">
            <button
              type="button"
              onClick={onClose}
              disabled={isImporting}
              className="px-3 py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!preview || isImporting}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded text-xs font-mono font-semibold bg-cyan-600 hover:bg-cyan-500 text-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{isImporting ? "Importing..." : "Import & Load"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
