import * as React from "react"
import { cn } from "../utils/cn"
import { Panel, PanelContent } from "../components/Panel"
import { formatPercent, formatCompactNumber } from "../utils/formatters"

export interface MetricCardProps {
  title: string;
  value: number | string;
  delta?: number;
  prefix?: string;
  suffix?: string;
  format?: "number" | "currency" | "percent" | "compact" | "raw";
  trend?: "up" | "down" | "flat"; // If not provided, computed from delta
  sparkline?: number[]; // Mock array of numbers for a sparkline
  className?: string;
}

export function MetricCard({
  title,
  value,
  delta,
  prefix = "",
  suffix = "",
  format = "raw",
  trend,
  sparkline,
  className
}: MetricCardProps) {
  
  // Format the main value
  let formattedValue = value.toString();
  if (typeof value === "number") {
    switch (format) {
      case "compact":
        formattedValue = formatCompactNumber(value);
        break;
      case "percent":
        formattedValue = formatPercent(value);
        break;
      case "currency":
        formattedValue = value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        break;
      case "number":
        formattedValue = value.toLocaleString("en-US");
        break;
    }
  }

  const computedTrend = trend || (delta !== undefined ? (delta > 0 ? "up" : delta < 0 ? "down" : "flat") : undefined);

  return (
    <Panel className={cn("flex flex-col", className)}>
      <PanelContent className="p-3 flex-1 flex flex-col justify-between">
        <h4 className="text-xs font-medium text-atlas-text-muted">{title}</h4>
        <div className="mt-2 flex items-baseline justify-between">
          <div className="text-xl font-semibold tabular-nums text-atlas-text-primary">
            {prefix}{formattedValue}{suffix}
          </div>
          
          {delta !== undefined && (
            <div className={cn(
              "text-xs font-medium tabular-nums ml-2",
              computedTrend === "up" ? "text-atlas-positive" : 
              computedTrend === "down" ? "text-atlas-negative" : "text-atlas-text-muted"
            )}>
              {computedTrend === "up" ? "+" : ""}{formatPercent(delta)}
            </div>
          )}
        </div>
        
        {/* Fake sparkline rendering just as a structural placeholder */}
        {sparkline && (
          <div className="mt-3 h-8 w-full border-b border-dashed border-atlas-border-subtle flex items-end">
             {/* If real chart engine was here, it would render a path. For stage 5 we just want to ensure it has space. */}
             <div className="h-full w-full opacity-20 bg-gradient-to-t from-atlas-blue to-transparent"></div>
          </div>
        )}
      </PanelContent>
    </Panel>
  )
}
