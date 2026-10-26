"use client";

import React, { useState } from "react";
import {
  Building2,
  ChevronDown,
  Globe,
  Landmark,
  X,
} from "lucide-react";
import { CountryOption, ExchangeOption, SectorOption } from "@/lib/screeners/types";

interface ScreenerToolbarProps {
  exchanges: ExchangeOption[];
  geographies: CountryOption[];
  industries: SectorOption[];
  selectedExchanges: string[];
  selectedCountries: string[];
  selectedSectors: string[];
  onToggleExchange: (mic: string) => void;
  onToggleCountry: (code: string) => void;
  onToggleSector: (name: string) => void;
}

export function ScreenerToolbar({
  exchanges,
  geographies,
  industries,
  selectedExchanges,
  selectedCountries,
  selectedSectors,
  onToggleExchange,
  onToggleCountry,
  onToggleSector,
}: ScreenerToolbarProps) {
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const toggleDropdown = (id: string) => {
    setOpenDropdown((prev) => (prev === id ? null : id));
  };

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border/50 bg-muted/20 px-6 py-2.5">
      <span className="text-xs font-medium text-muted-foreground mr-1">
        Universes & Scopes:
      </span>

      {/* 1. Exchange Filter Chip */}
      <div className="relative">
        <button
          type="button"
          onClick={() => toggleDropdown("exchanges")}
          className={`flex h-7 items-center gap-1.5 rounded-full border px-3 text-xs font-medium transition-colors ${
            selectedExchanges.length > 0
              ? "border-primary/50 bg-primary/10 text-primary"
              : "border-border/80 bg-background text-muted-foreground hover:bg-muted/60 hover:text-foreground"
          }`}
        >
          <Landmark className="h-3 w-3" />
          <span>Exchanges</span>
          {selectedExchanges.length > 0 && (
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground font-mono">
              {selectedExchanges.length}
            </span>
          )}
          <ChevronDown className="h-3 w-3 opacity-60" />
        </button>

        {openDropdown === "exchanges" && (
          <div className="absolute left-0 top-full z-30 mt-1 max-h-64 w-60 overflow-y-auto rounded-md border border-border bg-popover p-2 shadow-lg">
            <div className="mb-1.5 px-2 py-1 text-[11px] font-semibold text-muted-foreground">
              Filter by Exchange Venue
            </div>
            <div className="space-y-1">
              {exchanges.map((ex) => {
                const isSelected = selectedExchanges.includes(ex.mic);
                return (
                  <button
                    key={ex.mic}
                    type="button"
                    onClick={() => onToggleExchange(ex.mic)}
                    className={`flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-xs transition-colors ${
                      isSelected
                        ? "bg-primary/15 text-primary font-medium"
                        : "hover:bg-muted text-foreground"
                    }`}
                  >
                    <span className="truncate">{ex.name} ({ex.mic})</span>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {ex.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 2. Country / Geography Filter Chip */}
      <div className="relative">
        <button
          type="button"
          onClick={() => toggleDropdown("geographies")}
          className={`flex h-7 items-center gap-1.5 rounded-full border px-3 text-xs font-medium transition-colors ${
            selectedCountries.length > 0
              ? "border-primary/50 bg-primary/10 text-primary"
              : "border-border/80 bg-background text-muted-foreground hover:bg-muted/60 hover:text-foreground"
          }`}
        >
          <Globe className="h-3 w-3" />
          <span>Market Country</span>
          {selectedCountries.length > 0 && (
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground font-mono">
              {selectedCountries.length}
            </span>
          )}
          <ChevronDown className="h-3 w-3 opacity-60" />
        </button>

        {openDropdown === "geographies" && (
          <div className="absolute left-0 top-full z-30 mt-1 max-h-64 w-60 overflow-y-auto rounded-md border border-border bg-popover p-2 shadow-lg">
            <div className="mb-1.5 px-2 py-1 text-[11px] font-semibold text-muted-foreground">
              Filter by Market Country
            </div>
            <div className="space-y-1">
              {geographies.map((c) => {
                const isSelected = selectedCountries.includes(c.code);
                return (
                  <button
                    key={c.code}
                    type="button"
                    onClick={() => onToggleCountry(c.code)}
                    className={`flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-xs transition-colors ${
                      isSelected
                        ? "bg-primary/15 text-primary font-medium"
                        : "hover:bg-muted text-foreground"
                    }`}
                  >
                    <span className="truncate">{c.name} ({c.code})</span>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {c.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* 3. Sector / Industry Filter Chip */}
      <div className="relative">
        <button
          type="button"
          onClick={() => toggleDropdown("sectors")}
          className={`flex h-7 items-center gap-1.5 rounded-full border px-3 text-xs font-medium transition-colors ${
            selectedSectors.length > 0
              ? "border-primary/50 bg-primary/10 text-primary"
              : "border-border/80 bg-background text-muted-foreground hover:bg-muted/60 hover:text-foreground"
          }`}
        >
          <Building2 className="h-3 w-3" />
          <span>Sector</span>
          {selectedSectors.length > 0 && (
            <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground font-mono">
              {selectedSectors.length}
            </span>
          )}
          <ChevronDown className="h-3 w-3 opacity-60" />
        </button>

        {openDropdown === "sectors" && (
          <div className="absolute left-0 top-full z-30 mt-1 max-h-64 w-64 overflow-y-auto rounded-md border border-border bg-popover p-2 shadow-lg">
            <div className="mb-1.5 px-2 py-1 text-[11px] font-semibold text-muted-foreground">
              Filter by Classification Sector
            </div>
            <div className="space-y-1">
              {industries.map((sec) => {
                const isSelected = selectedSectors.includes(sec.name);
                return (
                  <button
                    key={sec.name}
                    type="button"
                    onClick={() => onToggleSector(sec.name)}
                    className={`flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-xs transition-colors ${
                      isSelected
                        ? "bg-primary/15 text-primary font-medium"
                        : "hover:bg-muted text-foreground"
                    }`}
                  >
                    <span className="truncate">{sec.name}</span>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      {sec.count}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Click outside backdrop */}
      {openDropdown && (
        <div
          className="fixed inset-0 z-20"
          onClick={() => setOpenDropdown(null)}
        />
      )}
    </div>
  );
}
