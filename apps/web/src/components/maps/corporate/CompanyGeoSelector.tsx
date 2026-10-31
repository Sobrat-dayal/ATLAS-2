"use client";

import React, { useEffect, useState } from "react";
import { Search, Building2, Check, Loader2 } from "lucide-react";
import { searchMappedCompanies } from "@/lib/maps/corporate/api";
import { MappedCompanySearchResult } from "@/lib/maps/corporate/types";

interface CompanyGeoSelectorProps {
  selectedCompanyId: string | null;
  onSelectCompany: (company: MappedCompanySearchResult) => void;
  className?: string;
}

export function CompanyGeoSelector({
  selectedCompanyId,
  onSelectCompany,
  className = "",
}: CompanyGeoSelectorProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MappedCompanySearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    let active = true;
    const fetchCompanies = async () => {
      setLoading(true);
      try {
        const data = await searchMappedCompanies(query);
        if (active) setResults(data);
      } catch (e) {
        if (active) setResults([]);
      } finally {
        if (active) setLoading(false);
      }
    };

    const timer = setTimeout(fetchCompanies, 200);
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [query]);

  const selectedCompany = results.find((r) => r.entity_id === selectedCompanyId || r.company_id === selectedCompanyId);

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-xs focus-within:border-sky-500/50 transition-colors">
        <Building2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={selectedCompany ? `${selectedCompany.canonical_name} (${selectedCompany.tickers?.[0] || selectedCompany.entity_id})` : "Search company by ticker, name, or LEI..."}
          className="bg-transparent text-zinc-200 placeholder-zinc-500 focus:outline-none w-full text-xs"
        />
        {loading && <Loader2 className="w-3 h-3 text-zinc-400 animate-spin shrink-0" />}
      </div>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 right-0 mt-1 max-h-60 overflow-y-auto bg-zinc-900 border border-zinc-800 rounded shadow-xl z-50 divide-y divide-zinc-800/50 text-xs">
            {results.length === 0 ? (
              <div className="p-3 text-center text-zinc-500">
                {loading ? "Searching mapped companies..." : "No mapped companies found."}
              </div>
            ) : (
              results.map((comp) => {
                const isSelected = comp.entity_id === selectedCompanyId || comp.company_id === selectedCompanyId;
                return (
                  <button
                    key={comp.entity_id}
                    type="button"
                    onClick={() => {
                      onSelectCompany(comp);
                      setIsOpen(false);
                      setQuery("");
                    }}
                    className={`w-full text-left p-2.5 flex items-center justify-between hover:bg-zinc-800/60 transition-colors ${
                      isSelected ? "bg-sky-950/30 text-sky-300" : "text-zinc-200"
                    }`}
                  >
                    <div>
                      <div className="font-semibold flex items-center gap-1.5">
                        <span>{comp.canonical_name}</span>
                        {comp.tickers && comp.tickers.length > 0 && (
                          <span className="font-mono text-[10px] px-1 py-0.2 bg-zinc-800 rounded text-sky-400">
                            {comp.tickers.join(", ")}
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-zinc-500 font-mono flex items-center gap-2 mt-0.5">
                        {comp.primary_country_code && <span>Country: {comp.primary_country_code}</span>}
                        {comp.lei && <span>LEI: {comp.lei}</span>}
                      </div>
                    </div>
                    {isSelected && <Check className="w-3.5 h-3.5 text-sky-400 shrink-0" />}
                  </button>
                );
              })
            )}
          </div>
        </>
      )}
    </div>
  );
}

