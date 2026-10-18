"use client";

/**
 * Chart Synchronization Manager Menu Popover for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Institutional Bloomberg/TradingView-inspired synchronization controls
 * - Group management (Group A, Group B, create group, rename, delete)
 * - Per-panel group membership assignment (P1 through P4)
 * - Independent per-property synchronization toggles:
 *   - Crosshair
 *   - Visible Time Range
 *   - Instrument
 *   - Interval
 *   - Chart Type
 *   - Drawings (with compatibility warnings)
 * - "Align Group to Active Panel" action
 * - "Return All to Independent Mode" action
 * - Informative compatibility and temporal alignment disclosures
 * - Full keyboard navigation and accessible aria labels
 */

import React, { useState } from "react";
import {
  Check,
  ChevronRight,
  Crosshair,
  ExternalLink,
  Layers,
  Link2,
  Maximize2,
  Plus,
  RefreshCw,
  RotateCcw,
  Sliders,
  Trash2,
  Unlink,
  X,
  Clock,
  CandlestickChart,
  Edit3,
} from "lucide-react";
import { useChartSync } from "@/hooks/charts";
import { ChartSyncGroup, ChartSyncProperty } from "@/lib/charts/sync";
import { MultiChartWorkspaceState } from "@/lib/charts/workspace";

export interface ChartSyncMenuProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceState: MultiChartWorkspaceState;
}

export function ChartSyncMenu({
  isOpen,
  onClose,
  workspaceState,
}: ChartSyncMenuProps) {
  const {
    groups,
    createGroup,
    deleteGroup,
    renameGroup,
    setGroupEnabled,
    toggleProperty,
    assignPanel,
    removePanel,
    resetToIndependentMode,
    alignGroupToPanel,
  } = useChartSync();

  const [selectedGroupId, setSelectedGroupId] = useState<string>(
    () => groups[0]?.id || "group-a"
  );
  const [isCreatingGroup, setIsCreatingGroup] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");

  if (!isOpen) return null;

  const activeGroup =
    groups.find((g) => g.id === selectedGroupId) || groups[0] || null;

  const handleCreateGroup = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;
    const created = createGroup(newGroupName.trim());
    setSelectedGroupId(created.id);
    setNewGroupName("");
    setIsCreatingGroup(false);
  };

  const activePanelId = workspaceState.activePanelId;
  const activePanel = workspaceState.panels[activePanelId];
  const activePanelIndex = workspaceState.panelIds.indexOf(activePanelId);
  const activePanelDisplay = `P${activePanelIndex >= 0 ? activePanelIndex + 1 : 1} (${activePanel?.symbol || "SPY"})`;

  return (
    <div
      role="dialog"
      aria-label="Chart Synchronization Controls"
      aria-modal="true"
      className="absolute top-full right-0 mt-2 w-96 max-h-[85vh] bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl z-50 flex flex-col overflow-hidden text-xs font-sans text-zinc-200 animate-in fade-in zoom-in-95 duration-100"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-zinc-900 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Link2 className="w-4 h-4 text-cyan-400" />
          <span className="font-mono font-bold tracking-wider text-zinc-100 uppercase text-xs">
            CHART SYNCHRONIZATION
          </span>
          <span className="px-1.5 py-0.2 bg-cyan-950 border border-cyan-800/80 text-cyan-300 font-mono text-[9px] rounded font-semibold">
            V1
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-100 transition-colors"
          title="Close Synchronization Menu"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="overflow-y-auto p-3 flex flex-col gap-3.5">
        {/* Group Selector Tabs */}
        <div>
          <div className="flex items-center justify-between mb-1.5 text-[11px] font-mono text-zinc-400">
            <span>SYNCHRONIZATION GROUPS</span>
            {!isCreatingGroup && groups.length < 4 && (
              <button
                type="button"
                onClick={() => setIsCreatingGroup(true)}
                className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <Plus className="w-3 h-3" />
                <span>New Group</span>
              </button>
            )}
          </div>

          {isCreatingGroup && (
            <form onSubmit={handleCreateGroup} className="flex items-center gap-1.5 mb-2">
              <input
                type="text"
                placeholder="Group name (e.g. Group C)"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                autoFocus
                className="flex-1 px-2 py-1 bg-zinc-900 border border-zinc-700 rounded text-xs text-zinc-100 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="px-2 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono font-semibold text-[11px]"
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setIsCreatingGroup(false)}
                className="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded text-[11px]"
              >
                Cancel
              </button>
            </form>
          )}

          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {groups.map((group) => {
              const isSelected = group.id === selectedGroupId;
              const memberCount = group.memberPanelIds.length;
              return (
                <button
                  key={group.id}
                  type="button"
                  onClick={() => setSelectedGroupId(group.id)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-mono transition-all ${
                    isSelected
                      ? "bg-zinc-900 border-cyan-500 text-zinc-100 shadow-sm"
                      : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                  }`}
                >
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: group.color }}
                  />
                  <span className="font-semibold">{group.name}</span>
                  <span
                    className={`px-1 py-0.2 rounded text-[9px] ${
                      group.enabled && memberCount > 0
                        ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20"
                        : "bg-zinc-800 text-zinc-500"
                    }`}
                  >
                    {memberCount}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {activeGroup && (
          <>
            {/* Active Group Settings Header & Master Enable Switch */}
            <div className="p-2.5 bg-zinc-900/80 border border-zinc-800/80 rounded flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: activeGroup.color }}
                  />
                  <span className="font-mono font-bold text-zinc-100 text-xs">
                    {activeGroup.name}
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    (Rev {activeGroup.revision})
                  </span>
                </div>
                <div className="text-[10px] text-zinc-400 mt-0.5 font-mono">
                  {activeGroup.enabled
                    ? `${activeGroup.memberPanelIds.length} panels linked`
                    : "Group synchronization is paused"}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setGroupEnabled(activeGroup.id, !activeGroup.enabled)}
                  className={`px-2.5 py-1 rounded text-xs font-mono font-semibold transition-colors ${
                    activeGroup.enabled
                      ? "bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-600/30"
                      : "bg-zinc-800 text-zinc-400 border border-zinc-700 hover:text-zinc-200"
                  }`}
                >
                  {activeGroup.enabled ? "ACTIVE" : "PAUSED"}
                </button>

                {groups.length > 1 && (
                  <button
                    type="button"
                    onClick={() => deleteGroup(activeGroup.id)}
                    title="Delete Group"
                    className="p-1 rounded text-zinc-500 hover:text-red-400 hover:bg-zinc-800 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>

            {/* Member Panel Assignment */}
            <div>
              <div className="text-[11px] font-mono text-zinc-400 mb-1.5 flex items-center justify-between">
                <span>ASSIGN PANELS TO {activeGroup.name.toUpperCase()}</span>
                <span className="text-[10px] text-zinc-500">Max 4 panels</span>
              </div>

              <div className="grid grid-cols-2 gap-1.5">
                {workspaceState.panelIds.map((panelId, idx) => {
                  const panel = workspaceState.panels[panelId];
                  const isMember = activeGroup.memberPanelIds.includes(panelId);
                  const isPanelActive = panelId === workspaceState.activePanelId;

                  return (
                    <button
                      key={panelId}
                      type="button"
                      onClick={() => {
                        if (isMember) {
                          removePanel(panelId);
                        } else {
                          assignPanel(panelId, activeGroup.id);
                        }
                      }}
                      className={`flex items-center justify-between p-2 rounded border text-xs font-mono transition-all text-left ${
                        isMember
                          ? "bg-cyan-950/40 border-cyan-500/60 text-zinc-100"
                          : "bg-zinc-950 border-zinc-800/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-300"
                      }`}
                    >
                      <div className="min-w-0">
                        <div className="flex items-center gap-1 font-semibold truncate">
                          <span>P{idx + 1}</span>
                          <span className="text-zinc-200">{panel?.symbol || "SPY"}</span>
                          {isPanelActive && (
                            <span className="text-[9px] text-cyan-400 font-normal">
                              (active)
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-zinc-500">
                          {panel?.interval || "1d"} • {panel?.renderMode || "candles"}
                        </div>
                      </div>

                      <div
                        className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ml-1 ${
                          isMember
                            ? "bg-cyan-500 border-cyan-400 text-black"
                            : "border-zinc-700 bg-zinc-900"
                        }`}
                      >
                        {isMember && <Check className="w-3 h-3 stroke-[3]" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Per-Property Synchronization Toggles */}
            <div>
              <div className="text-[11px] font-mono text-zinc-400 mb-1.5">
                SYNCHRONIZED PROPERTIES
              </div>

              <div className="flex flex-col gap-1 border border-zinc-800/80 rounded p-1.5 bg-zinc-950">
                {/* 1. Crosshair */}
                <PropertyToggleRow
                  icon={<Crosshair className="w-3.5 h-3.5 text-cyan-400" />}
                  label="Crosshairs & Time Guides"
                  description="Synchronizes vertical time cursor across panels at canonical UTC timestamp"
                  checked={activeGroup.settings.crosshair}
                  onChange={() => toggleProperty(activeGroup.id, "crosshair")}
                />

                {/* 2. Visible Time Range */}
                <PropertyToggleRow
                  icon={<Clock className="w-3.5 h-3.5 text-cyan-400" />}
                  label="Visible Time Range (Pan & Zoom)"
                  description="Synchronizes horizontal time axis scrolling and zooming with coverage clamping"
                  checked={activeGroup.settings.visibleTimeRange}
                  onChange={() => toggleProperty(activeGroup.id, "visibleTimeRange")}
                />

                {/* 3. Instrument */}
                <PropertyToggleRow
                  icon={<Layers className="w-3.5 h-3.5 text-cyan-400" />}
                  label="Financial Instrument"
                  description="Links canonical instrument and market series selection across member panels"
                  checked={activeGroup.settings.instrument}
                  onChange={() => toggleProperty(activeGroup.id, "instrument")}
                />

                {/* 4. Interval */}
                <PropertyToggleRow
                  icon={<Sliders className="w-3.5 h-3.5 text-cyan-400" />}
                  label="Timeframe Interval"
                  description="Synchronizes 1m, 5m, 1h, 1D chart intervals (preserving series availability)"
                  checked={activeGroup.settings.interval}
                  onChange={() => toggleProperty(activeGroup.id, "interval")}
                />

                {/* 5. Chart Type */}
                <PropertyToggleRow
                  icon={<CandlestickChart className="w-3.5 h-3.5 text-cyan-400" />}
                  label="Chart Render Mode"
                  description="Synchronizes Candlestick, Bar, Line, or Area presentation modes"
                  checked={activeGroup.settings.chartType}
                  onChange={() => toggleProperty(activeGroup.id, "chartType")}
                />

                {/* 6. Drawings */}
                <PropertyToggleRow
                  icon={<Edit3 className="w-3.5 h-3.5 text-amber-400" />}
                  label="Compatible Drawings"
                  description="Gated to identical canonical instrument and quotation currency"
                  checked={activeGroup.settings.drawings}
                  onChange={() => toggleProperty(activeGroup.id, "drawings")}
                  warning="Drawings require identical financial coordinates."
                />
              </div>
            </div>

            {/* Quick Actions Strip */}
            <div className="flex flex-col gap-1.5 pt-1 border-t border-zinc-800/80">
              <button
                type="button"
                onClick={() => alignGroupToPanel(activeGroup.id, activePanelId)}
                className="w-full py-1.5 px-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 rounded font-mono text-[11px] font-semibold text-cyan-300 flex items-center justify-center gap-1.5 transition-colors"
                title={`Align all members of ${activeGroup.name} to active panel ${activePanelDisplay}`}
              >
                <RefreshCw className="w-3 h-3 text-cyan-400" />
                <span>Align Group to Active Panel ({activePanelDisplay})</span>
              </button>

              <button
                type="button"
                onClick={resetToIndependentMode}
                className="w-full py-1.5 px-2 bg-zinc-950 hover:bg-zinc-900 border border-zinc-800 rounded font-mono text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center justify-center gap-1.5 transition-colors"
                title="Disconnect all panels and restore independent chart behavior"
              >
                <Unlink className="w-3 h-3 text-zinc-500" />
                <span>Restore All Panels to Independent Mode</span>
              </button>
            </div>
          </>
        )}

        {/* Financial Data Integrity Notice */}
        <div className="p-2 bg-zinc-900/40 border border-zinc-800/60 rounded text-[10px] text-zinc-400 font-mono leading-relaxed">
          <div className="font-semibold text-zinc-300 mb-0.5">
            INSTITUTIONAL SYNCHRONIZATION POLICY
          </div>
          <p>
            • Independent mode is the default; synchronization is opt-in.
            <br />
            • Crosshairs align strictly by UTC timestamp (never screen pixels).
            <br />
            • Different market calendars (crypto 24/7 vs equities) will never fabricate fake candles.
            <br />
            • Feedback loops and duplicate synchronization events are suppressed.
          </p>
        </div>
      </div>
    </div>
  );
}

interface PropertyToggleRowProps {
  icon: React.ReactNode;
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
  warning?: string;
}

function PropertyToggleRow({
  icon,
  label,
  description,
  checked,
  onChange,
  warning,
}: PropertyToggleRowProps) {
  return (
    <div
      onClick={onChange}
      className={`flex items-start justify-between gap-2 p-1.5 rounded cursor-pointer transition-colors ${
        checked ? "bg-zinc-900/90 text-zinc-100" : "hover:bg-zinc-900/50 text-zinc-400"
      }`}
    >
      <div className="flex items-start gap-2 min-w-0">
        <div className="mt-0.5">{icon}</div>
        <div>
          <div className="font-mono font-semibold text-xs flex items-center gap-1.5">
            <span>{label}</span>
            {warning && (
              <span className="text-[9px] text-amber-400/80 font-normal">
                ({warning})
              </span>
            )}
          </div>
          <div className="text-[10px] text-zinc-500 line-clamp-1">{description}</div>
        </div>
      </div>

      <div
        className={`w-7 h-4 rounded-full p-0.5 transition-colors shrink-0 mt-0.5 ${
          checked ? "bg-cyan-500" : "bg-zinc-800"
        }`}
      >
        <div
          className={`w-3 h-3 rounded-full bg-black transition-transform ${
            checked ? "translate-x-3" : "translate-x-0"
          }`}
        />
      </div>
    </div>
  );
}
