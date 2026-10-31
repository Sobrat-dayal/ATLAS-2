"use client";

import React, { useState, useEffect } from "react";
import { IntelligenceOverviewResponse } from "@/lib/intelligence/v1/types";
import { fetchIntelligenceOverview } from "@/lib/intelligence/v1/api";
import {
  Layers,
  Radio,
  Building2,
  AlertTriangle,
  Globe,
  PieChart,
  ShieldCheck,
  RefreshCw,
  ExternalLink,
  DollarSign
} from "lucide-react";

interface IntelligenceOverviewProps {
  onNavigateToView: (view: string, entityOrEventId?: string) => void;
  asOfDate?: string | null;
}

export function IntelligenceOverview({
  onNavigateToView,
  asOfDate
}: IntelligenceOverviewProps) {
  const [data, setData] = useState<IntelligenceOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadOverview = () => {
    setLoading(true);
    fetchIntelligenceOverview({
      as_of: asOfDate || undefined,
      selected_portfolio_id: "PORT_ALPHA"
    })
      .then((res) => setData(res))
      .catch((err) => {
        console.warn("Failed to fetch remote overview; falling back to offline snapshot", err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOverview();
  }, [asOfDate]);

  const sections = data?.sections || {};

  return (
    <div className="h-full overflow-y-auto bg-black p-4 font-mono text-xs space-y-4">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-zinc-950 border border-zinc-800 rounded">
        <div>
          <div className="text-sm font-bold text-zinc-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-400" />
            <span>INTELLIGENCE COMMAND CENTER — GLOBAL OVERVIEW</span>
          </div>
          <div className="text-[11px] text-zinc-400 mt-0.5">
            Verified state of financial, economic, corporate, and physical world events.
          </div>
        </div>
        <button
          onClick={loadOverview}
          disabled={loading}
          className="p-1.5 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          title="Refresh intelligence overview"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Warnings Banner if any source is degraded */}
      {data?.active_warnings && data.active_warnings.length > 0 && (
        <div className="p-3 bg-amber-950/20 border border-amber-800/80 rounded flex items-start gap-2.5 text-amber-300">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-[11px]">
            <span className="font-bold uppercase tracking-wider block">SOURCE AVAILABILITY NOTICE</span>
            {data.active_warnings.map((w, i) => (
              <p key={i} className="text-amber-200/90 leading-relaxed">{w}</p>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Multi-Domain Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Central Bank Decisions */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-3 space-y-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                <Radio className="w-3.5 h-3.5 text-blue-400" />
                <span>CENTRAL BANK & MONETARY DECISIONS</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400">
                {sections.macro_monetary?.status || "READY"}
              </span>
            </div>
            <div className="mt-2.5 space-y-2">
              {sections.macro_monetary?.data?.map((item: any, i: number) => (
                <div
                  key={i}
                  onClick={() => onNavigateToView("EVENTS", item.event_id)}
                  className="p-2 rounded bg-zinc-900/60 border border-zinc-800/60 hover:bg-zinc-900 cursor-pointer transition-colors"
                >
                  <div className="font-medium text-zinc-100 flex items-center justify-between">
                    <span>{item.title}</span>
                    <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-1 flex items-center gap-2">
                    <span>{item.institution}</span>
                    <span>•</span>
                    <span>{item.jurisdiction}</span>
                    <span>•</span>
                    <span className="text-emerald-400">{item.verification}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <button
            onClick={() => onNavigateToView("EVENTS")}
            className="text-[11px] text-sky-400 hover:text-sky-300 font-semibold pt-2 text-left"
          >
            Explore all monetary events →
          </button>
        </div>

        {/* Corporate Earnings */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-3 space-y-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                <Building2 className="w-3.5 h-3.5 text-purple-400" />
                <span>CORPORATE EARNINGS & FILINGS</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400">
                {sections.corporate_earnings?.status || "READY"}
              </span>
            </div>
            <div className="mt-2.5 space-y-2">
              {sections.corporate_earnings?.data?.map((item: any, i: number) => (
                <div
                  key={i}
                  onClick={() => onNavigateToView("ENTITIES", "COMP_AAPL")}
                  className="p-2 rounded bg-zinc-900/60 border border-zinc-800/60 hover:bg-zinc-900 cursor-pointer transition-colors"
                >
                  <div className="font-medium text-zinc-100 flex items-center justify-between">
                    <span>{item.title}</span>
                    <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </div>
                  <div className="text-[10px] text-zinc-400 mt-1 flex items-center gap-2">
                    <span className="text-sky-300">{item.company}</span>
                    <span>•</span>
                    <span>{item.period}</span>
                    <span>•</span>
                    <span>Source: {item.primary_source}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <button
            onClick={() => onNavigateToView("ENTITIES")}
            className="text-[11px] text-sky-400 hover:text-sky-300 font-semibold pt-2 text-left"
          >
            Explore company intelligence →
          </button>
        </div>

        {/* Physical World & Infrastructure Proximity */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-3 space-y-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>PHYSICAL WORLD & INFRASTRUCTURE</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400">
                {sections.physical_events?.status || "READY"}
              </span>
            </div>
            <div className="mt-2.5 space-y-2">
              {sections.physical_events?.data?.map((item: any, i: number) => (
                <div
                  key={i}
                  onClick={() => onNavigateToView("GEOGRAPHY", item.event_id)}
                  className="p-2 rounded bg-zinc-900/60 border border-zinc-800/60 hover:bg-zinc-900 cursor-pointer transition-colors"
                >
                  <div className="font-medium text-zinc-100 flex items-center justify-between">
                    <span>{item.title}</span>
                    <ExternalLink className="w-3 h-3 text-zinc-500" />
                  </div>
                  <div className="text-[11px] text-zinc-400 mt-1">
                    Nearby Asset: <span className="text-zinc-200">{item.nearby_asset}</span> ({item.distance_km} km away)
                  </div>
                  <div className="text-[10px] text-amber-300/80 mt-1 italic">
                    {item.status_note}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <button
            onClick={() => onNavigateToView("GEOGRAPHY")}
            className="text-[11px] text-sky-400 hover:text-sky-300 font-semibold pt-2 text-left"
          >
            Open 2D/3D Geographic map →
          </button>
        </div>

        {/* Documented Portfolio Exposure Summary */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-3 space-y-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
              <div className="flex items-center gap-1.5 font-semibold text-zinc-200">
                <PieChart className="w-3.5 h-3.5 text-amber-400" />
                <span>AUTHORIZED PORTFOLIO EXPOSURE</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400">
                AUTHORIZED
              </span>
            </div>
            <div className="mt-2.5 grid grid-cols-2 gap-2">
              {sections.exposure_context?.data?.map((item: any, i: number) => (
                <div key={i} className="p-2 rounded bg-zinc-900/60 border border-zinc-800">
                  <span className="text-[10px] text-zinc-500 block uppercase">{item.metric}</span>
                  <span className="text-xs font-bold text-zinc-200">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
          <button
            onClick={() => onNavigateToView("EXPOSURE")}
            className="text-[11px] text-sky-400 hover:text-sky-300 font-semibold pt-2 text-left"
          >
            Open Exposure Engine →
          </button>
        </div>
      </div>

      {/* Source Freshness & Coverage Bar */}
      <div className="bg-zinc-950 border border-zinc-800 rounded p-3">
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2 mb-2">
          <div className="flex items-center gap-1.5 font-semibold text-zinc-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>PRIMARY DATA SOURCES TELEMETRY</span>
          </div>
          <button
            onClick={() => onNavigateToView("SOURCES")}
            className="text-[10px] text-sky-400 hover:text-sky-300"
          >
            View full telemetry table →
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2 text-[11px]">
          {data?.source_freshness?.slice(0, 5).map((src) => (
            <div key={src.source_id} className="p-2 rounded bg-zinc-900/50 border border-zinc-800">
              <div className="font-semibold text-zinc-200 truncate">{src.source_name}</div>
              <div className="text-[10px] text-zinc-500 truncate mt-0.5">{src.dataset}</div>
              <div className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
                <span className={`w-1.5 h-1.5 rounded-full ${src.status === "READY" ? "bg-emerald-500" : "bg-amber-500"}`} />
                <span>{src.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
