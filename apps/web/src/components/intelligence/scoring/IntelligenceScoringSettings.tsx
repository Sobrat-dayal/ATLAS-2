"use client";

import React, { useState } from "react";
import { Sliders, ShieldCheck, CheckCircle2, Lock } from "lucide-react";

interface ScoringSettingsState {
  defaultObjective: string;
  selectedEntityId: string;
  portfolioId: string;
  minCoveragePct: number;
  candidateLimit: number;
}

interface IntelligenceScoringSettingsProps {
  onSaveSettings?: (settings: ScoringSettingsState) => void;
}

export function IntelligenceScoringSettings({ onSaveSettings }: IntelligenceScoringSettingsProps) {
  const [settings, setSettings] = useState<ScoringSettingsState>({
    defaultObjective: "EVENT_REVIEW_PRIORITY",
    selectedEntityId: "COMP_AAPL",
    portfolioId: "PORT_TECH_ALPHA",
    minCoveragePct: 50,
    candidateLimit: 25,
  });
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = () => {
    if (onSaveSettings) {
      onSaveSettings(settings);
    }
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <div className="h-full overflow-y-auto p-4 space-y-4 font-mono text-xs select-none bg-black text-zinc-100 max-w-2xl">
      <div className="p-3 bg-zinc-950 border border-zinc-800 rounded space-y-1">
        <h2 className="text-sm font-bold text-zinc-100 uppercase tracking-wider flex items-center gap-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          SCORING & PRIORITIZATION PREFERENCES
        </h2>
        <p className="text-[11px] text-zinc-400">
          Configure contextual research filters, default objective triage rules, and coverage thresholds.
        </p>
      </div>

      <div className="p-4 bg-zinc-950 border border-zinc-800 rounded space-y-4">
        {/* Default Objective */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
            DEFAULT SCORING OBJECTIVE
          </label>
          <select
            value={settings.defaultObjective}
            onChange={(e) => setSettings({ ...settings, defaultObjective: e.target.value })}
            className="w-full p-2 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 font-mono text-xs focus:outline-none focus:border-emerald-500"
          >
            <option value="EVENT_REVIEW_PRIORITY">EVENT_REVIEW_PRIORITY (Operational Triage Index)</option>
            <option value="EVENT_ENTITY_RELEVANCE">EVENT_ENTITY_RELEVANCE (Direct vs Indirect Graph Link)</option>
            <option value="PORTFOLIO_EVENT_ATTENTION">PORTFOLIO_EVENT_ATTENTION (Authorized Holdings NAV Weight)</option>
            <option value="GEOGRAPHIC_EVENT_RELEVANCE">GEOGRAPHIC_EVENT_RELEVANCE (Facility Buffer Proximity)</option>
            <option value="SOURCE_EVIDENCE_ASSESSMENT">SOURCE_EVIDENCE_ASSESSMENT (Grounding & Verification)</option>
          </select>
        </div>

        {/* Selected Entity Context */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
            DEFAULT TARGET ENTITY CONTEXT
          </label>
          <input
            type="text"
            value={settings.selectedEntityId}
            onChange={(e) => setSettings({ ...settings, selectedEntityId: e.target.value })}
            placeholder="e.g. COMP_AAPL"
            className="w-full p-2 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 font-mono text-xs focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Active Portfolio Context */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
            DEFAULT PORTFOLIO ATTENTION CONTEXT
          </label>
          <input
            type="text"
            value={settings.portfolioId}
            onChange={(e) => setSettings({ ...settings, portfolioId: e.target.value })}
            placeholder="e.g. PORT_TECH_ALPHA"
            className="w-full p-2 bg-zinc-900 border border-zinc-800 rounded text-zinc-200 font-mono text-xs focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Minimum Feature Coverage Threshold */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
            MINIMUM FEATURE COVERAGE THRESHOLD ({settings.minCoveragePct}%)
          </label>
          <input
            type="range"
            min="30"
            max="90"
            step="5"
            value={settings.minCoveragePct}
            onChange={(e) => setSettings({ ...settings, minCoveragePct: parseInt(e.target.value) })}
            className="w-full accent-emerald-500"
          />
          <span className="text-[10px] text-zinc-500 block">
            Events with feature coverage below this threshold will be marked INSUFFICIENT_DATA rather than scored partially.
          </span>
        </div>

        {/* Candidate Ranking Limit */}
        <div className="space-y-1.5">
          <label className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
            CANDIDATE RANKING LIMIT
          </label>
          <div className="flex gap-2">
            {[10, 25, 50, 100].map((lim) => (
              <button
                key={lim}
                type="button"
                onClick={() => setSettings({ ...settings, candidateLimit: lim })}
                className={`px-3 py-1.5 rounded border text-xs font-semibold ${
                  settings.candidateLimit === lim
                    ? "bg-emerald-600 border-emerald-500 text-white"
                    : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {lim} items
              </button>
            ))}
          </div>
        </div>

        {/* Global Governance Protection Notice */}
        <div className="p-3 bg-zinc-900/90 border border-zinc-800 rounded space-y-1 text-[10px] text-zinc-400">
          <div className="flex items-center gap-1.5 text-zinc-300 font-bold">
            <Lock className="w-3.5 h-3.5 text-amber-400" />
            <span>GLOBAL GOVERNANCE CONTROL</span>
          </div>
          <p>
            Personal preferences only alter your active viewing and filtering context. Modifying production model factor weights or activating candidate policies requires institutional <span className="text-zinc-200 font-semibold">RISK_ADMIN</span> credentials and governance board validation.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold text-xs transition-colors flex items-center justify-center gap-1.5"
        >
          {savedSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-white" />
              <span>Preferences Saved Successfully</span>
            </>
          ) : (
            <span>Apply Scoring Preferences</span>
          )}
        </button>
      </div>
    </div>
  );
}

