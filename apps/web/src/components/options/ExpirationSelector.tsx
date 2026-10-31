"use client";

import React from "react";
import { Calendar } from "lucide-react";
import { formatDte } from "@/lib/options/formatters";

interface ExpirationSelectorProps {
  expirations: string[];
  selectedExpiration: string;
  onSelect: (expiration: string) => void;
  daysToExpirationMap?: Record<string, number>;
}

export function ExpirationSelector({
  expirations,
  selectedExpiration,
  onSelect,
  daysToExpirationMap = {},
}: ExpirationSelectorProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto py-2 px-4 bg-zinc-950 border-b border-zinc-850 scrollbar-thin">
      <div className="flex items-center gap-1.5 text-zinc-500 text-xs font-medium mr-2 shrink-0">
        <Calendar className="w-3.5 h-3.5" />
        <span>Expirations:</span>
      </div>

      <div className="flex items-center gap-1.5">
        {expirations.map((exp) => {
          const isSelected = selectedExpiration === exp;
          const dte = daysToExpirationMap[exp];

          return (
            <button
              key={exp}
              onClick={() => onSelect(exp)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono transition-all shrink-0 ${
                isSelected
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                  : "bg-zinc-900 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-800"
              }`}
            >
              <span className="font-semibold">{exp}</span>
              {dte !== undefined && (
                <span
                  className={`text-[10px] px-1 py-0.2 rounded font-sans ${
                    isSelected ? "bg-cyan-500/30 text-cyan-200" : "bg-zinc-800 text-zinc-500"
                  }`}
                >
                  {formatDte(dte)}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
