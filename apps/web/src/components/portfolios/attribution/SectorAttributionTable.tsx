"use client";

import React, { useState } from "react";
import {
  formatBps,
  formatPercent,
  formatWeight,
  getEffectColorClass,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionCategoryDTO, AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import { ChevronDown, ChevronRight, Layers, SlidersHorizontal } from "lucide-react";

interface SectorAttributionTableProps {
  run: AttributionRunDTO;
}

export function SectorAttributionTable({ run }: SectorAttributionTableProps) {
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [sortField, setSortField] = useState<string>("total_effect");
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const toggleExpand = (catId: string) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [catId]: !prev[catId],
    }));
  };

  const sortedCategories = [...run.category_results].sort((a, b) => {
    const valA = parseFloat((a as any)[sortField] || "0");
    const valB = parseFloat((b as any)[sortField] || "0");
    return sortAsc ? valA - valB : valB - valA;
  });

  const handleHeaderClick = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      <div className="flex items-center justify-between border-b border-atlas-border-default/40 p-4">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            GICS Sector Performance Attribution
          </h3>
          <p className="text-xs text-atlas-text-secondary">
            Two-tier Brinson-Fachler decomposition across {run.category_results.length} market segments vs. {run.benchmark_name}.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-emerald-400" /> Positive Effect
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-rose-400" /> Negative Detraction
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary">
            <tr>
              <th
                className="cursor-pointer px-3 py-2.5 font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("category_label")}
              >
                Sector / Segment
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("portfolio_weight")}
              >
                Port Wgt
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("benchmark_weight")}
              >
                Bench Wgt
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("weight_delta")}
              >
                Active Wgt
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("portfolio_return")}
              >
                Port Ret
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("benchmark_return")}
              >
                Bench Ret
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                onClick={() => handleHeaderClick("return_delta")}
              >
                Excess Ret
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium text-atlas-accent hover:underline"
                onClick={() => handleHeaderClick("allocation_effect")}
              >
                Allocation
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium text-atlas-accent hover:underline"
                onClick={() => handleHeaderClick("selection_effect")}
              >
                Selection
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-medium text-atlas-accent hover:underline"
                onClick={() => handleHeaderClick("interaction_effect")}
              >
                Interaction
              </th>
              <th
                className="cursor-pointer px-3 py-2.5 text-right font-semibold text-atlas-text-primary hover:underline"
                onClick={() => handleHeaderClick("total_effect")}
              >
                Total Effect
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/40 text-atlas-text-primary">
            {sortedCategories.map((cat) => {
              const hasSubs = cat.sub_industries && cat.sub_industries.length > 0;
              const isExpanded = !!expandedCategories[cat.category_id];

              return (
                <React.Fragment key={cat.category_id}>
                  <tr className="hover:bg-atlas-surface-2/40 transition-colors">
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1.5 font-sans font-medium">
                        {hasSubs ? (
                          <button
                            onClick={() => toggleExpand(cat.category_id)}
                            className="text-atlas-text-muted hover:text-atlas-text-primary"
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-3.5 w-3.5" />
                            ) : (
                              <ChevronRight className="h-3.5 w-3.5" />
                            )}
                          </button>
                        ) : (
                          <span className="w-3.5" />
                        )}
                        <span>{cat.category_label}</span>
                        {cat.position_count > 0 && (
                          <span className="rounded bg-atlas-surface-3 px-1 text-[10px] text-atlas-text-muted font-mono">
                            {cat.position_count} pos
                          </span>
                        )}
                        {cat.is_residual && (
                          <span className="rounded bg-amber-500/10 px-1 text-[10px] text-amber-400 border border-amber-500/20">
                            Cash / Off-Bench
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-right">{formatWeight(cat.portfolio_weight)}</td>
                    <td className="px-3 py-2 text-right">{formatWeight(cat.benchmark_weight)}</td>
                    <td className={`px-3 py-2 text-right ${getEffectColorClass(cat.weight_delta)}`}>
                      {formatPercent(cat.weight_delta, 2, true)}
                    </td>
                    <td className="px-3 py-2 text-right">{formatPercent(cat.portfolio_return, 2, true)}</td>
                    <td className="px-3 py-2 text-right">{formatPercent(cat.benchmark_return, 2, true)}</td>
                    <td className={`px-3 py-2 text-right ${getEffectColorClass(cat.return_delta)}`}>
                      {formatPercent(cat.return_delta, 2, true)}
                    </td>
                    <td className={`px-3 py-2 text-right font-medium ${getEffectColorClass(cat.allocation_effect)}`}>
                      {formatPercent(cat.allocation_effect, 2, true)}
                    </td>
                    <td className={`px-3 py-2 text-right font-medium ${getEffectColorClass(cat.selection_effect)}`}>
                      {formatPercent(cat.selection_effect, 2, true)}
                    </td>
                    <td className={`px-3 py-2 text-right font-medium ${getEffectColorClass(cat.interaction_effect)}`}>
                      {formatPercent(cat.interaction_effect, 2, true)}
                    </td>
                    <td className={`px-3 py-2 text-right font-bold ${getEffectColorClass(cat.total_effect)}`}>
                      {formatPercent(cat.total_effect, 2, true)}
                    </td>
                  </tr>

                  {/* Expanded Sub-Industries */}
                  {isExpanded &&
                    cat.sub_industries?.map((sub) => (
                      <tr
                        key={sub.category_id}
                        className="bg-atlas-surface-2/20 text-atlas-text-secondary hover:bg-atlas-surface-2/50 transition-colors"
                      >
                        <td className="py-1.5 pl-8 pr-3 font-sans text-[11px]">
                          ↳ {sub.category_label}
                        </td>
                        <td className="px-3 py-1.5 text-right">{formatWeight(sub.portfolio_weight)}</td>
                        <td className="px-3 py-1.5 text-right">{formatWeight(sub.benchmark_weight)}</td>
                        <td className={`px-3 py-1.5 text-right ${getEffectColorClass(sub.weight_delta)}`}>
                          {formatPercent(sub.weight_delta, 2, true)}
                        </td>
                        <td className="px-3 py-1.5 text-right">{formatPercent(sub.portfolio_return, 2, true)}</td>
                        <td className="px-3 py-1.5 text-right">{formatPercent(sub.benchmark_return, 2, true)}</td>
                        <td className={`px-3 py-1.5 text-right ${getEffectColorClass(sub.return_delta)}`}>
                          {formatPercent(sub.return_delta, 2, true)}
                        </td>
                        <td className={`px-3 py-1.5 text-right ${getEffectColorClass(sub.allocation_effect)}`}>
                          {formatPercent(sub.allocation_effect, 2, true)}
                        </td>
                        <td className={`px-3 py-1.5 text-right ${getEffectColorClass(sub.selection_effect)}`}>
                          {formatPercent(sub.selection_effect, 2, true)}
                        </td>
                        <td className={`px-3 py-1.5 text-right ${getEffectColorClass(sub.interaction_effect)}`}>
                          {formatPercent(sub.interaction_effect, 2, true)}
                        </td>
                        <td className={`px-3 py-1.5 text-right font-semibold ${getEffectColorClass(sub.total_effect)}`}>
                          {formatPercent(sub.total_effect, 2, true)}
                        </td>
                      </tr>
                    ))}
                </React.Fragment>
              );
            })}
          </tbody>
          <tfoot className="border-t-2 border-atlas-border-default/80 bg-atlas-surface-2/80 font-semibold text-atlas-text-primary">
            <tr>
              <td className="px-3 py-2.5 font-sans">Total Portfolio Attribution</td>
              <td className="px-3 py-2.5 text-right">100.00%</td>
              <td className="px-3 py-2.5 text-right">100.00%</td>
              <td className="px-3 py-2.5 text-right">0.00%</td>
              <td className="px-3 py-2.5 text-right">{formatPercent(run.portfolio_return, 2, true)}</td>
              <td className="px-3 py-2.5 text-right">{formatPercent(run.benchmark_return, 2, true)}</td>
              <td className={`px-3 py-2.5 text-right ${getEffectColorClass(run.active_return)}`}>
                {formatPercent(run.active_return, 2, true)}
              </td>
              <td className={`px-3 py-2.5 text-right ${getEffectColorClass(run.total_allocation_effect)}`}>
                {formatPercent(run.total_allocation_effect, 2, true)}
              </td>
              <td className={`px-3 py-2.5 text-right ${getEffectColorClass(run.total_selection_effect)}`}>
                {formatPercent(run.total_selection_effect, 2, true)}
              </td>
              <td className={`px-3 py-2.5 text-right ${getEffectColorClass(run.total_interaction_effect)}`}>
                {formatPercent(run.total_interaction_effect, 2, true)}
              </td>
              <td className={`px-3 py-2.5 text-right text-sm font-bold ${getEffectColorClass(run.total_attributed)}`}>
                {formatPercent(run.total_attributed, 2, true)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

