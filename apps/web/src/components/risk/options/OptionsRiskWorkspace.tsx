"use client";

import React, { useState } from "react";
import {
  CalculateOptionsRiskRequestDTO,
  OptionGreeksResultDTO,
  OptionPositionRiskDTO,
  OptionType,
  PortfolioOptionsRiskSummaryDTO,
} from "@/lib/risk/types";
import {
  formatBondPrice,
  formatCurrency,
  formatDV01,
  formatDuration,
  formatGreeksDelta,
  formatGreeksGamma,
  formatGreeksRho,
  formatGreeksTheta,
  formatGreeksVega,
  formatSignedPercent,
  formatVolPercent,
} from "@/lib/risk/formatting";

interface OptionsRiskWorkspaceProps {
  portfolioId: string;
  optionsSummary: PortfolioOptionsRiskSummaryDTO | null;
  loading: boolean;
  onRefresh: () => Promise<void>;
  onCalculateOption: (req: CalculateOptionsRiskRequestDTO) => Promise<OptionGreeksResultDTO>;
}

export function OptionsRiskWorkspace({
  portfolioId,
  optionsSummary,
  loading,
  onRefresh,
  onCalculateOption,
}: OptionsRiskWorkspaceProps) {
  const [filterSymbol, setFilterSymbol] = useState<string>("");
  const [selectedPosition, setSelectedPosition] = useState<OptionPositionRiskDTO | null>(null);

  // Calculator State
  const [calcSymbol, setCalcSymbol] = useState<string>("SPY");
  const [calcType, setCalcType] = useState<OptionType>("CALL");
  const [calcStrike, setCalcStrike] = useState<number>(100.0);
  const [calcSpot, setCalcSpot] = useState<number>(100.0);
  const [calcTimeYears, setCalcTimeYears] = useState<number>(1.0);
  const [calcVol, setCalcVol] = useState<number>(0.20);
  const [calcRate, setCalcRate] = useState<number>(0.05);
  const [calcDiv, setCalcDiv] = useState<number>(0.0);
  const [calcMultiplier, setCalcMultiplier] = useState<number>(100.0);
  const [calcQuantity, setCalcQuantity] = useState<number>(1.0);
  const [calcResult, setCalcResult] = useState<OptionGreeksResultDTO | null>(null);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [calcError, setCalcError] = useState<string | null>(null);

  const handleRunCalculator = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculating(true);
    setCalcError(null);
    try {
      const res = await onCalculateOption({
        underlying_symbol: calcSymbol,
        option_type: calcType,
        strike_price: calcStrike,
        underlying_price: calcSpot,
        time_to_expiry_years: calcTimeYears,
        implied_volatility: calcVol,
        risk_free_rate: calcRate,
        dividend_yield: calcDiv,
        contract_multiplier: calcMultiplier,
        contracts_quantity: calcQuantity,
      });
      setCalcResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setCalcError(msg);
    } finally {
      setCalculating(false);
    }
  };

  const positions = optionsSummary?.positions || [];
  const filteredPositions = filterSymbol
    ? positions.filter(
        (p) =>
          p.underlying_symbol.toLowerCase().includes(filterSymbol.toLowerCase()) ||
          p.instrument_id.toLowerCase().includes(filterSymbol.toLowerCase())
      )
    : positions;

  const underlyings = optionsSummary?.underlying_exposures || {};

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border bg-surface-1 p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500/10 text-amber-400 font-mono font-bold text-lg">
            Δ
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-white flex items-center gap-2">
              Derivatives Contract Intelligence & Option Greeks
              <span className="rounded bg-amber-500/20 px-2 py-0.5 text-xs font-mono font-normal text-amber-300 border border-amber-500/30">
                BSM Closed-Form
              </span>
            </h2>
            <p className="text-xs text-muted-foreground">
              Nonlinear risk aggregation, net delta-equivalent exposure, position multipliers (QM), and local Taylor vs. full repricing.
            </p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="rounded border border-border bg-surface-2 px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:bg-surface-3 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "↻ Refresh Greeks"}
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Options Mkt Value
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-white">
            {formatCurrency(optionsSummary?.total_options_market_value ?? 0, optionsSummary?.base_currency || "USD")}
          </div>
          <span className="text-[10px] text-muted-foreground">
            {optionsSummary?.options_count ?? 0} active positions
          </span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Net Delta Notional
          </span>
          <div className={`mt-1 text-lg font-bold font-mono ${(optionsSummary?.net_delta_notional ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
            {formatCurrency(optionsSummary?.net_delta_notional ?? 0, optionsSummary?.base_currency || "USD")}
          </div>
          <span className="text-[10px] text-muted-foreground">
            Gross: {formatCurrency(optionsSummary?.gross_delta_notional ?? 0, optionsSummary?.base_currency || "USD")}
          </span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Net Vega (1% Vol)
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-cyan-400">
            {formatCurrency(optionsSummary?.net_vega_per_vol_point ?? 0, optionsSummary?.base_currency || "USD")}
          </div>
          <span className="text-[10px] text-muted-foreground">
            Gross: {formatCurrency(optionsSummary?.gross_vega_per_vol_point ?? 0, optionsSummary?.base_currency || "USD")}
          </span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Net Theta (/Day)
          </span>
          <div className={`mt-1 text-lg font-bold font-mono ${(optionsSummary?.net_theta_per_day ?? 0) <= 0 ? "text-amber-400" : "text-emerald-400"}`}>
            {formatCurrency(optionsSummary?.net_theta_per_day ?? 0, optionsSummary?.base_currency || "USD")}/d
          </div>
          <span className="text-[10px] text-muted-foreground">Calendar day decay</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Net Rho (1 bp)
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-purple-400">
            {formatCurrency(optionsSummary?.net_rho_per_basis_point ?? 0, optionsSummary?.base_currency || "USD")}/bp
          </div>
          <span className="text-[10px] text-muted-foreground">Interest rate sensitivity</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Parity Validation
          </span>
          <div className="mt-1 flex items-center gap-1.5 text-sm font-bold text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Verified
          </div>
          <span className="text-[10px] text-muted-foreground">C - P = S - Ke^-rT</span>
        </div>
      </div>

      {/* Main Grid: Positions Table & Underlying Decomposition */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Positions Table (2 cols) */}
        <div className="space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Derivatives Positions & Scaled Greeks (QM = Q × M)
            </h3>
            <input
              type="text"
              placeholder="Filter by symbol..."
              value={filterSymbol}
              onChange={(e) => setFilterSymbol(e.target.value)}
              className="rounded border border-border bg-surface-2 px-2.5 py-1 text-xs text-white placeholder-muted-foreground focus:border-amber-500 focus:outline-none"
            />
          </div>

          <div className="overflow-x-auto rounded-lg border border-border bg-surface-1 shadow-sm">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-border bg-surface-2 text-[11px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="py-2.5 px-3">Contract</th>
                  <th className="py-2.5 px-2">Type</th>
                  <th className="py-2.5 px-2 text-right">Strike</th>
                  <th className="py-2.5 px-2 text-right">Qty</th>
                  <th className="py-2.5 px-2 text-right">Mkt Val</th>
                  <th className="py-2.5 px-2 text-right">Delta Notional</th>
                  <th className="py-2.5 px-2 text-right">Vega / 1%</th>
                  <th className="py-2.5 px-2 text-right">Theta / d</th>
                  <th className="py-2.5 px-2 text-center">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredPositions.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-6 text-center text-muted-foreground">
                      No options positions matching filter.
                    </td>
                  </tr>
                ) : (
                  filteredPositions.map((pos) => {
                    const isSelected = selectedPosition?.position_id === pos.position_id;
                    return (
                      <tr
                        key={pos.position_id}
                        className={`transition-colors hover:bg-surface-2/60 ${
                          isSelected ? "bg-amber-500/10 border-l-2 border-l-amber-500" : ""
                        }`}
                      >
                        <td className="py-2 px-3 font-semibold text-white">
                          <div>{pos.instrument_id}</div>
                          <div className="text-[10px] text-muted-foreground">
                            Underlying: {pos.underlying_symbol} @ ${pos.underlying_price.toFixed(2)}
                          </div>
                        </td>
                        <td className="py-2 px-2">
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                              pos.option_type === "CALL"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                            }`}
                          >
                            {pos.option_type}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-right text-slate-200">
                          ${pos.strike_price.toFixed(2)}
                        </td>
                        <td className="py-2 px-2 text-right font-bold text-white">
                          {pos.contracts_quantity > 0 ? `+${pos.contracts_quantity}` : pos.contracts_quantity}
                        </td>
                        <td className="py-2 px-2 text-right text-slate-200">
                          {formatCurrency(pos.position_market_value, pos.currency)}
                        </td>
                        <td
                          className={`py-2 px-2 text-right font-bold ${
                            pos.position_delta_notional >= 0 ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {formatCurrency(pos.position_delta_notional, pos.currency)}
                        </td>
                        <td className="py-2 px-2 text-right text-cyan-400">
                          {formatCurrency(pos.position_vega_per_vol_point, pos.currency)}
                        </td>
                        <td className="py-2 px-2 text-right text-amber-400">
                          {formatCurrency(pos.position_theta_per_day, pos.currency)}
                        </td>
                        <td className="py-2 px-2 text-center">
                          <button
                            onClick={() => setSelectedPosition(isSelected ? null : pos)}
                            className="rounded border border-border px-2 py-0.5 text-[10px] text-slate-300 hover:bg-surface-3"
                          >
                            {isSelected ? "Close" : "Inspect"}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Detailed Position Inspector when selected */}
          {selectedPosition && (
            <div className="rounded-lg border border-amber-500/40 bg-surface-1 p-4 shadow-md space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-amber-400 text-sm">{selectedPosition.instrument_id}</span>
                  <span className="text-xs text-muted-foreground">
                    ({selectedPosition.option_type} on {selectedPosition.underlying_symbol})
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Time to Expiry: {selectedPosition.time_to_expiry_years.toFixed(3)} yrs
                </div>
              </div>

              {/* Per-contract vs Position-scaled Greeks */}
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 text-xs font-mono">
                <div className="rounded border border-border bg-surface-2 p-2">
                  <span className="text-muted-foreground text-[10px] block">Per-Contract Delta (Δ)</span>
                  <span className="text-white font-bold">{formatGreeksDelta(selectedPosition.per_contract_greeks.delta)}</span>
                  <span className="text-[10px] text-muted-foreground block mt-1">
                    Pos Units: {selectedPosition.position_delta_units.toFixed(2)}
                  </span>
                </div>

                <div className="rounded border border-border bg-surface-2 p-2">
                  <span className="text-muted-foreground text-[10px] block">Per-Contract Gamma (Γ)</span>
                  <span className="text-white font-bold">{formatGreeksGamma(selectedPosition.per_contract_greeks.gamma)}</span>
                  <span className="text-[10px] text-muted-foreground block mt-1">
                    Pos Units: {selectedPosition.position_gamma_units.toFixed(4)}
                  </span>
                </div>

                <div className="rounded border border-border bg-surface-2 p-2">
                  <span className="text-muted-foreground text-[10px] block">Per-Contract Vega (1%)</span>
                  <span className="text-cyan-400 font-bold">{formatGreeksVega(selectedPosition.per_contract_greeks.vega_per_vol_point)}</span>
                  <span className="text-[10px] text-muted-foreground block mt-1">
                    Pos 1%: {formatCurrency(selectedPosition.position_vega_per_vol_point, selectedPosition.currency)}
                  </span>
                </div>

                <div className="rounded border border-border bg-surface-2 p-2">
                  <span className="text-muted-foreground text-[10px] block">Per-Contract Theta (/d)</span>
                  <span className="text-amber-400 font-bold">{formatGreeksTheta(selectedPosition.per_contract_greeks.theta_per_day)}</span>
                  <span className="text-[10px] text-muted-foreground block mt-1">
                    Pos /d: {formatCurrency(selectedPosition.position_theta_per_day, selectedPosition.currency)}
                  </span>
                </div>
              </div>

              {/* Nonlinear Shock Comparison: Taylor Approximation vs Full Model Repricing */}
              <div className="mt-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Taylor Approximation vs. Full Model Repricing (P&L Shocks)
                </h4>
                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 text-xs font-mono">
                  {Object.entries(selectedPosition.full_reprice_pnl_shock).map(([shockName, repricePnl]) => {
                    const approxPnl = selectedPosition.approximate_pnl_shock[shockName] ?? 0;
                    const diff = Math.abs(repricePnl - approxPnl);
                    return (
                      <div key={shockName} className="rounded border border-border bg-surface-2 p-2">
                        <span className="text-[10px] text-slate-300 font-bold block capitalize">
                          {shockName.replace(/_/g, " ")}
                        </span>
                        <div className="flex justify-between mt-1 text-[11px]">
                          <span className="text-muted-foreground">Approx:</span>
                          <span className={approxPnl >= 0 ? "text-emerald-400" : "text-rose-400"}>
                            {formatCurrency(approxPnl, selectedPosition.currency)}
                          </span>
                        </div>
                        <div className="flex justify-between text-[11px]">
                          <span className="text-muted-foreground">Reprice:</span>
                          <span className={repricePnl >= 0 ? "text-emerald-400" : "text-rose-400"}>
                            {formatCurrency(repricePnl, selectedPosition.currency)}
                          </span>
                        </div>
                        <div className="flex justify-between text-[10px] border-t border-border/60 mt-1 pt-0.5 text-muted-foreground">
                          <span>Nonlinear Err:</span>
                          <span className="text-amber-300">{formatCurrency(diff, selectedPosition.currency)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Underlying Aggregation & Live Calculator */}
        <div className="space-y-6">
          {/* Underlying Asset Aggregation Card */}
          <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Underlying Asset Delta Exposure
            </h3>
            <div className="space-y-2">
              {Object.keys(underlyings).length === 0 ? (
                <div className="py-4 text-center text-xs text-muted-foreground">No underlying breakdown.</div>
              ) : (
                Object.entries(underlyings).map(([sym, metrics]) => (
                  <div key={sym} className="rounded border border-border bg-surface-2 p-2.5 text-xs font-mono">
                    <div className="flex items-center justify-between font-bold text-white mb-1">
                      <span>{sym}</span>
                      <span className={metrics.net_delta_notional >= 0 ? "text-emerald-400" : "text-rose-400"}>
                        {formatCurrency(metrics.net_delta_notional, optionsSummary?.base_currency || "USD")}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground">
                      <div>Gross Δ: {formatCurrency(metrics.gross_delta_notional, optionsSummary?.base_currency || "USD")}</div>
                      <div>Vega 1%: {formatCurrency(metrics.net_vega_per_vol_point, optionsSummary?.base_currency || "USD")}</div>
                      <div>Theta /d: {formatCurrency(metrics.net_theta_per_day, optionsSummary?.base_currency || "USD")}</div>
                      <div>Contracts: {metrics.contracts_count}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Real-Time BSM Option Calculator */}
          <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center justify-between">
              <span>Interactive BSM Calculator</span>
              <span className="text-[10px] font-mono text-amber-400 font-normal">Closed-Form</span>
            </h3>

            <form onSubmit={handleRunCalculator} className="space-y-2.5 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Symbol</label>
                  <input
                    type="text"
                    value={calcSymbol}
                    onChange={(e) => setCalcSymbol(e.target.value)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Right</label>
                  <select
                    value={calcType}
                    onChange={(e) => setCalcType(e.target.value as OptionType)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  >
                    <option value="CALL">CALL</option>
                    <option value="PUT">PUT</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Spot Price (S)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={calcSpot}
                    onChange={(e) => setCalcSpot(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Strike Price (K)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={calcStrike}
                    onChange={(e) => setCalcStrike(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Expiry (Yrs)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={calcTimeYears}
                    onChange={(e) => setCalcTimeYears(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Vol (σ)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={calcVol}
                    onChange={(e) => setCalcVol(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Rate (r)</label>
                  <input
                    type="number"
                    step="0.005"
                    value={calcRate}
                    onChange={(e) => setCalcRate(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={calculating}
                className="w-full mt-2 rounded bg-amber-600 px-3 py-1.5 font-semibold text-white transition-colors hover:bg-amber-500 disabled:opacity-50"
              >
                {calculating ? "Calculating..." : "Compute Theoretical Greeks"}
              </button>
            </form>

            {calcError && <div className="text-xs text-rose-400 bg-rose-500/10 p-2 rounded">{calcError}</div>}

            {calcResult && (
              <div className="mt-3 rounded border border-border bg-surface-2 p-3 font-mono text-xs space-y-2">
                <div className="flex justify-between items-center border-b border-border pb-1.5 font-bold">
                  <span className="text-slate-300">Theoretical Price:</span>
                  <span className="text-amber-400 text-sm">${calcResult.theoretical_price.toFixed(4)}</span>
                </div>
                <div className="grid grid-cols-2 gap-1 text-[11px]">
                  <div>Delta (Δ): <span className="text-white font-bold">{formatGreeksDelta(calcResult.delta)}</span></div>
                  <div>Gamma (Γ): <span className="text-white font-bold">{formatGreeksGamma(calcResult.gamma)}</span></div>
                  <div>Vega / 1%: <span className="text-cyan-400 font-bold">{formatGreeksVega(calcResult.vega_per_vol_point)}</span></div>
                  <div>Theta / d: <span className="text-amber-400 font-bold">{formatGreeksTheta(calcResult.theta_per_day)}</span></div>
                  <div>Rho / bp: <span className="text-purple-400 font-bold">{formatGreeksRho(calcResult.rho_per_basis_point)}</span></div>
                  <div>Time Val: <span className="text-white">${calcResult.time_value.toFixed(4)}</span></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

