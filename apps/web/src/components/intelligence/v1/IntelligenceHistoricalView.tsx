"use client";

import React, { useState } from "react";
import { History, Calendar, Clock, AlertTriangle, CheckCircle2, RotateCcw } from "lucide-react";

interface IntelligenceHistoricalViewProps {
  asOfDate: string | null;
  onSetAsOfDate: (date: string | null) => void;
}

export function IntelligenceHistoricalView({
  asOfDate,
  onSetAsOfDate
}: IntelligenceHistoricalViewProps) {
  const [selectedDate, setSelectedDate] = useState<string>(
    asOfDate ? asOfDate.split("T")[0] : "2024-12-31"
  );
  const [selectedTime, setSelectedTime] = useState<string>("16:00");

  const handleApplyHistorical = () => {
    const isoString = new Date(`${selectedDate}T${selectedTime}:00Z`).toISOString();
    onSetAsOfDate(isoString);
  };

  const handleResetCurrent = () => {
    onSetAsOfDate(null);
  };

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none p-4 space-y-4 overflow-y-auto">
      {/* Historical Horizon Control Box */}
      <div className="bg-zinc-950 border border-zinc-800 rounded p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-amber-400" />
            <span className="font-semibold text-zinc-100 uppercase tracking-wider">
              POINT-IN-TIME HISTORICAL RESEARCH MODE (STAGE 138)
            </span>
          </div>
          <span className="text-[11px] text-zinc-400">
            Mode: {asOfDate ? "HISTORICAL SNAPSHOT" : "CURRENT (LIVE)"}
          </span>
        </div>

        <p className="text-[11px] text-zinc-400 leading-relaxed">
          Evaluate what information was verified and officially known at a specific past timestamp.
          All event claims, knowledge graph relations, and exposure calculations are bounded by this epoch,
          preventing look-ahead bias in quantitative research.
        </p>

        {/* Date and Time Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="text-[10px] text-zinc-400 block mb-1">KNOWN AS-OF DATE</label>
            <div className="flex items-center gap-1.5 bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5">
              <Calendar className="w-3.5 h-3.5 text-sky-400" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="bg-transparent text-zinc-200 focus:outline-none w-full"
              />
            </div>
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 block mb-1">UTC TIME</label>
            <div className="flex items-center gap-1.5 bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5">
              <Clock className="w-3.5 h-3.5 text-purple-400" />
              <input
                type="time"
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                className="bg-transparent text-zinc-200 focus:outline-none w-full"
              />
            </div>
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={handleApplyHistorical}
              className="px-4 py-1.5 rounded bg-amber-600 hover:bg-amber-500 text-white font-bold transition-colors w-full"
            >
              SET AS-OF EPOCH
            </button>
            {asOfDate && (
              <button
                onClick={handleResetCurrent}
                className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300"
                title="Reset to current live knowledge"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Prominent Zero Look-Ahead Bias Notice */}
      <div className="p-3 bg-amber-950/20 border border-amber-800/80 rounded flex items-start gap-2.5 text-amber-300">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-[11px] leading-relaxed">
          <span className="font-bold uppercase tracking-wider block">ZERO LOOK-AHEAD BIAS ENFORCEMENT</span>
          When Historical Mode is active, all subsequent amendments, retractions, or data releases published after the evaluation timestamp are strictly excluded.
        </div>
      </div>

      {/* Historical Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-3 rounded bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>UNIVERSAL EVENTS</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            Filters events by <code>occurred_at &lt;= as_of</code> and <code>published_at &lt;= as_of</code>.
          </div>
        </div>

        <div className="p-3 rounded bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="flex items-center gap-1.5 text-sky-400 font-bold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>KNOWLEDGE GRAPH</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            Extracts relationship topology where <code>valid_at &lt;= as_of</code>.
          </div>
        </div>

        <div className="p-3 rounded bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="flex items-center gap-1.5 text-purple-400 font-bold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>EXPOSURE ENGINE</span>
          </div>
          <div className="text-[11px] text-zinc-400">
            Employs point-in-time FX rates and historical financial statement filings.
          </div>
        </div>
      </div>
    </div>
  );
}
