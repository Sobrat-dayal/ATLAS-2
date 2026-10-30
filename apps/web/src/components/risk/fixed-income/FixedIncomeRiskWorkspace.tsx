"use client";

import React, { useState } from "react";
import {
  BondCashFlowScheduleDTO,
  BondPositionRiskDTO,
  BondSensitivitiesResultDTO,
  CalculateFixedIncomeRiskRequestDTO,
  CouponFrequency,
  DayCountConvention,
  InterestRateCurveDefinitionDTO,
  PortfolioFixedIncomeRiskSummaryDTO,
} from "@/lib/risk/types";
import {
  formatBondPrice,
  formatCurrency,
  formatDV01,
  formatDuration,
  formatConvexity,
  formatYield,
} from "@/lib/risk/formatting";

interface FixedIncomeRiskWorkspaceProps {
  portfolioId: string;
  fixedIncomeSummary: PortfolioFixedIncomeRiskSummaryDTO | null;
  curveDefinition: InterestRateCurveDefinitionDTO | null;
  selectedBondCashFlows: BondCashFlowScheduleDTO | null;
  loading: boolean;
  onRefresh: () => Promise<void>;
  onCalculateBond: (req: CalculateFixedIncomeRiskRequestDTO) => Promise<BondSensitivitiesResultDTO>;
  onFetchCashFlows: (instrumentId: string) => Promise<void>;
}

export function FixedIncomeRiskWorkspace({
  portfolioId,
  fixedIncomeSummary,
  curveDefinition,
  selectedBondCashFlows,
  loading,
  onRefresh,
  onCalculateBond,
  onFetchCashFlows,
}: FixedIncomeRiskWorkspaceProps) {
  const [activeBondForSchedule, setActiveBondForSchedule] = useState<string | null>(null);

  // Standalone Calculator State
  const [calcFace, setCalcFace] = useState<number>(100.0);
  const [calcCoupon, setCalcCoupon] = useState<number>(0.05);
  const [calcFreq, setCalcFreq] = useState<CouponFrequency>("SEMI_ANNUAL");
  const [calcDayCount, setCalcDayCount] = useState<DayCountConvention>("ACT_ACT");
  const [calcMaturityYears, setCalcMaturityYears] = useState<number>(5.0);
  const [calcPrice, setCalcPrice] = useState<number>(100.0);
  const [calcResult, setCalcResult] = useState<BondSensitivitiesResultDTO | null>(null);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [calcError, setCalcError] = useState<string | null>(null);

  const handleRunBondCalculator = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculating(true);
    setCalcError(null);
    try {
      const res = await onCalculateBond({
        face_value: calcFace,
        coupon_rate: calcCoupon,
        coupon_frequency: calcFreq,
        day_count_convention: calcDayCount,
        maturity_years: calcMaturityYears,
        market_price: calcPrice,
      });
      setCalcResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setCalcError(msg);
    } finally {
      setCalculating(false);
    }
  };

  const handleInspectCashFlows = async (instrumentId: string) => {
    setActiveBondForSchedule(instrumentId);
    await onFetchCashFlows(instrumentId);
  };

  const positions = fixedIncomeSummary?.positions || [];
  const krProfile = fixedIncomeSummary?.key_rate_dv01_profile || {};
  const totalDv01 = fixedIncomeSummary?.portfolio_total_dv01 || 1.0;

  return (
    <div className="space-y-6 text-slate-100">
      {/* Top Header Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border bg-surface-1 p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 font-mono font-bold text-lg">
            DV
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-white flex items-center gap-2">
              Fixed-Income Risk Foundations & Yield-Curve Analytics
              <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-xs font-mono font-normal text-emerald-300 border border-emerald-500/30">
                DCF Cash-Flow Engine
              </span>
            </h2>
            <p className="text-xs text-muted-foreground">
              Macaulay/Modified Duration, Convexity, DV01/PV01, Key-Rate Sensitivities (KRD), and clean/dirty price reconciliation.
            </p>
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="rounded border border-border bg-surface-2 px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:bg-surface-3 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "↻ Refresh Fixed Income"}
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Debt Mkt Value
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-white">
            {formatCurrency(fixedIncomeSummary?.total_fixed_income_market_value ?? 0, fixedIncomeSummary?.base_currency || "USD")}
          </div>
          <span className="text-[10px] text-muted-foreground">
            {fixedIncomeSummary?.bonds_count ?? 0} bond holdings
          </span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Total DV01 ($)
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-emerald-400">
            {formatDV01(fixedIncomeSummary?.portfolio_total_dv01 ?? 0, fixedIncomeSummary?.base_currency || "USD")}
          </div>
          <span className="text-[10px] text-muted-foreground">P&L impact per +1 bp yield shift</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Modified Duration
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-cyan-400">
            {formatDuration(fixedIncomeSummary?.portfolio_weighted_modified_duration ?? 0)}
          </div>
          <span className="text-[10px] text-muted-foreground">Weighted interest rate risk</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Macaulay Duration
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-white">
            {formatDuration(fixedIncomeSummary?.portfolio_weighted_macaulay_duration ?? 0)}
          </div>
          <span className="text-[10px] text-muted-foreground">Weighted average maturity of cashflows</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Portfolio Convexity
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-amber-400">
            {formatConvexity(fixedIncomeSummary?.portfolio_weighted_convexity ?? 0)}
          </div>
          <span className="text-[10px] text-muted-foreground">Second-order curvature</span>
        </div>

        <div className="rounded-lg border border-border bg-surface-1 p-3.5">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
            Weighted Yield (YTM)
          </span>
          <div className="mt-1 text-lg font-bold font-mono text-purple-400">
            {formatYield(fixedIncomeSummary?.portfolio_weighted_yield ?? 0)}
          </div>
          <span className="text-[10px] text-muted-foreground">Annualized nominal yield</span>
        </div>
      </div>

      {/* Main Grid: Holdings Table & Key-Rate Profile */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Holdings Table (2 cols) */}
        <div className="space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
              Fixed-Income Holdings & Sensitivity Decomposition
            </h3>
          </div>

          <div className="overflow-x-auto rounded-lg border border-border bg-surface-1 shadow-sm">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-border bg-surface-2 text-[11px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="py-2.5 px-3">Instrument</th>
                  <th className="py-2.5 px-2">Issuer</th>
                  <th className="py-2.5 px-2 text-right">Dirty Px</th>
                  <th className="py-2.5 px-2 text-right">YTM</th>
                  <th className="py-2.5 px-2 text-right">Mod Dur</th>
                  <th className="py-2.5 px-2 text-right">Convexity</th>
                  <th className="py-2.5 px-2 text-right">Pos DV01</th>
                  <th className="py-2.5 px-2 text-center">Cash Flows</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {positions.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-6 text-center text-muted-foreground">
                      No fixed income positions identified.
                    </td>
                  </tr>
                ) : (
                  positions.map((pos) => {
                    const isSelected = activeBondForSchedule === pos.instrument_id;
                    return (
                      <tr
                        key={pos.position_id}
                        className={`transition-colors hover:bg-surface-2/60 ${
                          isSelected ? "bg-emerald-500/10 border-l-2 border-l-emerald-500" : ""
                        }`}
                      >
                        <td className="py-2.5 px-3 font-semibold text-white">
                          <div>{pos.instrument_id}</div>
                          <div className="text-[10px] text-muted-foreground">
                            Face: ${pos.face_value.toFixed(0)} | Qty: {pos.quantity}
                          </div>
                        </td>
                        <td className="py-2.5 px-2 text-slate-300">{pos.issuer_name}</td>
                        <td className="py-2.5 px-2 text-right text-white font-bold">
                          {formatBondPrice(pos.sensitivities.dirty_price)}
                          <div className="text-[10px] text-muted-foreground">
                            Clean: {formatBondPrice(pos.sensitivities.clean_price)}
                          </div>
                        </td>
                        <td className="py-2.5 px-2 text-right text-purple-400 font-bold">
                          {formatYield(pos.sensitivities.yield_to_maturity)}
                        </td>
                        <td className="py-2.5 px-2 text-right text-cyan-400">
                          {formatDuration(pos.sensitivities.modified_duration)}
                        </td>
                        <td className="py-2.5 px-2 text-right text-amber-400">
                          {formatConvexity(pos.sensitivities.convexity)}
                        </td>
                        <td className="py-2.5 px-2 text-right text-emerald-400 font-bold">
                          {formatDV01(pos.position_dv01, pos.currency)}
                        </td>
                        <td className="py-2.5 px-2 text-center">
                          <button
                            onClick={() => handleInspectCashFlows(pos.instrument_id)}
                            className="rounded border border-border px-2 py-0.5 text-[10px] text-slate-300 hover:bg-surface-3"
                          >
                            {isSelected ? "Active" : "Schedule"}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Cash Flow Schedule Inspector */}
          {selectedBondCashFlows && (
            <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <span>Projected Cash Flows: {selectedBondCashFlows.instrument_id}</span>
                  <span className="text-[10px] text-muted-foreground">
                    Accrued: ${selectedBondCashFlows.accrued_interest.toFixed(4)}
                  </span>
                </h4>
                <div className="text-xs text-muted-foreground">
                  Dirty Price: ${selectedBondCashFlows.dirty_price.toFixed(4)} | Clean: ${selectedBondCashFlows.clean_price.toFixed(4)}
                </div>
              </div>

              <div className="max-h-64 overflow-y-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="border-b border-border bg-surface-2 text-[10px] uppercase text-muted-foreground">
                    <tr>
                      <th className="py-1.5 px-2">#</th>
                      <th className="py-1.5 px-2">Payment Date</th>
                      <th className="py-1.5 px-2 text-right">Year (t)</th>
                      <th className="py-1.5 px-2 text-right">Coupon</th>
                      <th className="py-1.5 px-2 text-right">Principal</th>
                      <th className="py-1.5 px-2 text-right">Total CF</th>
                      <th className="py-1.5 px-2 text-right">DF</th>
                      <th className="py-1.5 px-2 text-right">PV</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {selectedBondCashFlows.cash_flows.map((cf) => (
                      <tr key={cf.period_index} className="hover:bg-surface-2/40">
                        <td className="py-1.5 px-2 text-muted-foreground">{cf.period_index}</td>
                        <td className="py-1.5 px-2 text-white">{cf.payment_date.split("T")[0]}</td>
                        <td className="py-1.5 px-2 text-right text-muted-foreground">{cf.year_fraction.toFixed(3)}</td>
                        <td className="py-1.5 px-2 text-right text-slate-300">${cf.coupon_amount.toFixed(2)}</td>
                        <td className="py-1.5 px-2 text-right text-slate-300">${cf.principal_amount.toFixed(2)}</td>
                        <td className="py-1.5 px-2 text-right text-white font-bold">${cf.total_cash_flow.toFixed(2)}</td>
                        <td className="py-1.5 px-2 text-right text-cyan-400">{cf.discount_factor.toFixed(4)}</td>
                        <td className="py-1.5 px-2 text-right text-emerald-400 font-bold">${cf.present_value.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Key-Rate Profile & Yield Curve Viewer */}
        <div className="space-y-6">
          {/* Key-Rate Duration & DV01 Term Structure */}
          <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Key-Rate DV01 Term Structure
            </h3>
            <p className="text-[11px] text-muted-foreground">
              Sensitivity to local 1 bp yield shifts across individual maturity buckets.
            </p>

            <div className="space-y-2 font-mono text-xs">
              {Object.keys(krProfile).length === 0 ? (
                <div className="py-4 text-center text-muted-foreground">No key-rate distribution.</div>
              ) : (
                Object.entries(krProfile).map(([tenor, dv01Val]) => {
                  const pct = totalDv01 > 0 ? (dv01Val / totalDv01) * 100 : 0;
                  return (
                    <div key={tenor} className="space-y-1">
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="font-bold text-white">{tenor}</span>
                        <span className="text-emerald-400 font-bold">
                          {formatDV01(dv01Val, fixedIncomeSummary?.base_currency || "USD")} ({pct.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-surface-3 rounded overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded"
                          style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Calibrated Yield Curve Viewer */}
          {curveDefinition && (
            <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-border pb-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  {curveDefinition.curve_id.replace(/_/g, " ")}
                </h3>
                <span className="text-[10px] font-mono text-cyan-400">{curveDefinition.interpolation_method}</span>
              </div>

              <div className="max-h-48 overflow-y-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="border-b border-border bg-surface-2 text-[10px] uppercase text-muted-foreground">
                    <tr>
                      <th className="py-1 px-2">Tenor</th>
                      <th className="py-1 px-2 text-right">Years</th>
                      <th className="py-1 px-2 text-right">Par Rate</th>
                      <th className="py-1 px-2 text-right">DF</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {curveDefinition.points.map((pt) => (
                      <tr key={pt.label} className="hover:bg-surface-2/40">
                        <td className="py-1 px-2 text-white font-bold">{pt.label}</td>
                        <td className="py-1 px-2 text-right text-muted-foreground">{pt.tenor_years.toFixed(2)}</td>
                        <td className="py-1 px-2 text-right text-purple-400 font-bold">{(pt.rate * 100).toFixed(2)}%</td>
                        <td className="py-1 px-2 text-right text-cyan-400">{pt.discount_factor.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Interactive Bond Pricing & Duration Calculator */}
          <div className="rounded-lg border border-border bg-surface-1 p-4 shadow-sm space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Interactive Bond Sensitivity Solver
            </h3>

            <form onSubmit={handleRunBondCalculator} className="space-y-2.5 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Face Value ($)</label>
                  <input
                    type="number"
                    step="1"
                    value={calcFace}
                    onChange={(e) => setCalcFace(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Coupon Rate (%)</label>
                  <input
                    type="number"
                    step="0.0025"
                    value={calcCoupon}
                    onChange={(e) => setCalcCoupon(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Frequency</label>
                  <select
                    value={calcFreq}
                    onChange={(e) => setCalcFreq(e.target.value as CouponFrequency)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  >
                    <option value="ANNUAL">Annual (1/y)</option>
                    <option value="SEMI_ANNUAL">Semi-Annual (2/y)</option>
                    <option value="QUARTERLY">Quarterly (4/y)</option>
                    <option value="MONTHLY">Monthly (12/y)</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-muted-foreground block mb-1">Maturity (Yrs)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={calcMaturityYears}
                    onChange={(e) => setCalcMaturityYears(parseFloat(e.target.value) || 0)}
                    className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] text-muted-foreground block mb-1">Target Clean Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={calcPrice}
                  onChange={(e) => setCalcPrice(parseFloat(e.target.value) || 0)}
                  className="w-full rounded border border-border bg-surface-2 px-2 py-1 font-mono text-white"
                />
              </div>

              <button
                type="submit"
                disabled={calculating}
                className="w-full mt-2 rounded bg-emerald-600 px-3 py-1.5 font-semibold text-white transition-colors hover:bg-emerald-500 disabled:opacity-50"
              >
                {calculating ? "Solving YTM..." : "Solve YTM, Duration & DV01"}
              </button>
            </form>

            {calcError && <div className="text-xs text-rose-400 bg-rose-500/10 p-2 rounded">{calcError}</div>}

            {calcResult && (
              <div className="mt-3 rounded border border-border bg-surface-2 p-3 font-mono text-xs space-y-2">
                <div className="flex justify-between items-center border-b border-border pb-1.5 font-bold">
                  <span className="text-slate-300">Yield to Maturity (YTM):</span>
                  <span className="text-purple-400 text-sm">{formatYield(calcResult.yield_to_maturity)}</span>
                </div>
                <div className="grid grid-cols-2 gap-1 text-[11px]">
                  <div>Dirty Price: <span className="text-white font-bold">${calcResult.dirty_price.toFixed(4)}</span></div>
                  <div>Accrued Int: <span className="text-white font-bold">${calcResult.accrued_interest.toFixed(4)}</span></div>
                  <div>Mod Dur: <span className="text-cyan-400 font-bold">{formatDuration(calcResult.modified_duration)}</span></div>
                  <div>Mac Dur: <span className="text-white font-bold">{formatDuration(calcResult.macaulay_duration)}</span></div>
                  <div>Convexity: <span className="text-amber-400 font-bold">{formatConvexity(calcResult.convexity)}</span></div>
                  <div>DV01 (per 100): <span className="text-emerald-400 font-bold">${calcResult.dv01_per_100_face.toFixed(4)}</span></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

