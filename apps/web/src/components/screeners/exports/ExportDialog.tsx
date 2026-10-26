"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Check,
  CheckSquare,
  Clock,
  Download,
  FileSpreadsheet,
  FileText,
  Info,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Square,
  X,
} from "lucide-react";
import {
  ExportFormat,
  ExportJobStatus,
  ExportScope,
  FilterCriterion,
  ScreenerColumnDefinition,
  ScreenerExportJob,
  ScreenerExportRequest,
  ScreenerRankingSpec,
  ScreenerRunRequest,
  SortCriterion,
} from "@/lib/screeners/types";
import {
  cancelScreenerExport,
  createScreenerExport,
  fetchScreenerExports,
  getScreenerExportDownloadUrl,
  getScreenerExportStatus,
} from "@/lib/screeners/api";

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  selectedUniverseId: string;
  selectedExchanges: string[];
  selectedCountries: string[];
  selectedSectors: string[];
  activeFilters: FilterCriterion[];
  sortCriteria: SortCriterion[];
  rankingSpec: ScreenerRankingSpec | null;
  columnsRegistry: ScreenerColumnDefinition[];
  visibleColumnIds: string[];
  totalMatchingCount: number;
  currentPage: number;
  pageSize: number;
  currentSavedScreenId?: string | null;
}

export function ExportDialog({
  isOpen,
  onClose,
  selectedUniverseId,
  selectedExchanges,
  selectedCountries,
  selectedSectors,
  activeFilters,
  sortCriteria,
  rankingSpec,
  columnsRegistry,
  visibleColumnIds,
  totalMatchingCount,
  currentPage,
  pageSize,
  currentSavedScreenId,
}: ExportDialogProps) {
  const [activeTab, setActiveTab] = useState<"configure" | "history">("configure");
  const [format, setFormat] = useState<ExportFormat>("csv");
  const [scope, setScope] = useState<ExportScope>("all_matching_results");
  const [selectedCols, setSelectedCols] = useState<string[]>(
    visibleColumnIds.length > 0 ? visibleColumnIds : columnsRegistry.filter((c) => c.default_visible).map((c) => c.column_id)
  );
  const [includeMetadata, setIncludeMetadata] = useState<boolean>(true);

  // Job execution state
  const [currentJob, setCurrentJob] = useState<ScreenerExportJob | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // History state
  const [recentJobs, setRecentJobs] = useState<ScreenerExportJob[]>([]);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      setError(null);
      setCurrentJob(null);
      loadRecentJobs();
    }
  }, [isOpen]);

  // Polling for running export job
  useEffect(() => {
    if (!currentJob || currentJob.status === "completed" || currentJob.status === "failed" || currentJob.status === "cancelled") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await getScreenerExportStatus(currentJob.export_job_id);
        setCurrentJob(updated);
        if (updated.status === "completed" || updated.status === "failed") {
          loadRecentJobs();
        }
      } catch (err: unknown) {
        console.warn("Error polling export job status:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentJob]);

  if (!isOpen) return null;

  const loadRecentJobs = async () => {
    setHistoryLoading(true);
    try {
      const data = await fetchScreenerExports();
      setRecentJobs(data.items);
    } catch (err: unknown) {
      console.warn("Error loading export history:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleToggleColumn = (colId: string) => {
    setSelectedCols((prev) =>
      prev.includes(colId) ? prev.filter((id) => id !== colId) : [...prev, colId]
    );
  };

  const handleSelectAllCols = () => {
    setSelectedCols(columnsRegistry.map((c) => c.column_id));
  };

  const handleDeselectAllCols = () => {
    setSelectedCols(["symbol", "company_name"]);
  };

  const handleStartExport = async () => {
    setLoading(true);
    setError(null);

    const queryPayload: ScreenerRunRequest = {
      universe: {
        universe_id: selectedUniverseId,
        exchange_mics: selectedExchanges.length > 0 ? selectedExchanges : null,
        listing_country_codes: selectedCountries.length > 0 ? selectedCountries : null,
        sectors: selectedSectors.length > 0 ? selectedSectors : null,
      },
      filters: activeFilters,
      sort: sortCriteria,
      ranking: rankingSpec,
      columns: selectedCols,
      page: currentPage,
      page_size: pageSize,
    };

    const exportPayload: ScreenerExportRequest = {
      query: queryPayload,
      saved_screen_id: currentSavedScreenId ?? null,
      format,
      scope,
      selected_columns: selectedCols,
      include_metadata: includeMetadata,
    };

    try {
      const job = await createScreenerExport(exportPayload);
      setCurrentJob(job);
      loadRecentJobs();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to generate export.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await cancelScreenerExport(jobId);
      const updated = await getScreenerExportStatus(jobId);
      setCurrentJob(updated);
      loadRecentJobs();
    } catch (err: unknown) {
      console.warn("Failed to cancel export job:", err);
    }
  };

  const formatBytes = (bytes?: number | null) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl rounded-lg border border-border bg-card shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 px-6 py-4 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <Download className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                Institutional Financial Data Export
              </h2>
              <p className="text-xs text-muted-foreground">
                Deterministic Result Snapshots, Multi-Sheet Workbooks & Injection-Safe Datasets
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center border-b border-border/60 bg-background px-6 pt-2">
          <button
            type="button"
            onClick={() => setActiveTab("configure")}
            className={`px-3 py-2 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "configure"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            Export Configuration
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("history")}
            className={`flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === "history"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <span>Recent Exports</span>
            {recentJobs.length > 0 && (
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-muted text-[10px] font-mono">
                {recentJobs.length}
              </span>
            )}
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {error && (
            <div className="flex items-start gap-2 rounded-md bg-destructive/10 border border-destructive/20 p-3 text-xs text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {activeTab === "configure" ? (
            <>
              {/* Active Job Status Banner if running or completed */}
              {currentJob && (
                <div className={`p-4 rounded-lg border text-xs space-y-2 ${
                  currentJob.status === "completed"
                    ? "border-emerald-500/30 bg-emerald-500/5 text-foreground"
                    : currentJob.status === "failed"
                    ? "border-destructive/30 bg-destructive/5 text-destructive"
                    : "border-primary/30 bg-primary/5 text-foreground"
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {currentJob.status === "completed" ? (
                        <Check className="h-4 w-4 text-emerald-500" />
                      ) : currentJob.status === "failed" ? (
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      ) : (
                        <Loader2 className="h-4 w-4 text-primary animate-spin" />
                      )}
                      <span className="font-semibold text-xs uppercase">
                        Export Job Status: {currentJob.status}
                      </span>
                    </div>

                    {currentJob.status === "completed" && (
                      <a
                        href={getScreenerExportDownloadUrl(currentJob.export_job_id)}
                        download
                        className="flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1 text-xs font-medium text-white hover:bg-emerald-700 shadow-sm transition-colors"
                      >
                        <Download className="h-3.5 w-3.5" />
                        <span>Download {currentJob.format.toUpperCase()}</span>
                      </a>
                    )}

                    {(currentJob.status === "queued" || currentJob.status === "running") && (
                      <button
                        type="button"
                        onClick={() => handleCancelJob(currentJob.export_job_id)}
                        className="rounded border border-border px-2 py-0.5 text-[11px] text-muted-foreground hover:bg-muted"
                      >
                        Cancel Job
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] text-muted-foreground pt-1">
                    <div>Format: <span className="font-semibold text-foreground">{currentJob.format}</span></div>
                    <div>Rows: <span className="font-semibold text-foreground">{currentJob.row_count}</span></div>
                    <div>Size: <span className="font-semibold text-foreground">{formatBytes(currentJob.file_size_bytes)}</span></div>
                  </div>
                </div>
              )}

              {/* Format Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">File Format</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setFormat("csv")}
                    className={`flex items-center gap-2.5 p-3 rounded-md border text-left transition-all ${
                      format === "csv"
                        ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                        : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                    }`}
                  >
                    <FileText className="h-4 w-4 shrink-0" />
                    <div>
                      <div className="text-xs font-semibold text-foreground">CSV (RFC 4180 / UTF-8)</div>
                      <div className="text-[11px] text-muted-foreground">
                        Machine-readable delimited text with formula injection neutralization
                      </div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setFormat("xlsx")}
                    className={`flex items-center gap-2.5 p-3 rounded-md border text-left transition-all ${
                      format === "xlsx"
                        ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                        : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                    }`}
                  >
                    <FileSpreadsheet className="h-4 w-4 shrink-0" />
                    <div>
                      <div className="text-xs font-semibold text-foreground">Excel Workbook (.xlsx)</div>
                      <div className="text-[11px] text-muted-foreground">
                        Multi-sheet workbook (Results, Methodology, Sources, Configuration)
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Scope Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Export Scope</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setScope("current_page")}
                    className={`p-3 rounded-md border text-left transition-all ${
                      scope === "current_page"
                        ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                        : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                    }`}
                  >
                    <div className="text-xs font-semibold text-foreground">Current View Page</div>
                    <div className="text-[11px] text-muted-foreground">
                      Export currently viewed {Math.min(pageSize, totalMatchingCount)} rows (Page {currentPage})
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setScope("all_matching_results")}
                    className={`p-3 rounded-md border text-left transition-all ${
                      scope === "all_matching_results"
                        ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                        : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                    }`}
                  >
                    <div className="text-xs font-semibold text-foreground">All Filtered Results</div>
                    <div className="text-[11px] text-muted-foreground">
                      Export full universe match of {totalMatchingCount} securities (up to 50,000 max)
                    </div>
                  </button>
                </div>
              </div>

              {/* Column Selection */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-foreground">
                  <span>Selected Columns ({selectedCols.length}/{columnsRegistry.length})</span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handleSelectAllCols}
                      className="text-[11px] text-primary hover:underline"
                    >
                      Select All
                    </button>
                    <span className="text-muted-foreground/40">·</span>
                    <button
                      type="button"
                      onClick={handleDeselectAllCols}
                      className="text-[11px] text-muted-foreground hover:underline"
                    >
                      Minimal
                    </button>
                  </div>
                </div>

                <div className="max-h-36 overflow-y-auto rounded-md border border-border/80 p-2.5 grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs bg-background">
                  {columnsRegistry.map((col) => {
                    const isChecked = selectedCols.includes(col.column_id);
                    return (
                      <label
                        key={col.column_id}
                        className="flex items-center gap-1.5 cursor-pointer text-muted-foreground hover:text-foreground select-none"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleToggleColumn(col.column_id)}
                          className="rounded border-border text-primary focus:ring-primary h-3.5 w-3.5"
                        />
                        <span className="truncate text-[11px]">{col.display_label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Security & Provenance Notices */}
              <div className="rounded-md border border-border/70 bg-muted/20 p-3 space-y-1.5 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 font-semibold text-foreground text-[11px]">
                  <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                  <span>Security & Auditable Provenance</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  Formula-injection defenses neutralize unsafe spreadsheet expressions (<code className="text-foreground">=, +, -, @</code>) while preserving valid negative financial numbers. Ticker symbols are guaranteed text type to prevent unintended spreadsheet truncation.
                </p>
              </div>
            </>
          ) : (
            /* History Tab */
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Recent Background & Synchronous Export Jobs</span>
                <button
                  type="button"
                  onClick={loadRecentJobs}
                  disabled={historyLoading}
                  className="flex items-center gap-1 text-[11px] hover:text-foreground"
                >
                  <RefreshCw className={`h-3 w-3 ${historyLoading ? "animate-spin" : ""}`} />
                  <span>Refresh</span>
                </button>
              </div>

              {recentJobs.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-center text-muted-foreground border border-dashed rounded-lg">
                  <Clock className="h-6 w-6 text-muted-foreground/40 mb-1" />
                  <p className="text-xs">No export jobs found for this session</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {recentJobs.map((job) => (
                    <div
                      key={job.export_job_id}
                      className="flex items-center justify-between p-3 rounded-md border border-border/70 bg-muted/20 text-xs"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-foreground uppercase">{job.format} Export</span>
                          <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono uppercase ${
                            job.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                              : job.status === "failed"
                              ? "bg-destructive/10 text-destructive border border-destructive/20"
                              : "bg-primary/10 text-primary border border-primary/20"
                          }`}>
                            {job.status}
                          </span>
                        </div>
                        <div className="text-[11px] font-mono text-muted-foreground">
                          {job.row_count} rows · {formatBytes(job.file_size_bytes)} · {job.scope}
                        </div>
                      </div>

                      <div>
                        {job.status === "completed" ? (
                          <a
                            href={getScreenerExportDownloadUrl(job.export_job_id)}
                            download
                            className="flex items-center gap-1 rounded bg-primary/10 hover:bg-primary/20 text-primary px-2.5 py-1 text-xs font-medium transition-colors"
                          >
                            <Download className="h-3 w-3" />
                            <span>Download</span>
                          </a>
                        ) : job.status === "running" || job.status === "queued" ? (
                          <button
                            type="button"
                            onClick={() => handleCancelJob(job.export_job_id)}
                            className="rounded border border-border px-2 py-0.5 text-[11px] text-muted-foreground hover:bg-muted"
                          >
                            Cancel
                          </button>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border/70 px-6 py-3 bg-muted/20">
          <span className="text-[11px] text-muted-foreground font-mono">
            Quota: 50,000 rows max · 24-hr download retention
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted transition-colors"
            >
              Close
            </button>
            {activeTab === "configure" && (
              <button
                type="button"
                onClick={handleStartExport}
                disabled={loading || selectedCols.length === 0}
                className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Preparing...</span>
                  </>
                ) : (
                  <>
                    <Download className="h-3.5 w-3.5" />
                    <span>Generate {format.toUpperCase()} Export</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
