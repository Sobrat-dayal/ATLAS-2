"use client";

import React from "react";
import { Landmark } from "lucide-react";
import { CentralBankInstitutionDTO } from "@/lib/economics/central-banks";

interface CentralBankSelectorProps {
  institutions: CentralBankInstitutionDTO[];
  selectedBankId: string;
  onSelectBank: (bankId: string) => void;
}

export function CentralBankSelector({
  institutions,
  selectedBankId,
  onSelectBank,
}: CentralBankSelectorProps) {
  // Flag / Geography badges
  const getGeoBadge = (geoId: string) => {
    switch (geoId.toUpperCase()) {
      case "US":
        return { flag: "🇺🇸", label: "US" };
      case "EA":
        return { flag: "🇪🇺", label: "Euro Area" };
      case "GB":
        return { flag: "🇬🇧", label: "UK" };
      case "JP":
        return { flag: "🇯🇵", label: "Japan" };
      case "IN":
        return { flag: "🇮🇳", label: "India" };
      case "CN":
        return { flag: "🇨🇳", label: "China" };
      default:
        return { flag: "🌐", label: geoId };
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-atlas-surface border border-atlas-border-subtle rounded-lg p-3">
      <div className="flex items-center gap-2">
        <Landmark className="w-4 h-4 text-atlas-accent shrink-0" />
        <span className="text-xs font-semibold uppercase tracking-wider text-atlas-text-muted">
          Monetary Authority:
        </span>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {institutions.map((bank) => {
          const isSelected = bank.central_bank_id === selectedBankId;
          const { flag, label } = getGeoBadge(bank.primary_geography_id);
          return (
            <button
              key={bank.central_bank_id}
              onClick={() => onSelectBank(bank.central_bank_id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                isSelected
                  ? "bg-atlas-accent text-white shadow-xs font-semibold"
                  : "bg-atlas-background hover:bg-atlas-surface-elevated text-atlas-text-primary border border-atlas-border-subtle"
              }`}
            >
              <span>{flag}</span>
              <span>{bank.acronym}</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                  isSelected ? "bg-white/20 text-white" : "bg-atlas-surface text-atlas-text-muted"
                }`}
              >
                {bank.currency_code}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
