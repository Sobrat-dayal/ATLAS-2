"use client";

import React from "react";
import {
  GodsEyeInvestigationResult,
  GodsEyeMapFeature,
} from "@/lib/intelligence/gods-eye/types";
import {
  Building2,
  Network,
  PieChart,
  TrendingUp,
  ShieldCheck,
  FileText,
  AlertTriangle,
  Info,
  ExternalLink,
  ChevronRight,
  Crosshair,
} from "lucide-react";

interface GodsEyeInspectorProps {
  investigation: GodsEyeInvestigationResult | null;
  selectedFeature?: GodsEyeMapFeature | null;
  selectedEventId?: string | null;
  onClose?: () => void;
}

export function GodsEyeInspector({
  investigation,
  selectedFeature,
  selectedEventId,
  onClose,
}: GodsEyeInspectorProps) {
  if (!investigation) {
    return (
      <div className="h-full flex items-center justify-center p-6 text-zinc-500 font-mono text-xs">
        Select an entity, event, or map feature to inspect verified intelligence details.
      </div>
    );
  }

  const selectedEvent = selectedEventId
    ? investigation.events.find((e) => e.event_id === selectedEventId)
    : null;

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-l border-zinc-800 font-mono text-xs select-none overflow-y-auto divide-y divide-zinc-900">
      {/* Inspector Header */}
      <div className="p-3 bg-zinc-900/60 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Crosshair className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-semibold text-zinc-100 uppercase tracking-wider text-[11px]">
            Situational Deep Inspector
          </span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 text-xs px-1.5 py-0.5 rounded bg-zinc-800"
          >
            ✕
          </button>
        )}
      </div>

      {/* Selected Map Feature Card */}
      {selectedFeature && (
        <div className="p-3 bg-zinc-900/40">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 mb-1">
            <span className="font-semibold uppercase tracking-wider text-amber-400">
              Selected Spatial Feature
            </span>
            <span className="px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300">
              {selectedFeature.feature_type}
            </span>
          </div>

          <div className="font-bold text-zinc-100 text-sm mb-2">
            {selectedFeature.name}
          </div>

          <div className="space-y-1 text-[11px] text-zinc-300 bg-zinc-950 p-2 rounded border border-zinc-800">
            <div className="flex justify-between">
              <span className="text-zinc-500">Damage Assessment:</span>
              <span className="font-bold text-amber-400">{selectedFeature.damage_status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-500">Coordinates:</span>
              <span>[{selectedFeature.coordinates[0]?.toFixed(2)}, {selectedFeature.coordinates[1]?.toFixed(2)}]</span>
            </div>
            {selectedFeature.properties?.distance_to_epicenter_km && (
              <div className="flex justify-between text-amber-400 font-bold">
                <span>Distance to Epicenter:</span>
                <span>{selectedFeature.properties.distance_to_epicenter_km} km</span>
              </div>
            )}
            {selectedFeature.properties?.operator && (
              <div className="flex justify-between">
                <span className="text-zinc-500">Operator:</span>
                <span className="truncate">{selectedFeature.properties.operator}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Observational Market Context Card */}
      {investigation.market_context && (
        <div className="p-3">
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-400 font-semibold uppercase tracking-wider mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-sky-400" />
            <span>Observational Market Context</span>
          </div>

          <div className="bg-zinc-900/60 p-2.5 rounded border border-zinc-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-zinc-200">
                {investigation.market_context.benchmark_symbol}
              </span>
              <span
                className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                  investigation.market_context.pct_change >= 0
                    ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                    : "bg-rose-950 text-rose-400 border border-rose-800"
                }`}
              >
                {investigation.market_context.pct_change >= 0 ? "+" : ""}
                {investigation.market_context.pct_change.toFixed(2)}%
              </span>
            </div>

            <div className="flex justify-between text-[11px] text-zinc-400">
              <span>Window:</span>
              <span>{investigation.market_context.time_window}</span>
            </div>

            <div className="flex justify-between text-[11px] text-zinc-400">
              <span>Before: {investigation.market_context.price_before}</span>
              <span>After: {investigation.market_context.price_after}</span>
            </div>

            <div className="text-[10px] text-zinc-500 italic pt-1 border-t border-zinc-800/80">
              {investigation.market_context.disclaimer}
            </div>
          </div>
        </div>
      )}

      {/* Financial & Economic Exposure Card */}
      {investigation.exposure_summary && (
        <div className="p-3">
          <div className="flex items-center gap-1.5 text-[10px] text-zinc-400 font-semibold uppercase tracking-wider mb-2">
            <PieChart className="w-3.5 h-3.5 text-emerald-400" />
            <span>Financial Exposure Look-Through</span>
          </div>

          <div className="bg-zinc-900/60 p-2.5 rounded border border-zinc-800 space-y-1.5">
            <div className="flex justify-between text-[11px]">
              <span className="text-zinc-400">Target Entity:</span>
              <span className="font-bold text-zinc-200">
                {investigation.exposure_summary.entity_or_portfolio_id}
              </span>
            </div>

            {investigation.exposure_summary.gross_revenue_exposure_pct !== undefined && (
              <div className="flex justify-between text-[11px]">
                <span className="text-zinc-400">Revenue Concentration:</span>
                <span className="font-bold text-amber-400">
                  {investigation.exposure_summary.gross_revenue_exposure_pct}%
                </span>
              </div>
            )}

            {investigation.exposure_summary.supply_chain_tier1_concentration_pct !== undefined && (
              <div className="flex justify-between text-[11px]">
                <span className="text-zinc-400">Tier-1 Supply Chain:</span>
                <span className="font-bold text-zinc-200">
                  {investigation.exposure_summary.supply_chain_tier1_concentration_pct}%
                </span>
              </div>
            )}

            {investigation.exposure_summary.primary_vulnerable_corridor && (
              <div className="text-[11px] text-zinc-400">
                <span>Vulnerable Corridor: </span>
                <span className="text-zinc-200">
                  {investigation.exposure_summary.primary_vulnerable_corridor}
                </span>
              </div>
            )}

            <div className="text-[10px] text-zinc-500 italic pt-1 border-t border-zinc-800/80">
              {investigation.exposure_summary.disclaimer}
            </div>
          </div>
        </div>
      )}

      {/* Knowledge Graph Subgraph Overview */}
      <div className="p-3">
        <div className="flex items-center gap-1.5 text-[10px] text-zinc-400 font-semibold uppercase tracking-wider mb-2">
          <Network className="w-3.5 h-3.5 text-purple-400" />
          <span>Knowledge Graph Topology</span>
        </div>

        <div className="bg-zinc-900/60 p-2.5 rounded border border-zinc-800 space-y-1.5">
          <div className="flex justify-between text-[11px]">
            <span className="text-zinc-400">Root Node:</span>
            <span className="font-bold text-zinc-200">
              {investigation.knowledge_graph_subgraph.root_node}
            </span>
          </div>

          <div className="flex justify-between text-[11px]">
            <span className="text-zinc-400">Nodes / Edges Traversed:</span>
            <span>
              {investigation.knowledge_graph_subgraph.node_count} nodes /{" "}
              {investigation.knowledge_graph_subgraph.edge_count} edges (depth{" "}
              {investigation.knowledge_graph_subgraph.traversal_depth})
            </span>
          </div>

          <div className="divide-y divide-zinc-800/60 pt-1">
            {investigation.knowledge_graph_subgraph.edges.map((edge) => (
              <div key={edge.id} className="py-1 flex items-center justify-between text-[10px]">
                <span className="text-zinc-400 font-mono">{edge.predicate}</span>
                <span className="text-zinc-200 truncate ml-2">{edge.target}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Primary Evidence Sources */}
      <div className="p-3">
        <div className="flex items-center gap-1.5 text-[10px] text-zinc-400 font-semibold uppercase tracking-wider mb-2">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Verified Evidence Sources</span>
        </div>

        <div className="space-y-1.5">
          {investigation.evidence_sources.map((src) => (
            <div
              key={src.source_id}
              className="p-2 rounded bg-zinc-900 border border-zinc-800 flex items-center justify-between text-[11px]"
            >
              <div>
                <div className="font-semibold text-zinc-200">{src.name}</div>
                <div className="text-[10px] text-zinc-500">{src.source_type}</div>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[9px] bg-emerald-950/80 border border-emerald-800 text-emerald-400">
                {src.verification_tier}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Coverage & Limitations */}
      <div className="p-3 bg-zinc-950 text-[10px] text-zinc-500 space-y-1">
        <div className="font-semibold text-zinc-400 uppercase tracking-wider mb-1">
          Coverage Notes & Disclaimers
        </div>
        {investigation.coverage_notes.map((note, idx) => (
          <div key={idx} className="flex items-start gap-1">
            <span className="text-amber-500">•</span>
            <span>{note}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

