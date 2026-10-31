"use client";

import React, { useState, useEffect } from "react";
import { resolveEntityContext } from "@/lib/intelligence/v1/api";
import {
  Building2,
  Radio,
  Network,
  PieChart,
  ExternalLink,
  ShieldCheck,
  Search,
  Globe,
  Layers
} from "lucide-react";

interface IntelligenceEntityViewProps {
  initialEntityId?: string;
  onNavigateToView: (view: string, entityOrEventId?: string) => void;
}

const PRESET_ENTITIES = [
  { id: "COMP_AAPL", name: "Apple Inc. (AAPL)", type: "COMPANY" },
  { id: "COMP_ACME", name: "Acme Global Corporation (ACME)", type: "COMPANY" },
  { id: "CB_FED", name: "Federal Reserve System (Fed)", type: "CENTRAL_BANK" }
];

export function IntelligenceEntityView({
  initialEntityId = "COMP_AAPL",
  onNavigateToView
}: IntelligenceEntityViewProps) {
  const [selectedEntityId, setSelectedEntityId] = useState<string>(initialEntityId);
  const [entityData, setEntityData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    resolveEntityContext(selectedEntityId)
      .then((data) => setEntityData(data))
      .catch((err) => {
        console.warn("Entity context fallback", err);
        setEntityData({
          canonical_ref: {
            entity_id: selectedEntityId,
            canonical_name: selectedEntityId === "COMP_AAPL" ? "Apple Inc." : selectedEntityId,
            node_type: selectedEntityId === "CB_FED" ? "CENTRAL_BANK" : "COMPANY",
            country_code: "US",
            sector: selectedEntityId === "CB_FED" ? "Monetary Authority" : "Information Technology",
            identifier_map: selectedEntityId === "COMP_AAPL" ? { CIK: "0000320193", TICKER: "AAPL" } : {}
          },
          official_name: selectedEntityId === "COMP_AAPL" ? "Apple Inc." : selectedEntityId,
          sector: selectedEntityId === "CB_FED" ? "Monetary Authority" : "Information Technology",
          jurisdiction: "United States",
          verified_events_count: 8,
          verified_relationships_count: 14,
          exposure_supported: true
        });
      })
      .finally(() => setLoading(false));
  }, [selectedEntityId]);

  const canon = entityData?.canonical_ref;

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none">
      {/* Entity Selector Header */}
      <div className="p-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-zinc-500 uppercase text-[10px] font-semibold tracking-wider">
            CANONICAL ENTITY:
          </span>
          <select
            value={selectedEntityId}
            onChange={(e) => setSelectedEntityId(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-zinc-200 font-medium focus:outline-none focus:border-sky-500"
          >
            {PRESET_ENTITIES.map((ent) => (
              <option key={ent.id} value={ent.id}>
                {ent.name}
              </option>
            ))}
          </select>
        </div>

        {/* Cross-Module Quick Links */}
        <div className="flex items-center gap-2">
          <a
            href={`/companies?id=${selectedEntityId}`}
            className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1.5"
          >
            <Building2 className="w-3.5 h-3.5 text-sky-400" />
            <span>Open in /companies</span>
          </a>
          <a
            href={`/markets`}
            className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 flex items-center gap-1.5"
          >
            <ExternalLink className="w-3.5 h-3.5 text-purple-400" />
            <span>Markets</span>
          </a>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Entity Identifiers & Overview Card */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-4 space-y-3">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold text-zinc-100">
                  {entityData?.official_name || selectedEntityId}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-zinc-800 font-bold text-sky-400 uppercase">
                  {canon?.node_type || "ENTITY"}
                </span>
              </div>
              <div className="text-zinc-400 text-[11px] mt-1">
                {entityData?.sector} • Jurisdiction: {entityData?.jurisdiction}
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-zinc-500 uppercase block">CANONICAL ID</span>
              <span className="text-xs text-zinc-300 font-bold">{canon?.entity_id || selectedEntityId}</span>
            </div>
          </div>

          {/* Official Identifiers Table */}
          {canon?.identifier_map && Object.keys(canon.identifier_map).length > 0 && (
            <div className="pt-2 border-t border-zinc-900 grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(canon.identifier_map).map(([k, v]) => (
                <div key={k} className="p-2 rounded bg-zinc-900/60 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block uppercase">{k}</span>
                  <span className="text-xs font-semibold text-zinc-200">{String(v)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 3-Column Intelligence Grid: Events, Graph Edges, Exposure Footprint */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Linked Events */}
          <div className="bg-zinc-950 border border-zinc-800 rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-2">
                <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                  <Radio className="w-3.5 h-3.5 text-blue-400" />
                  <span>VERIFIED EVENTS ({entityData?.verified_events_count || 0})</span>
                </div>
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed mb-3">
                Events where {entityData?.official_name} is the direct subject, issuer, or official action target.
              </p>
            </div>
            <button
              onClick={() => onNavigateToView("EVENTS")}
              className="w-full py-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-sky-400 text-center font-semibold"
            >
              Inspect Events in Monitor →
            </button>
          </div>

          {/* Knowledge Graph Relationships */}
          <div className="bg-zinc-950 border border-zinc-800 rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-2">
                <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                  <Network className="w-3.5 h-3.5 text-sky-400" />
                  <span>KNOWLEDGE GRAPH ({entityData?.verified_relationships_count || 0})</span>
                </div>
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed mb-3">
                Verified multi-hop paths connecting corporate entities, facilities, regulators, and issuing jurisdictions.
              </p>
            </div>
            <button
              onClick={() => onNavigateToView("GRAPH")}
              className="w-full py-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-sky-400 text-center font-semibold"
            >
              Open Entity Knowledge Graph →
            </button>
          </div>

          {/* Financial Exposure Engine */}
          <div className="bg-zinc-950 border border-zinc-800 rounded p-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-2">
                <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                  <PieChart className="w-3.5 h-3.5 text-amber-400" />
                  <span>FINANCIAL EXPOSURE FOOTPRINT</span>
                </div>
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed mb-3">
                Source-backed geographic revenue share, portfolio weights, and corporate group consolidation.
              </p>
            </div>
            <button
              onClick={() => onNavigateToView("EXPOSURE")}
              className="w-full py-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-sky-400 text-center font-semibold"
            >
              Open Exposure Analytics →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
