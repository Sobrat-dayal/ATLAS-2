"use client";

import React from "react";
import {
  HeatmapLeafNode,
  describeExclusionReason,
  formatMarketCap,
  formatPrice,
  formatSignedPercent,
} from "@/lib/markets/heatmaps";

interface HeatmapAccessibleTableProps {
  nodes: HeatmapLeafNode[];
  selectedNode: HeatmapLeafNode | null;
  onSelectNode: (node: HeatmapLeafNode) => void;
  weightUnit?: string | null;
}

export function HeatmapAccessibleTable({
  nodes,
  selectedNode,
  onSelectNode,
  weightUnit = "USD",
}: HeatmapAccessibleTableProps) {
  return (
    <div className="w-full overflow-x-auto rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]">
      <table
        className="w-full text-left text-xs text-[var(--atlas-text-secondary)] border-collapse"
        aria-label="Accessible market heatmap data table"
      >
        <caption className="sr-only">
          Institutional market heatmap constituent table with qualified returns, market capitalization weights, and data freshness.
        </caption>
        <thead className="bg-[var(--atlas-surface-elevated)] text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] border-b border-[var(--atlas-border-subtle)] select-none">
          <tr>
            <th scope="col" className="p-3">Symbol</th>
            <th scope="col" className="p-3">Name</th>
            <th scope="col" className="p-3">Sector</th>
            <th scope="col" className="p-3 text-right">Return %</th>
            <th scope="col" className="p-3 text-right">Price</th>
            <th scope="col" className="p-3 text-right">Reference</th>
            <th scope="col" className="p-3 text-right">Market Cap</th>
            <th scope="col" className="p-3 text-right">Weight</th>
            <th scope="col" className="p-3 text-center">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--atlas-border-subtle)] font-mono text-[11px]">
          {nodes.map((node) => {
            const isSelected = selectedNode?.node_id === node.node_id;
            const isPos = (Number(node.percent_change) || 0) >= 0;

            return (
              <tr
                key={node.node_id}
                role="button"
                tabIndex={0}
                onClick={() => onSelectNode(node)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelectNode(node);
                  }
                }}
                className={`hover:bg-[var(--atlas-surface-elevated)]/60 cursor-pointer transition-colors ${
                  isSelected ? "bg-[var(--atlas-surface-elevated)] font-semibold" : ""
                }`}
              >
                <td className="p-3 font-bold text-[var(--atlas-text-primary)]">
                  {node.symbol}
                </td>
                <td className="p-3 font-sans truncate max-w-[180px] text-[var(--atlas-text-primary)]">
                  {node.display_name}
                </td>
                <td className="p-3 font-sans text-[var(--atlas-text-secondary)]">
                  {node.sector || "Unclassified"}
                </td>
                <td
                  className={`p-3 text-right font-bold ${
                    node.percent_change !== null && node.percent_change !== undefined
                      ? isPos
                        ? "text-emerald-400"
                        : "text-red-400"
                      : "text-zinc-500"
                  }`}
                >
                  {formatSignedPercent(node.percent_change)}
                </td>
                <td className="p-3 text-right text-[var(--atlas-text-secondary)]">
                  {formatPrice(node.current_price, node.currency)}
                </td>
                <td className="p-3 text-right text-[var(--atlas-text-tertiary)]">
                  {formatPrice(node.reference_price, node.currency)}
                </td>
                <td className="p-3 text-right text-[var(--atlas-text-primary)] font-semibold">
                  {formatMarketCap(node.weight_value, weightUnit || "USD")}
                </td>
                <td className="p-3 text-right text-[var(--atlas-text-secondary)]">
                  {node.normalized_weight
                    ? `${(Number(node.normalized_weight) * 100).toFixed(2)}%`
                    : "—"}
                </td>
                <td className="p-3 text-center">
                  <span
                    className={`inline-block px-1.5 py-0.5 rounded text-[10px] ${
                      node.is_qualified
                        ? "bg-emerald-950/80 text-emerald-400 border border-emerald-800/40"
                        : "bg-amber-950/80 text-amber-400 border border-amber-800/40"
                    }`}
                    title={node.exclusion_reason ? describeExclusionReason(node.exclusion_reason) : "Qualified"}
                  >
                    {node.is_qualified ? "Qualified" : "Excluded"}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
