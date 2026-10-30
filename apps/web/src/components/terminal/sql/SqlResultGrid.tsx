/**
 * High-density Bloomberg-style interactive tabular result grid for SQL queries.
 */

import React, { useState } from "react";
import type { TabularResult } from "@/lib/terminal/executionTypes";
import { Download, FileSpreadsheet, ArrowUpDown, Copy, Check } from "lucide-react";

interface SqlResultGridProps {
  result: TabularResult;
  durationMs?: number | null;
  className?: string;
}

export const SqlResultGrid: React.FC<SqlResultGridProps> = ({
  result,
  durationMs,
  className = "",
}) => {
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);

  const { columns, rows, total_rows, truncated } = result;

  const handleSort = (colName: string) => {
    if (sortCol === colName) {
      setSortAsc(!sortAsc);
    } else {
      setSortCol(colName);
      setSortAsc(true);
    }
  };

  const sortedRows = React.useMemo(() => {
    if (!sortCol) return rows;
    return [...rows].sort((a, b) => {
      const valA = a[sortCol];
      const valB = b[sortCol];
      if (valA === valB) return 0;
      if (valA == null) return 1;
      if (valB == null) return -1;
      if (typeof valA === "number" && typeof valB === "number") {
        return sortAsc ? valA - valB : valB - valA;
      }
      return sortAsc
        ? String(valA).localeCompare(String(valB))
        : String(valB).localeCompare(String(valA));
    });
  }, [rows, sortCol, sortAsc]);

  const exportCsv = () => {
    if (columns.length === 0 || rows.length === 0) return;
    const header = columns.map((c) => `"${c.name}"`).join(",");
    const body = rows
      .map((r) =>
        columns.map((c) => `"${r[c.name] != null ? String(r[c.name]).replace(/"/g, '""') : ""}"`).join(",")
      )
      .join("\n");
    const blob = new Blob([`${header}\n${body}`], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `sql_result_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(rows, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!columns || columns.length === 0) {
    return (
      <div className="p-4 text-xs font-mono text-neutral-500 italic">
        Query completed with 0 columns returned.
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-neutral-950 border border-neutral-800 rounded overflow-hidden ${className}`}>
      {/* Grid Toolbar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-neutral-900 border-b border-neutral-800 text-xs font-mono">
        <div className="flex items-center gap-3 text-neutral-400">
          <span className="font-semibold text-neutral-200">
            {total_rows} row{total_rows === 1 ? "" : "s"}
          </span>
          {durationMs != null && (
            <span className="text-neutral-500 text-[11px]">
              ({durationMs.toFixed(1)}ms)
            </span>
          )}
          {truncated && (
            <span className="text-amber-400 text-[11px] font-semibold">
              [TRUNCATED TO {rows.length} ROWS]
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={copyJson}
            className="flex items-center gap-1 px-2 py-0.5 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-[11px] border border-neutral-700 transition"
            title="Copy as JSON"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? "Copied" : "JSON"}</span>
          </button>
          <button
            onClick={exportCsv}
            className="flex items-center gap-1 px-2 py-0.5 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-[11px] border border-neutral-700 transition"
            title="Export as CSV"
          >
            <Download className="w-3 h-3" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Grid Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse font-mono text-xs text-left">
          <thead className="bg-neutral-900/90 sticky top-0 border-b border-neutral-800 text-neutral-300 text-[11px]">
            <tr>
              <th className="px-2 py-1.5 text-neutral-600 w-10 text-right select-none border-r border-neutral-800/50">#</th>
              {columns.map((col) => (
                <th
                  key={col.name}
                  onClick={() => handleSort(col.name)}
                  className="px-3 py-1.5 font-semibold select-none cursor-pointer hover:bg-neutral-800/80 transition border-r border-neutral-800/50 last:border-r-0"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span>{col.name}</span>
                    <span className="text-neutral-500 text-[9px] uppercase">{col.data_type}</span>
                    <ArrowUpDown className="w-2.5 h-2.5 text-neutral-500 opacity-60" />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-900">
            {sortedRows.map((row, idx) => (
              <tr
                key={idx}
                className="hover:bg-neutral-900/60 transition group even:bg-neutral-950 odd:bg-neutral-950/40"
              >
                <td className="px-2 py-1 text-neutral-600 text-right select-none text-[10px] border-r border-neutral-900 font-mono">
                  {idx + 1}
                </td>
                {columns.map((col) => {
                  const val = row[col.name];
                  const isNumber = typeof val === "number";
                  return (
                    <td
                      key={col.name}
                      className={`px-3 py-1 whitespace-nowrap text-neutral-300 border-r border-neutral-900 last:border-r-0 ${
                        isNumber ? "text-right font-mono" : ""
                      }`}
                    >
                      {val === null || val === undefined ? (
                        <span className="text-neutral-600 italic">null</span>
                      ) : isNumber ? (
                        val.toLocaleString()
                      ) : (
                        String(val)
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

