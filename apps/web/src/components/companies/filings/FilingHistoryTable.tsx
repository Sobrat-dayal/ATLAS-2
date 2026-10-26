"use client";

import React, { useState } from "react";
import {
  FilingCategory,
  FilingSummaryDTO,
} from "@/lib/companies/filings";
import {
  FileText,
  Search,
  ExternalLink,
  GitCompare,
  ArrowUpDown,
  Filter,
  CheckCircle2,
  FileCode,
  Calendar,
} from "lucide-react";

interface FilingHistoryTableProps {
  filings: FilingSummaryDTO[];
  onSelectFiling: (filingId: string) => void;
  onCompareFilings?: (leftFilingId: string, rightFilingId: string) => void;
  initialCategory?: FilingCategory | "ALL";
}

export const FilingHistoryTable: React.FC<FilingHistoryTableProps> = ({
  filings,
  onSelectFiling,
  onCompareFilings,
  initialCategory = "ALL",
}) => {
  const [categoryFilter, setCategoryFilter] = useState<string>(initialCategory);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [amendmentsOnly, setAmendmentsOnly] = useState<boolean>(false);
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);

  const filteredFilings = filings.filter((f) => {
    if (categoryFilter !== "ALL" && f.category !== categoryFilter) return false;
    if (amendmentsOnly && !f.is_amendment) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchForm = f.form_type.toLowerCase().includes(q);
      const matchTitle = f.title.toLowerCase().includes(q);
      const matchAcc = f.accession_number.toLowerCase().includes(q);
      const matchPeriod = f.reporting_period.toLowerCase().includes(q);
      if (!matchForm && !matchTitle && !matchAcc && !matchPeriod) return false;
    }
    return true;
  });

  const handleToggleCompare = (filingId: string) => {
    setSelectedForCompare((prev) => {
      if (prev.includes(filingId)) {
        return prev.filter((id) => id !== filingId);
      }
      if (prev.length >= 2) {
        return [prev[1], filingId];
      }
      return [...prev, filingId];
    });
  };

  const getFormBadgeStyle = (form: string, isAmendment: boolean) => {
    if (form.startsWith("10-K")) {
      return isAmendment
        ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
        : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }
    if (form.startsWith("10-Q")) {
      return "bg-sky-500/10 text-sky-400 border-sky-500/30";
    }
    if (form.startsWith("8-K")) {
      return "bg-amber-500/10 text-amber-400 border-amber-500/30";
    }
    if (form.includes("14A")) {
      return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
    }
    if (form.startsWith("13F") || form.startsWith("SC 13")) {
      return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
    if (form === "4" || form === "3" || form === "5") {
      return "bg-slate-500/10 text-slate-300 border-slate-500/30";
    }
    return "bg-muted text-muted-foreground border-border";
  };

  return (
    <div className="space-y-3">
      {/* Table Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-2.5 rounded-lg border border-border/60 bg-card/40">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Box */}
          <div className="relative w-48 sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter by form, title, period..."
              className="w-full pl-8 pr-2.5 py-1 text-xs rounded bg-background/80 border border-border focus:outline-none focus:ring-1 focus:ring-primary text-foreground placeholder:text-muted-foreground"
            />
          </div>

          {/* Category Selector */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs px-2.5 py-1 rounded bg-background/80 border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="ALL">All Categories</option>
            <option value="ANNUAL_REPORTS">Annual Reports (10-K, 20-F)</option>
            <option value="QUARTERLY_REPORTS">Quarterly Reports (10-Q)</option>
            <option value="CURRENT_REPORTS">Current Events (8-K)</option>
            <option value="OWNERSHIP_INSIDER">Ownership & Insiders (13F, 4)</option>
            <option value="PROXY_STATEMENTS">Proxy Statements (DEF 14A)</option>
          </select>

          {/* Amendments Checkbox */}
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer select-none">
            <input
              type="checkbox"
              checked={amendmentsOnly}
              onChange={(e) => setAmendmentsOnly(e.target.checked)}
              className="rounded border-border text-primary focus:ring-0"
            />
            <span>Amendments Only (/A)</span>
          </label>
        </div>

        {/* Compare Action Button */}
        {selectedForCompare.length === 2 && onCompareFilings && (
          <button
            type="button"
            onClick={() => onCompareFilings(selectedForCompare[0], selectedForCompare[1])}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors shadow-sm"
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>Compare Selected (2)</span>
          </button>
        )}
      </div>

      {/* Table Container */}
      <div className="rounded-lg border border-border/60 bg-card/40 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 text-muted-foreground font-semibold uppercase tracking-wider text-[10px] border-b border-border/60">
              <tr>
                <th className="py-2.5 px-3 w-10 text-center">Diff</th>
                <th className="py-2.5 px-3 w-24">Form</th>
                <th className="py-2.5 px-3">Title / Description</th>
                <th className="py-2.5 px-3 w-28">Period</th>
                <th className="py-2.5 px-3 w-28">Filed Date</th>
                <th className="py-2.5 px-3 w-36">Accepted Timestamp</th>
                <th className="py-2.5 px-3 w-28">Accession No.</th>
                <th className="py-2.5 px-3 w-24 text-center">XBRL Facts</th>
                <th className="py-2.5 px-3 w-24 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 font-mono">
              {filteredFilings.length > 0 ? (
                filteredFilings.map((filing) => {
                  const isChecked = selectedForCompare.includes(filing.filing_id);
                  return (
                    <tr
                      key={filing.filing_id}
                      className="hover:bg-muted/30 transition-colors cursor-pointer group"
                      onClick={() => onSelectFiling(filing.filing_id)}
                    >
                      {/* Checkbox for comparison */}
                      <td
                        className="py-2 px-3 text-center"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleCompare(filing.filing_id);
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}}
                          title="Select to compare (choose 2)"
                          className="rounded border-border text-primary cursor-pointer"
                        />
                      </td>

                      {/* Form Badge */}
                      <td className="py-2 px-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold border ${getFormBadgeStyle(
                            filing.form_type,
                            filing.is_amendment
                          )}`}
                        >
                          {filing.form_type}
                        </span>
                        {filing.is_amendment && (
                          <span className="ml-1 px-1 py-0.2 rounded text-[9px] font-semibold bg-amber-500/20 text-amber-300">
                            REV
                          </span>
                        )}
                      </td>

                      {/* Title */}
                      <td className="py-2 px-3 font-sans max-w-xs sm:max-w-md truncate">
                        <span className="font-semibold text-foreground group-hover:text-primary transition-colors">
                          {filing.title}
                        </span>
                        <div className="text-[10px] text-muted-foreground font-mono truncate">
                          {filing.primary_document_name} &bull; {filing.document_count} attachments
                        </div>
                      </td>

                      {/* Reporting Period */}
                      <td className="py-2 px-3 whitespace-nowrap text-muted-foreground">
                        {filing.reporting_period}
                      </td>

                      {/* Filed Date */}
                      <td className="py-2 px-3 whitespace-nowrap text-foreground font-semibold">
                        {filing.filing_date}
                      </td>

                      {/* Accepted Timestamp */}
                      <td className="py-2 px-3 whitespace-nowrap text-muted-foreground text-[11px]">
                        {filing.acceptance_timestamp ? (
                          filing.acceptance_timestamp.slice(0, 19).replace("T", " ")
                        ) : (
                          <span className="text-muted-foreground/60">—</span>
                        )}
                      </td>

                      {/* Accession Number */}
                      <td className="py-2 px-3 whitespace-nowrap text-muted-foreground text-[11px]">
                        {filing.accession_number}
                      </td>

                      {/* Fact Count */}
                      <td className="py-2 px-3 whitespace-nowrap text-center">
                        {filing.fact_count > 0 ? (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 font-semibold">
                            {filing.fact_count} facts
                          </span>
                        ) : (
                          <span className="text-muted-foreground/50 text-[10px]">—</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td
                        className="py-2 px-3 text-right whitespace-nowrap"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          type="button"
                          onClick={() => onSelectFiling(filing.filing_id)}
                          className="px-2 py-0.5 rounded text-[11px] font-medium text-primary hover:bg-primary/10 transition-colors"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-muted-foreground font-sans text-xs">
                    No regulatory filings matched the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Footer info */}
        <div className="p-2 bg-muted/20 border-t border-border/40 text-[11px] text-muted-foreground flex items-center justify-between font-mono">
          <span>Showing {filteredFilings.length} of {filings.length} filings cataloged</span>
          <span>Regulator: SEC EDGAR (CIK: 0000320193)</span>
        </div>
      </div>
    </div>
  );
};
