"use client";

import React, { useEffect, useState } from "react";
import { Wrench, Shield, Check, RefreshCw } from "lucide-react";
import { fetchAiToolPreferences, fetchAiTools, updateAiToolPreferences } from "@/lib/ai/tools/api";
import { AiToolDescriptor, AiToolPreferences } from "@/lib/ai/tools/types";

interface AiToolSettingsProps {
  onClose?: () => void;
}

export function AiToolSettings({ onClose }: AiToolSettingsProps) {
  const [tools, setTools] = useState<AiToolDescriptor[]>([]);
  const [prefs, setPrefs] = useState<AiToolPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [toolsData, prefsData] = await Promise.all([
          fetchAiTools(undefined, true),
          fetchAiToolPreferences(),
        ]);
        setTools(toolsData);
        setPrefs(prefsData);
      } catch (err) {
        console.error("Failed to load AI tool settings:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleToggleAutoApprove = () => {
    if (!prefs) return;
    setPrefs({ ...prefs, auto_approve_read_only: !prefs.auto_approve_read_only });
  };

  const handleToggleSensitive = () => {
    if (!prefs) return;
    setPrefs({ ...prefs, require_approval_for_sensitive: !prefs.require_approval_for_sensitive });
  };

  const handleToggleTool = (toolId: string) => {
    if (!prefs) return;
    const isCurrentlyDisabled = prefs.disabled_tools.includes(toolId);
    let newDisabled = [...prefs.disabled_tools];
    if (isCurrentlyDisabled) {
      newDisabled = newDisabled.filter((id) => id !== toolId);
    } else {
      newDisabled.push(toolId);
    }
    setPrefs({ ...prefs, disabled_tools: newDisabled });
  };

  const handleSave = async () => {
    if (!prefs) return;
    try {
      setSaving(true);
      await updateAiToolPreferences({
        auto_approve_read_only: prefs.auto_approve_read_only,
        require_approval_for_sensitive: prefs.require_approval_for_sensitive,
        disabled_tools: prefs.disabled_tools,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      console.error("Failed to save tool preferences:", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !prefs) {
    return (
      <div className="flex items-center justify-center p-8 text-zinc-400 text-xs">
        <RefreshCw className="w-4 h-4 animate-spin mr-2" />
        Loading AI Tool Governance...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4 text-xs text-zinc-200">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-blue-400" />
          <h4 className="font-semibold text-zinc-100">AI Tool Permissions & Governance</h4>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            Close
          </button>
        )}
      </div>

      {/* Global Policies */}
      <div className="flex flex-col gap-2.5 rounded border border-zinc-800 bg-zinc-950 p-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium text-zinc-200">Auto-Approve Read-Only Tools</div>
            <div className="text-[11px] text-zinc-500">
              Execute discovery and market quote queries without prompting.
            </div>
          </div>
          <input
            type="checkbox"
            checked={prefs.auto_approve_read_only}
            onChange={handleToggleAutoApprove}
            className="rounded border-zinc-700 bg-zinc-900 text-blue-500 focus:ring-0 cursor-pointer"
          />
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-zinc-900">
          <div>
            <div className="font-medium text-zinc-200">Require Approval for Sensitive Scope</div>
            <div className="text-[11px] text-zinc-500">
              Prompt confirmation before accessing private portfolio holdings.
            </div>
          </div>
          <input
            type="checkbox"
            checked={prefs.require_approval_for_sensitive}
            onChange={handleToggleSensitive}
            className="rounded border-zinc-700 bg-zinc-900 text-blue-500 focus:ring-0 cursor-pointer"
          />
        </div>
      </div>

      {/* Per-Tool Controls */}
      <div>
        <div className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500 mb-2">
          Registered Canonical Tools ({tools.length})
        </div>
        <div className="flex flex-col gap-1 max-h-56 overflow-y-auto pr-1">
          {tools.map((t) => {
            const isEnabled = !prefs.disabled_tools.includes(t.tool_id);
            return (
              <div
                key={t.tool_id}
                className="flex items-center justify-between rounded bg-zinc-950/60 border border-zinc-850 px-2.5 py-1.5"
              >
                <div className="min-w-0 pr-2">
                  <div className="font-mono text-zinc-300 text-[11px] truncate">{t.name}</div>
                  <div className="text-[10px] text-zinc-500 truncate">{t.tool_id}</div>
                </div>
                <input
                  type="checkbox"
                  checked={isEnabled}
                  onChange={() => handleToggleTool(t.tool_id)}
                  className="rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 cursor-pointer"
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-1.5 rounded bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
        >
          {saveSuccess ? (
            <>
              <Check className="w-3.5 h-3.5 text-white" />
              <span>Saved</span>
            </>
          ) : (
            <span>{saving ? "Saving..." : "Save Preferences"}</span>
          )}
        </button>
      </div>
    </div>
  );
}

