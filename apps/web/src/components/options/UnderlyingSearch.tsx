"use client";

import React, { useState } from "react";
import { Search, Globe, AlertTriangle } from "lucide-react";

export interface UnderlyingItem {
  symbol: string;
  name: string;
  market_id: string;
  spot_price: number;
  quote_time: string;
  currency: string;
  has_adjusted_contracts: boolean;
}

interface UnderlyingSearchProps {
  underlyings: UnderlyingItem[];
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
  isLoading?: boolean;
}

export function UnderlyingSearch({
  underlyings,
  selectedSymbol,
  onSelect,
  isLoading,
}: UnderlyingSearchProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const filtered = underlyings.filter(
    (u) =>
      u.symbol.toLowerCase().includes(query.toLowerCase()) ||
      u.name.toLowerCase().includes(query.toLowerCase())
  );

  const selectedItem = underlyings.find((u) => u.symbol === selectedSymbol);

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <div className="relative w-48 sm:w-64">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder={selectedItem ? `${selectedItem.symbol} — ${selectedItem.name}` : "Search underlying..."}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2.5" />
        </div>

        {/* Quick Tickers */}
        <div className="hidden md:flex items-center gap-1.5">
          {underlyings.slice(0, 4).map((u) => (
            <button
              key={u.symbol}
              onClick={() => {
                onSelect(u.symbol);
                setQuery("");
                setIsOpen(false);
              }}
              className={`px-2.5 py-1 text-xs font-mono font-medium rounded transition-colors ${
                selectedSymbol === u.symbol
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "bg-zinc-900/80 text-zinc-400 hover:text-zinc-200 border border-zinc-800/80"
              }`}
            >
              {u.symbol}
            </button>
          ))}
        </div>
      </div>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-20"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 mt-1 w-80 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl z-30 overflow-hidden divide-y divide-zinc-800">
            {filtered.length === 0 ? (
              <div className="p-3 text-xs text-zinc-500 text-center">No underlying instruments found</div>
            ) : (
              filtered.map((u) => {
                const prefix = u.currency === "INR" ? "₹" : u.currency === "EUR" ? "€" : "$";
                return (
                  <button
                    key={u.symbol}
                    onClick={() => {
                      onSelect(u.symbol);
                      setIsOpen(false);
                      setQuery("");
                    }}
                    className="w-full text-left p-2.5 hover:bg-zinc-800/70 transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-xs text-white">{u.symbol}</span>
                        <span className="text-[10px] text-zinc-400 truncate max-w-[120px]">{u.name}</span>
                      </div>
                      <div className="flex items-center gap-1.5 mt-1 text-[10px] text-zinc-500">
                        <Globe className="w-3 h-3" />
                        <span>{u.market_id}</span>
                        {u.has_adjusted_contracts && (
                          <span className="text-amber-400 flex items-center gap-0.5 ml-1">
                            <AlertTriangle className="w-2.5 h-2.5" />
                            Adjusted
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono font-medium text-xs text-zinc-200">
                        {prefix}{u.spot_price.toFixed(2)}
                      </div>
                      <div className="text-[10px] text-zinc-500">{u.currency}</div>
                    </div>
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
