"use client";

import React, { useState, useEffect } from "react";
import {
  AtlasIntelligenceScore,
  RankedItem,
  ScoreObjectiveId,
} from "@/lib/intelligence/scoring/types";
import { queryIntelligenceRankings } from "@/lib/intelligence/scoring/api";
import { IntelligenceRankingTable } from "./IntelligenceRankingTable";
import { IntelligenceScoreInspector } from "./IntelligenceScoreInspector";
import { IntelligenceModelDetails } from "./IntelligenceModelDetails";
import { IntelligenceScoringSettings } from "./IntelligenceScoringSettings";
import {
  Sliders,
  Radio,
  Building2,
  PieChart,
  Globe,
  Database,
  Layers,
  RefreshCw,
  Award,
} from "lucide-react";

interface IntelligenceScoringViewProps {
  asOfDate?: string | null;
  onNavigateToView?: (view: string, entityOrEventId?: string) => void;
}

const MOCK_CANDIDATE_EVENTS = [
  {
    event_id: "evt_fed_fomc_nov",
    title: "Federal Reserve FOMC Benchmark Rate Decision (5.25% - 5.50%)",
    published_at: "2024-11-01T18:00:00Z",
    valid_at: "2024-11-01T18:00:00Z",
    entities: [{ entity_id: "CB_FED", predicate: "ISSUED_BY" }],
    sources: [
      { source_id: "src_fed_1", name: "Federal Reserve Bulletin", source_type: "CENTRAL_BANK_BULLETIN" },
      { source_id: "src_wire_1", name: "Reuters Financial", article_fingerprint: "wire_fomc_1" },
    ],
  },
  {
    event_id: "evt_aapl_earnings_q4",
    title: "Apple Inc. Q4 Revenue & Form 10-K Annual Filing",
    published_at: "2024-10-31T20:30:00Z",
    valid_at: "2024-10-31T20:30:00Z",
    entities: [{ entity_id: "COMP_AAPL", predicate: "ISSUED_BY" }],
    sources: [
      { source_id: "sec_edgar_1", name: "SEC EDGAR Form 10-K", source_type: "OFFICIAL_REGULATORY" },
      { source_id: "src_pr_1", name: "Apple PR News", article_fingerprint: "wire_aapl_q4" },
    ],
  },
  {
    event_id: "evt_quake_shizuoka",
    title: "Magnitude 5.8 Seismic Activity (Shizuoka Prefecture, Japan)",
    published_at: "2024-11-01T04:15:00Z",
    valid_at: "2024-11-01T04:15:00Z",
    proximity_km: 14.2,
    sources: [
      { source_id: "usgs_1", name: "USGS Earthquake Hazards", source_type: "OFFICIAL_GOVERNMENT" },
    ],
  },
  {
    event_id: "evt_acme_supply_chain",
    title: "Acme Global Manufacturing Supply Chain Disruption Notice",
    published_at: "2024-10-30T14:00:00Z",
    valid_at: "2024-10-30T14:00:00Z",
    entities: [{ entity_id: "COMP_ACME", predicate: "ISSUED_BY" }],
    sources: [
      { source_id: "wire_trade_1", name: "Industrial Daily", article_fingerprint: "wire_acme_ind" },
    ],
  },
];

export function IntelligenceScoringView({ asOfDate, onNavigateToView }: IntelligenceScoringViewProps) {
  const [subTab, setSubTab] = useState<"RANKING" | "MODELS" | "SETTINGS">("RANKING");
  const [selectedObjective, setSelectedObjective] = useState<ScoreObjectiveId>("EVENT_REVIEW_PRIORITY");
  const [rankedItems, setRankedItems] = useState<RankedItem[]>([]);
  const [selectedScore, setSelectedScore] = useState<AtlasIntelligenceScore | null>(null);
  const [loading, setLoading] = useState(false);

  const loadRankings = () => {
    setLoading(true);
    queryIntelligenceRankings({
      candidate_events: MOCK_CANDIDATE_EVENTS,
      objective_id: selectedObjective,
      known_as_of: asOfDate || undefined,
      context: {
        selected_entity_id: "COMP_AAPL",
        portfolio_context: {
          portfolio_id: "PORT_TECH_ALPHA",
          holding_weight_pct: 18.5,
          tenant_id: "default_tenant",
        },
      },
      limit: 25,
    })
      .then((items) => {
        setRankedItems(items);
        if (items.length > 0 && !selectedScore) {
          setSelectedScore(items[0].score);
        }
      })
      .catch((err) => {
        console.warn("Could not query rankings:", err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadRankings();
  }, [selectedObjective, asOfDate]);

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none overflow-hidden">
      {/* Top Filter and Objective Switcher Bar */}
      <div className="p-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          {/* SubTab navigation */}
          <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 p-0.5 rounded">
            <button
              onClick={() => setSubTab("RANKING")}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                subTab === "RANKING"
                  ? "bg-emerald-600 text-white font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Prioritized Ranking</span>
            </button>
            <button
              onClick={() => setSubTab("MODELS")}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                subTab === "MODELS"
                  ? "bg-sky-600 text-white font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Award className="w-3.5 h-3.5" />
              <span>Model Registry</span>
            </button>
            <button
              onClick={() => setSubTab("SETTINGS")}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                subTab === "SETTINGS"
                  ? "bg-zinc-800 text-white font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Settings</span>
            </button>
          </div>

          {/* Objective Switcher Dropdown (when on Ranking view) */}
          {subTab === "RANKING" && (
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">OBJECTIVE:</span>
              <select
                value={selectedObjective}
                onChange={(e) => setSelectedObjective(e.target.value as ScoreObjectiveId)}
                className="px-2.5 py-1 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 font-mono text-xs focus:outline-none focus:border-emerald-500"
              >
                <option value="EVENT_REVIEW_PRIORITY">Event Review Priority</option>
                <option value="EVENT_ENTITY_RELEVANCE">Entity Relevance (COMP_AAPL)</option>
                <option value="PORTFOLIO_EVENT_ATTENTION">Portfolio Attention (PORT_ALPHA)</option>
                <option value="GEOGRAPHIC_EVENT_RELEVANCE">Geographic Proximity</option>
                <option value="SOURCE_EVIDENCE_ASSESSMENT">Source Evidence Assessment</option>
              </select>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {asOfDate && (
            <span className="px-2 py-0.5 rounded bg-amber-950/80 border border-amber-800 text-amber-300 text-[10px]">
              AS-OF: {asOfDate.split("T")[0]}
            </span>
          )}
          <button
            onClick={loadRankings}
            className="p-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 transition-colors"
            title="Refresh Scores"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Workspace Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {subTab === "RANKING" && (
          <div className="h-full flex overflow-hidden">
            {/* Left: Ranked Events Table */}
            <div className={`h-full overflow-hidden flex-1 ${selectedScore ? "border-r border-zinc-800" : ""}`}>
              <IntelligenceRankingTable
                rankedItems={rankedItems}
                selectedScoreId={selectedScore?.score_id}
                onSelectScore={setSelectedScore}
                loading={loading}
              />
            </div>

            {/* Right: Deep Score Inspector */}
            {selectedScore && (
              <div className="w-96 shrink-0 h-full overflow-hidden">
                <IntelligenceScoreInspector
                  score={selectedScore}
                  onClose={() => setSelectedScore(null)}
                />
              </div>
            )}
          </div>
        )}

        {subTab === "MODELS" && <IntelligenceModelDetails />}

        {subTab === "SETTINGS" && <IntelligenceScoringSettings />}
      </div>
    </div>
  );
}
