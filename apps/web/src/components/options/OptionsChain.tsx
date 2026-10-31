"use client";

import React, { useState } from "react";
import {
  AtlasOptionContract,
  LegSide,
  OptionChainResponse,
  OptionChainRow,
  OptionQuote,
} from "@/lib/options/types";
import {
  formatCurrency,
  formatPercent,
  formatNumber,
  formatMoneynessBadge,
  formatQualityFlag,
} from "@/lib/options/formatters";
import { AlertCircle, Info, Plus } from "lucide-react";

interface OptionsChainProps {
  chain: OptionChainResponse | null;
  onSelectContract: (contract: AtlasOptionContract, quote: OptionQuote | null) => void;
  onAddLeg: (contract: AtlasOptionContract, quote: OptionQuote, side: LegSide) => void;
  currency?: string;
  isLoading?: boolean;
}

export function OptionsChain({
  chain,
  onSelectContract,
  onAddLeg,
  currency = "USD",
  isLoading,
}: OptionsChainProps) {
  const [filterMoneyness, setFilterMoneyness] = useState<"ALL" | "ITM" | "ATM" | "OTM">("ALL");

  if (isLoading) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        Loading institutional options chain...
      </div>
    );
  }

  if (!chain || chain.rows.length === 0) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        No active options chain available for this underlying and expiration.
      </div>
    );
  }

  const filteredRows = chain.rows.filter((row) => {
    if (filterMoneyness === "ALL") return true;
    if (filterMoneyness === "ITM") return row.moneyness === "IN_THE_MONEY";
    if (filterMoneyness === "ATM") return row.moneyness === "AT_THE_MONEY";
    if (filterMoneyness === "OTM") return row.moneyness === "OUT_OF_THE_MONEY";
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* Chain Status Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2 bg-zinc-900/60 border-b border-zinc-800 text-xs text-zinc-400 gap-2">
        <div className="flex items-center gap-3">
          <div>
            <span className="text-zinc-500">Underlying: </span>
            <span className="font-mono font-bold text-white">{chain.underlying_symbol}</span>
            <span className="font-mono text-zinc-300 ml-1.5">
              {formatCurrency(chain.underlying_price, currency)}
            </span>
          </div>
          <div className="hidden sm:inline text-zinc-700">|</div>
          <div className="hidden sm:flex items-center gap-1">
            <span className="text-zinc-500">Expiry: </span>
            <span className="font-mono text-white">{chain.expiration_date}</span>
            <span className="text-zinc-500 ml-1">({chain.days_to_expiration} DTE)</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-zinc-500">Filter:</span>
            {(["ALL", "ITM", "ATM", "OTM"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setFilterMoneyness(m)}
                className={`px-2 py-0.5 text-[10px] rounded font-medium transition-colors ${
                  filterMoneyness === m
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                    : "bg-zinc-800/80 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5">
            {chain.is_delayed ? (
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                Delayed {chain.delay_minutes}m
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                Real-Time
              </span>
            )}
            <span className="text-[10px] text-zinc-500 font-mono hidden md:inline">
              Source: {chain.source_id}
            </span>
          </div>
        </div>
      </div>

      {/* Options Chain Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse text-xs font-mono">
          <thead className="sticky top-0 bg-zinc-900 border-b border-zinc-800 z-10 text-[11px] select-none">
            <tr>
              {/* Calls Side */}
              <th className="py-2 px-2 text-center text-emerald-400 font-bold bg-emerald-950/20" colSpan={7}>
                CALLS
              </th>
              {/* Strike */}
              <th className="py-2 px-3 text-center text-zinc-300 font-bold bg-zinc-800/60" colSpan={1}>
                STRIKE
              </th>
              {/* Puts Side */}
              <th className="py-2 px-2 text-center text-rose-400 font-bold bg-rose-950/20" colSpan={7}>
                PUTS
              </th>
            </tr>
            <tr className="text-zinc-500 text-[10px] uppercase tracking-wider border-b border-zinc-800 bg-zinc-900/90">
              {/* Calls */}
              <th className="py-1 px-2 text-right">Delta</th>
              <th className="py-1 px-2 text-right">IV</th>
              <th className="py-1 px-2 text-right">OI</th>
              <th className="py-1 px-2 text-right">Vol</th>
              <th className="py-1 px-2 text-right">Bid</th>
              <th className="py-1 px-2 text-left">Ask</th>
              <th className="py-1 px-1 text-center">Add</th>
              {/* Strike */}
              <th className="py-1 px-3 text-center bg-zinc-850 text-zinc-300">Strike</th>
              {/* Puts */}
              <th className="py-1 px-1 text-center">Add</th>
              <th className="py-1 px-2 text-right">Bid</th>
              <th className="py-1 px-2 text-left">Ask</th>
              <th className="py-1 px-2 text-right">Vol</th>
              <th className="py-1 px-2 text-right">OI</th>
              <th className="py-1 px-2 text-right">IV</th>
              <th className="py-1 px-2 text-right">Delta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-850">
            {filteredRows.map((row) => {
              const isCallItm = row.strike_price < chain.underlying_price;
              const isPutItm = row.strike_price > chain.underlying_price;
              const moneynessBadge = formatMoneynessBadge(row.moneyness);

              const callQ = row.call_quote;
              const putQ = row.put_quote;
              const callC = row.call_contract;
              const putC = row.put_contract;

              return (
                <tr key={row.strike_price} className="hover:bg-zinc-800/40 transition-colors">
                  {/* CALLS: Delta */}
                  <td className={`py-1 px-2 text-right ${isCallItm ? "bg-emerald-950/15" : ""}`}>
                    {callQ?.greeks?.delta !== null && callQ?.greeks?.delta !== undefined
                      ? callQ.greeks.delta.toFixed(3)
                      : "—"}
                  </td>

                  {/* CALLS: IV */}
                  <td className={`py-1 px-2 text-right text-cyan-300 ${isCallItm ? "bg-emerald-950/15" : ""}`}>
                    {callQ?.implied_volatility !== null && callQ?.implied_volatility !== undefined
                      ? formatPercent(callQ.implied_volatility, 1)
                      : "—"}
                  </td>

                  {/* CALLS: OI */}
                  <td className={`py-1 px-2 text-right text-zinc-400 ${isCallItm ? "bg-emerald-950/15" : ""}`}>
                    {callQ ? formatNumber(callQ.open_interest) : "—"}
                  </td>

                  {/* CALLS: Vol */}
                  <td className={`py-1 px-2 text-right text-zinc-300 ${isCallItm ? "bg-emerald-950/15" : ""}`}>
                    {callQ ? formatNumber(callQ.volume) : "—"}
                  </td>

                  {/* CALLS: Bid (Click to sell) */}
                  <td
                    onClick={() => {
                      if (callC && callQ && callQ.bid !== null && callQ.bid !== undefined) {
                        onAddLeg(callC, callQ, "SHORT_CALL");
                      }
                    }}
                    className={`py-1 px-2 text-right cursor-pointer hover:bg-rose-500/20 transition-colors ${
                      isCallItm ? "bg-emerald-950/15" : ""
                    }`}
                    title="Click to Sell Call at Bid"
                  >
                    <span className={callQ?.bid === 0 ? "text-zinc-600 italic" : "text-emerald-400 font-semibold"}>
                      {callQ ? formatCurrency(callQ.bid, currency) : "—"}
                    </span>
                  </td>

                  {/* CALLS: Ask (Click to buy) */}
                  <td
                    onClick={() => {
                      if (callC && callQ && callQ.ask !== null && callQ.ask !== undefined) {
                        onAddLeg(callC, callQ, "LONG_CALL");
                      }
                    }}
                    className={`py-1 px-2 text-left cursor-pointer hover:bg-emerald-500/20 transition-colors ${
                      isCallItm ? "bg-emerald-950/15" : ""
                    }`}
                    title="Click to Buy Call at Ask"
                  >
                    <span className="text-zinc-200 font-semibold">
                      {callQ ? formatCurrency(callQ.ask, currency) : "—"}
                    </span>
                  </td>

                  {/* CALLS: Action */}
                  <td className={`py-1 px-1 text-center ${isCallItm ? "bg-emerald-950/15" : ""}`}>
                    {callC && (
                      <button
                        onClick={() => onSelectContract(callC, callQ || null)}
                        className="p-1 hover:text-cyan-400 text-zinc-500 transition-colors"
                        title="Inspect Call Contract"
                      >
                        <Info className="w-3 h-3" />
                      </button>
                    )}
                  </td>

                  {/* CENTER: STRIKE PRICE */}
                  <td className="py-1 px-3 text-center bg-zinc-900 border-x border-zinc-800 font-bold text-white">
                    <div className="flex items-center justify-center gap-1.5">
                      <span>{row.strike_price.toFixed(2)}</span>
                      <span className={`text-[9px] px-1 py-0.2 rounded font-sans font-medium ${moneynessBadge.className}`}>
                        {moneynessBadge.label}
                      </span>
                    </div>
                  </td>

                  {/* PUTS: Action */}
                  <td className={`py-1 px-1 text-center ${isPutItm ? "bg-rose-950/15" : ""}`}>
                    {putC && (
                      <button
                        onClick={() => onSelectContract(putC, putQ || null)}
                        className="p-1 hover:text-cyan-400 text-zinc-500 transition-colors"
                        title="Inspect Put Contract"
                      >
                        <Info className="w-3 h-3" />
                      </button>
                    )}
                  </td>

                  {/* PUTS: Bid (Click to sell) */}
                  <td
                    onClick={() => {
                      if (putC && putQ && putQ.bid !== null && putQ.bid !== undefined) {
                        onAddLeg(putC, putQ, "SHORT_PUT");
                      }
                    }}
                    className={`py-1 px-2 text-right cursor-pointer hover:bg-rose-500/20 transition-colors ${
                      isPutItm ? "bg-rose-950/15" : ""
                    }`}
                    title="Click to Sell Put at Bid"
                  >
                    <span className={putQ?.bid === 0 ? "text-zinc-600 italic" : "text-emerald-400 font-semibold"}>
                      {putQ ? formatCurrency(putQ.bid, currency) : "—"}
                    </span>
                  </td>

                  {/* PUTS: Ask (Click to buy) */}
                  <td
                    onClick={() => {
                      if (putC && putQ && putQ.ask !== null && putQ.ask !== undefined) {
                        onAddLeg(putC, putQ, "LONG_PUT");
                      }
                    }}
                    className={`py-1 px-2 text-left cursor-pointer hover:bg-emerald-500/20 transition-colors ${
                      isPutItm ? "bg-rose-950/15" : ""
                    }`}
                    title="Click to Buy Put at Ask"
                  >
                    <span className="text-zinc-200 font-semibold">
                      {putQ ? formatCurrency(putQ.ask, currency) : "—"}
                    </span>
                  </td>

                  {/* PUTS: Vol */}
                  <td className={`py-1 px-2 text-right text-zinc-300 ${isPutItm ? "bg-rose-950/15" : ""}`}>
                    {putQ ? formatNumber(putQ.volume) : "—"}
                  </td>

                  {/* PUTS: OI */}
                  <td className={`py-1 px-2 text-right text-zinc-400 ${isPutItm ? "bg-rose-950/15" : ""}`}>
                    {putQ ? formatNumber(putQ.open_interest) : "—"}
                  </td>

                  {/* PUTS: IV */}
                  <td className={`py-1 px-2 text-right text-cyan-300 ${isPutItm ? "bg-rose-950/15" : ""}`}>
                    {putQ?.implied_volatility !== null && putQ?.implied_volatility !== undefined
                      ? formatPercent(putQ.implied_volatility, 1)
                      : "—"}
                  </td>

                  {/* PUTS: Delta */}
                  <td className={`py-1 px-2 text-right ${isPutItm ? "bg-rose-950/15" : ""}`}>
                    {putQ?.greeks?.delta !== null && putQ?.greeks?.delta !== undefined
                      ? putQ.greeks.delta.toFixed(3)
                      : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Chain Footer Summary */}
      <div className="p-2.5 bg-zinc-900 border-t border-zinc-800 text-[11px] text-zinc-400 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-4">
          <div>
            Total Call Volume: <span className="font-mono text-white font-bold">{formatNumber(chain.total_call_volume)}</span>
          </div>
          <div>
            Total Put Volume: <span className="font-mono text-white font-bold">{formatNumber(chain.total_put_volume)}</span>
          </div>
          <div>
            P/C Volume Ratio:{" "}
            <span className="font-mono text-cyan-300 font-bold">
              {chain.put_call_volume_ratio ? chain.put_call_volume_ratio.toFixed(2) : "—"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div>
            Total Call OI: <span className="font-mono text-white font-bold">{formatNumber(chain.total_call_oi)}</span>
          </div>
          <div>
            Total Put OI: <span className="font-mono text-white font-bold">{formatNumber(chain.total_put_oi)}</span>
          </div>
          <div>
            P/C OI Ratio:{" "}
            <span className="font-mono text-cyan-300 font-bold">
              {chain.put_call_oi_ratio ? chain.put_call_oi_ratio.toFixed(2) : "—"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
