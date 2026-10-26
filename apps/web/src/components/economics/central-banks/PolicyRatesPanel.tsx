"use client";

import React from "react";
import { Sliders, CheckCircle2 } from "lucide-react";
import { PolicyInstrumentDTO } from "@/lib/economics/central-banks";

interface PolicyRatesPanelProps {
  instruments: PolicyInstrumentDTO[];
}

export function PolicyRatesPanel({ instruments }: PolicyRatesPanelProps) {
  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-atlas-accent" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Administered Monetary Policy Instruments & Key Interest Rates
          </h3>
        </div>
        <span className="text-xs font-mono text-atlas-text-muted">
          {instruments.length} Operational Instruments
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 font-mono text-[11px] text-atlas-text-muted uppercase">
              <th className="py-2.5 px-3">Instrument Code & Name</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Representation</th>
              <th className="py-2.5 px-3 text-right">Current Target / Level</th>
              <th className="py-2.5 px-3">Effective Date</th>
              <th className="py-2.5 px-3">Operational Role</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
            {instruments.map((inst) => {
              const displayRate =
                inst.representation === "TARGET_RANGE"
                  ? `${inst.current_lower_bound?.toFixed(2)}% - ${inst.current_upper_bound?.toFixed(2)}%`
                  : inst.current_rate != null
                  ? `${inst.current_rate.toFixed(2)}%`
                  : "N/A";

              return (
                <tr key={inst.instrument_id} className="hover:bg-atlas-surface-elevated/40 transition-colors">
                  <td className="py-3 px-3">
                    <span className="font-bold text-atlas-text-primary block font-sans text-xs">
                      {inst.name}
                    </span>
                    <span className="text-[10px] text-atlas-text-muted font-mono">
                      {inst.code}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded text-[10px] bg-atlas-background text-atlas-text-primary border border-atlas-border-subtle">
                      {inst.category}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-[11px] text-atlas-text-muted">
                    {inst.representation}
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-atlas-accent text-sm">
                    {displayRate}
                  </td>
                  <td className="py-3 px-3 text-atlas-text-muted text-[11px]">
                    {inst.effective_date}
                  </td>
                  <td className="py-3 px-3 text-atlas-text-muted font-sans text-xs max-w-xs leading-relaxed">
                    {inst.operational_description}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="pt-3 border-t border-atlas-border-subtle flex items-center gap-2 text-[11px] text-atlas-text-muted">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>
          Policy rates are verified official operational targets and administered facility rates, distinct from effective market interest rates.
        </span>
      </div>
    </div>
  );
}
