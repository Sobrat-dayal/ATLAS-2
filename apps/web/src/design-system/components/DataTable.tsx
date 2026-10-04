import * as React from "react"
import { cn } from "../utils/cn"

export interface Column<T> {
  key: string;
  header: React.ReactNode;
  cell?: (row: T) => React.ReactNode;
  align?: "left" | "right" | "center";
  width?: string | number;
}

export interface DataTableProps<T> extends React.HTMLAttributes<HTMLDivElement> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
  compact?: boolean;
}

export function DataTable<T>({ 
  data, 
  columns, 
  keyExtractor, 
  onRowClick,
  compact = true,
  className,
  ...props 
}: DataTableProps<T>) {
  return (
    <div className={cn("w-full overflow-auto", className)} {...props}>
      <table className="w-full text-sm">
        <thead className="sticky top-0 z-10 bg-atlas-surface-1 border-b border-atlas-border-default">
          <tr className="text-atlas-text-muted">
            {columns.map((col, index) => (
              <th 
                key={col.key || index}
                style={{ width: col.width }}
                className={cn(
                  "font-medium py-2 px-3",
                  col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left",
                  compact ? "py-1.5 text-xs" : "py-2.5"
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-8 text-center text-atlas-text-muted">
                No results found.
              </td>
            </tr>
          ) : (
            data.map((row) => (
              <tr 
                key={keyExtractor(row)}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={cn(
                  "border-b border-atlas-border-subtle hover:bg-atlas-surface-hover transition-colors",
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col, index) => (
                  <td 
                    key={`${keyExtractor(row)}-${col.key || index}`}
                    className={cn(
                      "px-3 whitespace-nowrap",
                      col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left",
                      compact ? "py-1.5" : "py-2.5"
                    )}
                  >
                    {col.cell ? col.cell(row) : (row as any)[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
