"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface ScreenerPaginationProps {
  page: number;
  pageSize: number;
  totalPages: number;
  totalMatchingCount: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newSize: number) => void;
}

export function ScreenerPagination({
  page,
  pageSize,
  totalPages,
  totalMatchingCount,
  onPageChange,
  onPageSizeChange,
}: ScreenerPaginationProps) {
  const startItem = totalMatchingCount === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, totalMatchingCount);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/60 bg-muted/20 px-6 py-2.5 text-xs text-muted-foreground">
      {/* Record Counter */}
      <div className="flex items-center gap-1.5 font-mono">
        <span>Showing</span>
        <span className="font-semibold text-foreground">
          {startItem}–{endItem}
        </span>
        <span>of</span>
        <span className="font-semibold text-foreground">{totalMatchingCount}</span>
        <span>securities</span>
      </div>

      {/* Page Controls */}
      <div className="flex items-center gap-4">
        {/* Page Size Dropdown */}
        <div className="flex items-center gap-1.5">
          <span>Rows per page:</span>
          <select
            aria-label="Rows per page"
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="h-7 rounded border border-border bg-background px-2 text-xs font-mono font-medium text-foreground focus:border-primary focus:outline-none"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        {/* Page Navigation */}
        <div className="flex items-center gap-1 font-mono">
          <button
            type="button"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="flex h-7 w-7 items-center justify-center rounded border border-border bg-background hover:bg-muted disabled:opacity-30 disabled:pointer-events-none"
            title="Previous page"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </button>

          <span className="px-2">
            Page <span className="font-semibold text-foreground">{page}</span> of{" "}
            <span className="font-semibold text-foreground">{Math.max(1, totalPages)}</span>
          </span>

          <button
            type="button"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="flex h-7 w-7 items-center justify-center rounded border border-border bg-background hover:bg-muted disabled:opacity-30 disabled:pointer-events-none"
            title="Next page"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
