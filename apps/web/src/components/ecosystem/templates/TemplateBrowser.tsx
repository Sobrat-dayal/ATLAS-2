"use client";

import React, { useState } from "react";
import type { EcosystemTemplate } from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

interface TemplateBrowserProps {
  initialTemplates?: EcosystemTemplate[];
}

export const TemplateBrowser: React.FC<TemplateBrowserProps> = ({
  initialTemplates = [],
}) => {
  const [templates] = useState<EcosystemTemplate[]>(initialTemplates);
  const [selectedKind, setSelectedKind] = useState<"ALL" | "AGENT" | "TEAM" | "WORKFLOW">("ALL");
  const [instantiatingId, setInstantiatingId] = useState<string | null>(null);
  const [createdNotice, setCreatedNotice] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const filtered = templates.filter((t) => {
    if (selectedKind === "ALL") return true;
    return t.kind === selectedKind;
  });

  const handleInstantiate = async (template: EcosystemTemplate) => {
    setInstantiatingId(template.template_id);
    setErrorMsg(null);
    setCreatedNotice(null);
    try {
      const res = await ecosystemApi.instantiateTemplate(template.template_id);
      setCreatedNotice(
        `Draft instance of '${res.name}' created successfully (Agent ID: ${res.agent_id}). Zero auto-execution enforced.`
      );
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to instantiate template.");
    } finally {
      setInstantiatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-3 gap-2">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
            Institutional Templates Platform
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Preconfigured Agent, Team, and Workflow starters that instantiate into safe, governed DRAFT states.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex rounded border border-zinc-800 bg-[#111] p-0.5 text-xs">
          {(["ALL", "AGENT", "TEAM", "WORKFLOW"] as const).map((kind) => (
            <button
              key={kind}
              onClick={() => setSelectedKind(kind)}
              className={`rounded px-3 py-1 font-medium transition ${
                selectedKind === kind
                  ? "bg-zinc-800 text-zinc-100 shadow"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {kind === "ALL" ? "All Templates" : `${kind}s`}
            </button>
          ))}
        </div>
      </div>

      {createdNotice && (
        <div className="rounded border border-emerald-800 bg-emerald-950/60 p-2.5 text-xs text-emerald-300">
          {createdNotice}
        </div>
      )}

      {errorMsg && (
        <div className="rounded border border-rose-900 bg-rose-950/60 p-2.5 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Grid of Templates */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((t) => (
          <div
            key={t.template_id}
            className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 flex flex-col justify-between space-y-3"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="rounded bg-zinc-800 border border-zinc-700 px-1.5 py-0.5 text-[10px] text-zinc-300 font-semibold font-mono">
                  {t.kind}
                </span>
                <span className="text-[10px] text-zinc-500 font-mono">v{t.version}</span>
              </div>
              <h3 className="text-xs font-bold text-zinc-100">{t.name}</h3>
              <p className="text-[11px] text-zinc-400 line-clamp-3">{t.description}</p>
            </div>

            <div className="space-y-2 pt-2 border-t border-zinc-800/60 text-[10px] font-mono">
              <div className="text-zinc-400">Category: {t.category}</div>
              <div className="text-zinc-500 truncate">
                Required Tools: {t.required_tools.join(", ") || "None"}
              </div>
              <button
                onClick={() => handleInstantiate(t)}
                disabled={instantiatingId === t.template_id}
                className="w-full mt-2 rounded bg-zinc-800 border border-zinc-700 px-3 py-1.5 text-xs font-semibold text-zinc-200 hover:bg-zinc-700 transition disabled:opacity-50"
              >
                {instantiatingId === t.template_id ? "Instantiating..." : "+ Instantiate Draft"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
