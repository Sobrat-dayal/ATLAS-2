"use client";

import React, { useState } from "react";
import { CLIENT_INVESTIGATION_PRESETS } from "@/lib/intelligence/v1/presets";
import { saveInvestigation } from "@/lib/intelligence/v1/api";
import {
  Sliders,
  Radio,
  Building2,
  Network,
  PieChart,
  Globe,
  Save,
  CheckCircle2,
  Bookmark
} from "lucide-react";

interface IntelligenceInvestigationWorkspaceProps {
  onNavigateToView: (view: string, entityOrEventId?: string) => void;
}

export function IntelligenceInvestigationWorkspace({
  onNavigateToView
}: IntelligenceInvestigationWorkspaceProps) {
  const [activePresetId, setActivePresetId] = useState<string>("preset_event_investigation");
  const [saveTitle, setSaveTitle] = useState<string>("");
  const [showSaveModal, setShowSaveModal] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const activePreset = CLIENT_INVESTIGATION_PRESETS[activePresetId] || CLIENT_INVESTIGATION_PRESETS.preset_event_investigation;

  const handleSave = async () => {
    if (!saveTitle.trim()) return;

    try {
      await saveInvestigation({
        investigation_id: `inv_${Date.now()}`,
        title: saveTitle,
        preset_id: activePresetId,
        context: {
          context_id: `ctx_${Date.now()}`,
          known_as_of: new Date().toISOString()
        }
      });
      setSavedSuccess(true);
      setTimeout(() => {
        setSavedSuccess(false);
        setShowSaveModal(false);
        setSaveTitle("");
      }, 1500);
    } catch (err) {
      console.error("Save investigation failed:", err);
    }
  };

  return (
    <div className="h-full flex flex-col bg-black text-zinc-100 font-mono text-xs select-none">
      {/* Investigation Toolbar */}
      <div className="p-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-zinc-500 uppercase text-[10px] font-semibold tracking-wider">
            INVESTIGATION PRESET:
          </span>
          <select
            value={activePresetId}
            onChange={(e) => setActivePresetId(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-zinc-200 font-medium focus:outline-none focus:border-sky-500"
          >
            {Object.values(CLIENT_INVESTIGATION_PRESETS).map((p) => (
              <option key={p.preset_id} value={p.preset_id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>

        {/* Action: Save Investigation */}
        <button
          onClick={() => setShowSaveModal(true)}
          className="px-3 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold flex items-center gap-1.5 transition-colors"
        >
          <Save className="w-3.5 h-3.5" />
          <span>SAVE INVESTIGATION</span>
        </button>
      </div>

      {/* Preset Description Banner */}
      <div className="px-4 py-2 bg-zinc-900/40 border-b border-zinc-800 flex items-center justify-between text-zinc-400 text-[11px]">
        <div>
          <span className="text-zinc-200 font-semibold">{activePreset.name}</span>: {activePreset.description}
        </div>
        <div className="text-[10px] text-zinc-500">
          Linked Channels: {activePreset.linking_channels.join(", ")}
        </div>
      </div>

      {/* Coordinated Multi-Panel Grid Layout */}
      <div className="flex-1 p-4 grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto">
        {activePreset.panels.map((panelType, idx) => (
          <div
            key={idx}
            className="bg-zinc-950 border border-zinc-800 rounded p-4 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-3">
                <div className="flex items-center gap-2 font-bold text-zinc-100 uppercase tracking-wider">
                  {panelType === "EVENT_MONITOR" && <Radio className="w-4 h-4 text-blue-400" />}
                  {panelType === "ENTITY_GRAPH" && <Network className="w-4 h-4 text-sky-400" />}
                  {panelType === "ENTITY_CONTEXT" && <Building2 className="w-4 h-4 text-purple-400" />}
                  {panelType === "EXPOSURE_SUMMARY" && <PieChart className="w-4 h-4 text-amber-400" />}
                  {panelType === "GEOGRAPHY_MAP" && <Globe className="w-4 h-4 text-emerald-400" />}
                  <span>{panelType.replace(/_/g, " ")}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  LINKED
                </span>
              </div>

              <p className="text-[11px] text-zinc-400 leading-relaxed mb-4">
                Interactive workspace panel synchronized through the{" "}
                <span className="text-zinc-200 font-mono">
                  {activePreset.linking_channels[0] || "global"}
                </span>{" "}
                linking channel.
              </p>
            </div>

            <button
              onClick={() => {
                if (panelType === "EVENT_MONITOR") onNavigateToView("EVENTS");
                if (panelType === "ENTITY_GRAPH") onNavigateToView("GRAPH");
                if (panelType === "ENTITY_CONTEXT") onNavigateToView("ENTITIES");
                if (panelType === "EXPOSURE_SUMMARY") onNavigateToView("EXPOSURE");
                if (panelType === "GEOGRAPHY_MAP") onNavigateToView("GEOGRAPHY");
              }}
              className="w-full py-2 rounded bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-sky-400 font-bold text-center"
            >
              Focus Full View →
            </button>
          </div>
        ))}
      </div>

      {/* Save Investigation Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-5 w-full max-w-md space-y-4">
            <div className="flex items-center gap-2 font-bold text-zinc-100 text-sm">
              <Bookmark className="w-4 h-4 text-sky-400" />
              <span>SAVE INVESTIGATION WORKSPACE</span>
            </div>
            <div>
              <label className="text-[10px] text-zinc-400 block mb-1">INVESTIGATION TITLE</label>
              <input
                type="text"
                value={saveTitle}
                onChange={(e) => setSaveTitle(e.target.value)}
                placeholder="e.g. FOMC Decision & Bank Exposure Analysis"
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-zinc-100 focus:outline-none focus:border-sky-500"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowSaveModal(false)}
                className="px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={!saveTitle.trim()}
                className="px-4 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold disabled:opacity-50 flex items-center gap-1.5"
              >
                {savedSuccess ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300" />
                    <span>SAVED!</span>
                  </>
                ) : (
                  <span>CONFIRM SAVE</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

