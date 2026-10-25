import React, { useState } from "react";
import { formatEnrichmentDisplay } from "@/lib/watchlists/enrichment/formatting";
import { WatchlistRowCellValue } from "@/lib/watchlists/columns/types";
import { EnrichmentDetailsPopover } from "./EnrichmentDetailsPopover";

interface EnrichmentCellProps {
  columnId: string;
  label: string;
  cell?: WatchlistRowCellValue | null;
  cellStyle?: React.CSSProperties;
  pinnedBorder?: string;
}

export function EnrichmentCell({
  columnId,
  label,
  cell,
  cellStyle,
  pinnedBorder = "",
}: EnrichmentCellProps) {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const [popoverPos, setPopoverPos] = useState<{ x: number; y: number } | undefined>();

  const display = formatEnrichmentDisplay(columnId, cell);

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const rect = e.currentTarget.getBoundingClientRect();
    setPopoverPos({ x: rect.left, y: rect.bottom });
    setIsPopoverOpen((prev) => !prev);
  };

  const isNumeric =
    columnId.startsWith("fundamentals.") ||
    columnId.startsWith("valuation.") ||
    columnId.startsWith("technical.") ||
    columnId.startsWith("earnings.");

  return (
    <>
      <td
        style={cellStyle}
        onClick={handleClick}
        className={`px-3 py-2 cursor-pointer transition-colors hover:bg-zinc-800/40 font-mono ${
          isNumeric ? "text-right" : "text-left"
        } ${pinnedBorder}`}
        title={`Click to inspect ${label} provenance & metadata`}
      >
        <div className="flex flex-col">
          <span
            className={`text-xs tabular-nums ${
              display.isDimmed ? "text-zinc-500 font-normal" : display.colorClass || "text-zinc-200"
            }`}
          >
            {display.text}
          </span>
          {display.subtext && (
            <span className="text-[10px] text-zinc-400 font-sans tracking-tight">
              {display.subtext}
            </span>
          )}
        </div>
      </td>

      {cell && isPopoverOpen && (
        <div className="relative">
          <div
            className="fixed inset-0 z-40"
            onClick={(e) => {
              e.stopPropagation();
              setIsPopoverOpen(false);
            }}
          />
          <EnrichmentDetailsPopover
            label={label}
            columnId={columnId}
            cell={cell}
            isOpen={isPopoverOpen}
            onClose={() => setIsPopoverOpen(false)}
            position={popoverPos}
          />
        </div>
      )}
    </>
  );
}
