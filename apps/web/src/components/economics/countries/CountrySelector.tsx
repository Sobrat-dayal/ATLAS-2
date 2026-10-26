"use client";

import React, { useState } from "react";
import { Search, ChevronDown, Check, Globe } from "lucide-react";
import { CountryEconomicProfileDTO } from "@/lib/economics/countries";

interface CountrySelectorProps {
  countries: CountryEconomicProfileDTO[];
  selectedCountryId: string;
  onSelectCountry: (countryId: string) => void;
}

export function CountrySelector({
  countries,
  selectedCountryId,
  onSelectCountry,
}: CountrySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");

  const selectedProfile = countries.find(
    (c) =>
      c.geography_id.toLowerCase() === selectedCountryId.toLowerCase() ||
      c.iso_code.toLowerCase() === selectedCountryId.toLowerCase()
  );

  const filteredCountries = countries.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.iso_code.toLowerCase().includes(search.toLowerCase()) ||
      c.currency_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 bg-atlas-surface border border-atlas-border-subtle hover:border-atlas-border-strong rounded text-xs font-medium text-atlas-text-primary transition-colors shadow-xs"
        aria-expanded={isOpen}
      >
        <div className="w-5 h-5 rounded bg-atlas-background flex items-center justify-center font-mono font-bold text-[10px] text-atlas-accent border border-atlas-border-subtle">
          {selectedProfile?.iso_code || "US"}
        </div>
        <div className="text-left">
          <div className="text-xs font-bold leading-none">
            {selectedProfile?.name || "United States"}
          </div>
          <div className="text-[10px] text-atlas-text-muted leading-tight mt-0.5">
            {selectedProfile?.currency_code} · {selectedProfile?.central_bank_name.split("(")[0].trim()}
          </div>
        </div>
        <ChevronDown className="w-3.5 h-3.5 text-atlas-text-muted ml-1" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-20"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute left-0 mt-1 w-72 rounded-md bg-atlas-surface border border-atlas-border-strong shadow-lg z-30 py-1 text-xs">
            {/* Search Input */}
            <div className="p-2 border-b border-atlas-border-subtle">
              <div className="relative flex items-center">
                <Search className="w-3.5 h-3.5 absolute left-2 text-atlas-text-muted" />
                <input
                  type="text"
                  placeholder="Filter country or currency..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-atlas-background border border-atlas-border-subtle rounded pl-7 pr-2 py-1 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-hidden focus:border-atlas-accent"
                  autoFocus
                />
              </div>
            </div>

            {/* Country list */}
            <div className="max-h-60 overflow-y-auto py-1">
              {filteredCountries.length === 0 ? (
                <div className="px-3 py-2 text-atlas-text-muted text-center text-xs">
                  No matching countries found
                </div>
              ) : (
                filteredCountries.map((country) => {
                  const isSelected =
                    selectedProfile?.geography_id === country.geography_id;
                  return (
                    <button
                      key={country.geography_id}
                      onClick={() => {
                        onSelectCountry(country.iso_code);
                        setIsOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-atlas-surface-elevated transition-colors ${
                        isSelected ? "bg-atlas-accent/10 text-atlas-accent font-semibold" : "text-atlas-text-primary"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="font-mono font-bold text-[10px] w-6 px-1 py-0.5 rounded bg-atlas-background text-center border border-atlas-border-subtle">
                          {country.iso_code}
                        </span>
                        <div>
                          <div className="text-xs">{country.name}</div>
                          <div className="text-[10px] text-atlas-text-muted">
                            {country.currency_code} · {country.statistical_agency.split("(")[0].trim()}
                          </div>
                        </div>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-atlas-accent" />}
                    </button>
                  );
                })
              )}
            </div>

            <div className="px-3 py-1.5 bg-atlas-background/50 border-t border-atlas-border-subtle text-[10px] text-atlas-text-muted flex items-center gap-1">
              <Globe className="w-3 h-3 text-atlas-accent" />
              <span>G6 Core Sovereign Jurisdictions (SNA 2008 / ESA 2010)</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
