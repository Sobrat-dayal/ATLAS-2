"use client";

import React, { useEffect, useState } from "react";
import {
  AtlasOptionContract,
  LegSide,
  OptionChainResponse,
  OptionPositionItem,
  OptionQuote,
  OptionStrategyAnalysisResult,
  OptionStrategyLeg,
  StrategyTemplateDefinition,
} from "@/lib/options/types";
import {
  analyzeOptionStrategy,
  getOptionChain,
  getOptionContract,
  getOptionExpirations,
  getOptionsCapabilities,
  getOptionUnderlyings,
  getStrategyTemplates,
  getStrikeActivity,
  getUnderlyingAdjustments,
  getUserOptionPositions,
  getVolatilitySmile,
  getVolatilityTermStructure,
} from "@/lib/options/api";
import { OptionsNavigation, OptionsViewMode } from "./OptionsNavigation";
import { UnderlyingItem, UnderlyingSearch } from "./UnderlyingSearch";
import { ExpirationSelector } from "./ExpirationSelector";
import { OptionsChain } from "./OptionsChain";
import { OptionsStrategyBuilder } from "./OptionsStrategyBuilder";
import { OptionsVolatilityView } from "./OptionsVolatilityView";
import { OptionsActivityView } from "./OptionsActivityView";
import { OptionsPositionsView } from "./OptionsPositionsView";
import { OptionContractInspector } from "./OptionContractInspector";
import { OptionAdjustmentInspector } from "./OptionAdjustmentInspector";
import { OptionsStrategyWorkbench } from "./quant/OptionsStrategyWorkbench";
import {
  Activity,
  AlertTriangle,
  FileText,
  Info,
  Layers,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/options/formatters";

export function OptionsTerminal() {
  // Navigation & View Mode
  const [currentView, setCurrentView] = useState<OptionsViewMode>("CHAIN");

  // Underlyings & Expirations
  const [underlyings, setUnderlyings] = useState<UnderlyingItem[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("SPY");
  const [expirations, setExpirations] = useState<string[]>([]);
  const [selectedExpiration, setSelectedExpiration] = useState<string>("");

  // Options Chain
  const [chain, setChain] = useState<OptionChainResponse | null>(null);
  const [isChainLoading, setIsChainLoading] = useState<boolean>(false);

  // Strategy Builder
  const [strategyLegs, setStrategyLegs] = useState<OptionStrategyLeg[]>([]);
  const [templates, setTemplates] = useState<StrategyTemplateDefinition[]>([]);
  const [analysisResult, setAnalysisResult] =
    useState<OptionStrategyAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

  // Volatility & Activity
  const [smileData, setSmileData] = useState<any | null>(null);
  const [termStructureData, setTermStructureData] = useState<any | null>(null);
  const [activityData, setActivityData] = useState<any[]>([]);
  const [isVolLoading, setIsVolLoading] = useState<boolean>(false);

  // Portfolio Positions
  const [positions, setPositions] = useState<OptionPositionItem[]>([]);
  const [portfolioId, setPortfolioId] = useState<string>("PORT_USER_A_FUND");

  // Adjustments & Inspector Drawers
  const [adjustments, setAdjustments] = useState<any[]>([]);
  const [isAdjustmentsOpen, setIsAdjustmentsOpen] = useState<boolean>(false);
  const [inspectedContract, setInspectedContract] =
    useState<AtlasOptionContract | null>(null);
  const [inspectedQuote, setInspectedQuote] = useState<OptionQuote | null>(null);

  // Disclaimers Banner
  const [showDisclaimers, setShowDisclaimers] = useState<boolean>(false);

  // Initial Underlyings & Templates Load
  useEffect(() => {
    async function init() {
      try {
        const uList = await getOptionUnderlyings();
        setUnderlyings(uList);
        if (uList.length > 0 && !selectedSymbol) {
          setSelectedSymbol(uList[0].symbol);
        }

        const tList = await getStrategyTemplates();
        setTemplates(tList);
      } catch (err) {
        console.error("Failed to initialize options terminal:", err);
      }
    }
    init();
  }, []);

  // Fetch Expirations & Adjustments when Symbol changes
  useEffect(() => {
    if (!selectedSymbol) return;

    async function loadExpirationsAndAdjustments() {
      try {
        const exps = await getOptionExpirations(selectedSymbol);
        setExpirations(exps);
        if (exps.length > 0) {
          setSelectedExpiration(exps[0]);
        }

        const adjs = await getUnderlyingAdjustments(selectedSymbol);
        setAdjustments(adjs);
      } catch (err) {
        console.error("Failed to load expirations for", selectedSymbol, err);
      }
    }
    loadExpirationsAndAdjustments();
  }, [selectedSymbol]);

  // Fetch Chain when Symbol or Expiration changes
  useEffect(() => {
    if (!selectedSymbol || !selectedExpiration) return;

    async function loadChain() {
      setIsChainLoading(true);
      try {
        const c = await getOptionChain(selectedSymbol, selectedExpiration);
        setChain(c);
      } catch (err) {
        console.error("Failed to fetch chain:", err);
        setChain(null);
      } finally {
        setIsChainLoading(false);
      }
    }
    loadChain();
  }, [selectedSymbol, selectedExpiration]);

  // Fetch Volatility & Activity Data when entering those views
  useEffect(() => {
    if (!selectedSymbol || !selectedExpiration) return;

    if (currentView === "VOLATILITY") {
      setIsVolLoading(true);
      Promise.all([
        getVolatilitySmile(selectedSymbol, selectedExpiration),
        getVolatilityTermStructure(selectedSymbol),
      ])
        .then(([smile, term]) => {
          setSmileData(smile);
          setTermStructureData(term);
        })
        .catch((err) => console.error("Failed to load volatility:", err))
        .finally(() => setIsVolLoading(false));
    } else if (currentView === "ACTIVITY") {
      setIsVolLoading(true);
      getStrikeActivity(selectedSymbol, selectedExpiration)
        .then((res) => {
          setActivityData(res.activity_by_strike);
        })
        .catch((err) => console.error("Failed to load activity:", err))
        .finally(() => setIsVolLoading(false));
    } else if (currentView === "POSITIONS") {
      getUserOptionPositions(portfolioId)
        .then((pos) => setPositions(pos))
        .catch((err) => console.error("Failed to load positions:", err));
    }
  }, [currentView, selectedSymbol, selectedExpiration, portfolioId]);

  // Strategy Analysis trigger
  const handleAnalyzeStrategy = async (legsToAnalyze: OptionStrategyLeg[]) => {
    if (legsToAnalyze.length === 0) {
      setAnalysisResult(null);
      return;
    }
    setIsAnalyzing(true);
    try {
      const res = await analyzeOptionStrategy({
        strategy_name: "Custom Multi-Leg Strategy",
        underlying_symbol: selectedSymbol,
        expiration_date: selectedExpiration,
        legs: legsToAnalyze,
      });
      setAnalysisResult(res);
    } catch (err: any) {
      console.error("Strategy analysis error:", err);
      alert(err.message || "Failed to analyze option strategy");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Add Leg directly from Chain
  const handleAddLegFromChain = (
    contract: AtlasOptionContract,
    quote: OptionQuote,
    side: LegSide
  ) => {
    const isBuy = side === "LONG_CALL" || side === "LONG_PUT";
    const premium = isBuy ? quote.ask || 0.0 : quote.bid || 0.0;

    const newLeg: OptionStrategyLeg = {
      contract_id: contract.option_contract_id,
      side,
      quantity: 1,
      entry_premium: premium,
      multiplier: contract.contract_multiplier,
    };

    const updated = [...strategyLegs, newLeg];
    setStrategyLegs(updated);
    setCurrentView("STRATEGIES");
    handleAnalyzeStrategy(updated);
  };

  const selectedItem = underlyings.find((u) => u.symbol === selectedSymbol);
  const currency = selectedItem?.currency || "USD";

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-zinc-950 text-zinc-100 overflow-hidden font-sans">
      {/* Top Header & Search Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800 gap-3">
        <div className="flex items-center gap-3">
          <UnderlyingSearch
            underlyings={underlyings}
            selectedSymbol={selectedSymbol}
            onSelect={(sym) => setSelectedSymbol(sym)}
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDisclaimers(!showDisclaimers)}
            className="flex items-center gap-1 px-2.5 py-1 text-xs text-zinc-400 hover:text-zinc-200 bg-zinc-800/80 rounded border border-zinc-750 transition-colors"
          >
            <Info className="w-3.5 h-3.5" />
            <span>Regulatory & Risk Disclaimers</span>
          </button>
        </div>
      </div>

      {/* Disclaimers Dropdown Banner */}
      {showDisclaimers && (
        <div className="bg-zinc-900 border-b border-zinc-800 p-3 text-xs text-zinc-400 space-y-1">
          <p>
            <span className="font-semibold text-white">Options Risk Warning:</span> Options involve high risk and are not suitable for all investors. Prior to buying or selling options, investors must read Characteristics and Risks of Standardized Options (ODD).
          </p>
          <p>
            <span className="font-semibold text-white">Execution Boundary:</span> ATLAS provides institutional analytics and strategy payoff modeling. No automated trading, order routing, or broker execution is executed.
          </p>
          <p>
            <span className="font-semibold text-white">Expiration Settlement vs Mark-to-Market:</span> Payoff models reflect piecewise-linear intrinsic value at expiration cutoff (T = Expiration Cutoff). Mark-to-market Black-Scholes / QuantLib pricing is reserved for Stage 142.
          </p>
        </div>
      )}

      {/* Subview Navigation */}
      <OptionsNavigation
        currentView={currentView}
        onViewChange={(v) => setCurrentView(v)}
        selectedSymbol={selectedSymbol}
        underlyingPrice={selectedItem?.spot_price}
        currency={currency}
        hasAdjustedContracts={selectedItem?.has_adjusted_contracts}
        onOpenAdjustments={() => setIsAdjustmentsOpen(true)}
        legCount={strategyLegs.length}
      />

      {/* Expirations Bar (Shown for Chain, Volatility, Activity, Strategies) */}
      {currentView !== "POSITIONS" && (
        <ExpirationSelector
          expirations={expirations}
          selectedExpiration={selectedExpiration}
          onSelect={(exp) => setSelectedExpiration(exp)}
          daysToExpirationMap={
            chain ? { [chain.expiration_date]: chain.days_to_expiration } : {}
          }
        />
      )}

      {/* Main View Display Area */}
      <div className="flex-1 overflow-hidden relative">
        {/* OVERVIEW VIEW */}
        {currentView === "OVERVIEW" && (
          <div className="p-6 space-y-6 overflow-y-auto h-full">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-zinc-900/60 border border-zinc-800 p-4 rounded-xl">
                <div className="text-zinc-500 text-xs">Spot Underlying Price</div>
                <div className="font-mono text-2xl font-bold text-white mt-1">
                  {formatCurrency(selectedItem?.spot_price, currency)}
                </div>
                <div className="text-[10px] text-zinc-500 mt-1">
                  Market: {selectedItem?.market_id}
                </div>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800 p-4 rounded-xl">
                <div className="text-zinc-500 text-xs">Total Chain Volume</div>
                <div className="font-mono text-2xl font-bold text-cyan-400 mt-1">
                  {formatNumber(
                    (chain?.total_call_volume || 0) + (chain?.total_put_volume || 0)
                  )}
                </div>
                <div className="text-[10px] text-zinc-500 mt-1">
                  P/C Vol Ratio: {chain?.put_call_volume_ratio?.toFixed(2) || "—"}
                </div>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800 p-4 rounded-xl">
                <div className="text-zinc-500 text-xs">Total Open Interest</div>
                <div className="font-mono text-2xl font-bold text-white mt-1">
                  {formatNumber(
                    (chain?.total_call_oi || 0) + (chain?.total_put_oi || 0)
                  )}
                </div>
                <div className="text-[10px] text-zinc-500 mt-1">
                  P/C OI Ratio: {chain?.put_call_oi_ratio?.toFixed(2) || "—"}
                </div>
              </div>

              <div className="bg-zinc-900/60 border border-zinc-800 p-4 rounded-xl">
                <div className="text-zinc-500 text-xs">Contract Deliverable Multiplier</div>
                <div className="font-mono text-2xl font-bold text-amber-300 mt-1">
                  {selectedSymbol === "NIFTY" ? "50 Shares" : "100 Shares"}
                </div>
                <div className="text-[10px] text-zinc-500 mt-1">
                  Standard lot size for {selectedSymbol}
                </div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5">
              <h3 className="text-sm font-bold text-white mb-3">Institutional Research Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <button
                  onClick={() => setCurrentView("CHAIN")}
                  className="p-3 text-left bg-zinc-900 hover:bg-zinc-850 rounded-lg border border-zinc-800 transition-colors"
                >
                  <div className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
                    <Layers className="w-4 h-4" />
                    <span>Dual-Sided Options Chain</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    Inspect bid-ask spreads, volume, open interest and click quotes to build multi-leg strategies.
                  </p>
                </button>

                <button
                  onClick={() => setCurrentView("VOLATILITY")}
                  className="p-3 text-left bg-zinc-900 hover:bg-zinc-850 rounded-lg border border-zinc-800 transition-colors"
                >
                  <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4" />
                    <span>Volatility Smile & Skew</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    Analyze source-provided implied volatility curves, term structures, and 25-delta put/call skew.
                  </p>
                </button>

                <button
                  onClick={() => setCurrentView("STRATEGIES")}
                  className="p-3 text-left bg-zinc-900 hover:bg-zinc-850 rounded-lg border border-zinc-800 transition-colors"
                >
                  <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                    <Activity className="w-4 h-4" />
                    <span>Strategy Payoff Modeler</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    Model multi-leg spreads with analytical breakeven root finding and unbounded loss safeguards.
                  </p>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* OPTIONS CHAIN VIEW */}
        {currentView === "CHAIN" && (
          <OptionsChain
            chain={chain}
            onSelectContract={(contract, quote) => {
              setInspectedContract(contract);
              setInspectedQuote(quote);
            }}
            onAddLeg={handleAddLegFromChain}
            currency={currency}
            isLoading={isChainLoading}
          />
        )}

        {/* VOLATILITY & SKEW VIEW */}
        {currentView === "VOLATILITY" && (
          <OptionsVolatilityView
            smile={smileData}
            termStructure={termStructureData}
            currency={currency}
            isLoading={isVolLoading}
          />
        )}

        {/* ACTIVITY & OPEN INTEREST VIEW */}
        {currentView === "ACTIVITY" && (
          <OptionsActivityView
            activityData={activityData}
            expirationDate={selectedExpiration}
            currency={currency}
            isLoading={isVolLoading}
          />
        )}

        {/* STRATEGY BUILDER VIEW */}
        {currentView === "STRATEGIES" && (
          <OptionsStrategyBuilder
            legs={strategyLegs}
            onUpdateLegs={(updated) => setStrategyLegs(updated)}
            templates={templates}
            chain={chain}
            currency={currency}
            analysisResult={analysisResult}
            onAnalyze={handleAnalyzeStrategy}
            isAnalyzing={isAnalyzing}
          />
        )}

        {/* QUANT STRATEGY LAB VIEW (Stage 142 QuantLib) */}
        {currentView === "QUANT_LAB" && (
          <OptionsStrategyWorkbench
            initialSymbol={selectedSymbol}
            initialSpot={selectedItem?.spot_price || 500.0}
          />
        )}

        {/* POSITIONS VIEW */}
        {currentView === "POSITIONS" && (
          <OptionsPositionsView
            positions={positions}
            portfolioId={portfolioId}
            onSelectPortfolio={(id) => setPortfolioId(id)}
            currency={currency}
          />
        )}
      </div>

      {/* Contract Specification Inspector Drawer */}
      {inspectedContract && (
        <OptionContractInspector
          contract={inspectedContract}
          quote={inspectedQuote}
          onClose={() => {
            setInspectedContract(null);
            setInspectedQuote(null);
          }}
        />
      )}

      {/* Corporate Action Adjustment Drawer */}
      <OptionAdjustmentInspector
        symbol={selectedSymbol}
        adjustments={adjustments}
        isOpen={isAdjustmentsOpen}
        onClose={() => setIsAdjustmentsOpen(false)}
      />
    </div>
  );
}
