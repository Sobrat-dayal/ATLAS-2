"use client";

import React, { useState } from "react";
import {
  Award,
  Check,
  Info,
  Plus,
  Scale,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import {
  RankingDirection,
  RankingFactorWeight,
  RankingMethod,
  RankingMode,
  RankingTransformation,
  ScreenerColumnDefinition,
  ScreenerRankingSpec,
} from "@/lib/screeners/types";

interface RankingConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  rankingSpec: ScreenerRankingSpec | null;
  columnsRegistry: ScreenerColumnDefinition[];
  onApplyRanking: (spec: ScreenerRankingSpec | null) => void;
}

const DEFAULT_FACTOR_CANDIDATES = [
  { id: "market_cap", label: "Market Capitalization", defaultDirection: "higher_value_first" as RankingDirection },
  { id: "pe_ratio", label: "P/E Ratio (LTM)", defaultDirection: "lower_value_first" as RankingDirection },
  { id: "revenue_growth_yoy", label: "Revenue Growth YoY", defaultDirection: "higher_value_first" as RankingDirection },
  { id: "ebitda_margin", label: "EBITDA Margin", defaultDirection: "higher_value_first" as RankingDirection },
  { id: "roe", label: "Return on Equity (ROE)", defaultDirection: "higher_value_first" as RankingDirection },
  { id: "rsi_14", label: "RSI (14-day Momentum)", defaultDirection: "higher_value_first" as RankingDirection },
  { id: "volatility_30d", label: "Historical Volatility (30d)", defaultDirection: "lower_value_first" as RankingDirection },
];

export function RankingConfigModal({
  isOpen,
  onClose,
  rankingSpec,
  columnsRegistry,
  onApplyRanking,
}: RankingConfigModalProps) {
  const [mode, setMode] = useState<RankingMode>(rankingSpec?.mode ?? "single_factor");
  const [cohortPolicy, setCohortPolicy] = useState<string>(
    rankingSpec?.cohort_policy ?? "filter_matched_securities"
  );
  const [method, setMethod] = useState<RankingMethod>(rankingSpec?.method ?? "dense_rank");
  const [transformation, setTransformation] = useState<RankingTransformation>(
    rankingSpec?.factors?.[0]?.transformation ?? "percentile"
  );

  // Single-factor mode state
  const [singleFactorId, setSingleFactorId] = useState<string>(
    rankingSpec?.factors?.[0]?.factor_id ?? "market_cap"
  );
  const [singleDirection, setSingleDirection] = useState<RankingDirection>(
    rankingSpec?.factors?.[0]?.direction ?? "higher_value_first"
  );

  // Multi-factor composite mode state
  const [factors, setFactors] = useState<RankingFactorWeight[]>(
    rankingSpec && rankingSpec.factors && rankingSpec.factors.length > 0
      ? rankingSpec.factors
      : [
          { factor_id: "revenue_growth_yoy", weight: 0.5, direction: "higher_value_first", transformation: "z_score" },
          { factor_id: "pe_ratio", weight: 0.5, direction: "lower_value_first", transformation: "z_score" },
        ]
  );

  React.useEffect(() => {
    if (isOpen) {
      if (rankingSpec) {
        setMode(rankingSpec.mode);
        setCohortPolicy(rankingSpec.cohort_policy ?? "filter_matched_securities");
        setMethod(rankingSpec.method);
        if (rankingSpec.factors && rankingSpec.factors.length > 0) {
          setSingleFactorId(rankingSpec.factors[0].factor_id);
          setSingleDirection(rankingSpec.factors[0].direction);
          setTransformation(rankingSpec.factors[0].transformation);
          setFactors(rankingSpec.factors);
        }
      }
    }
  }, [isOpen, rankingSpec]);

  if (!isOpen) return null;

  // Available numeric factors from columnsRegistry
  const numericColumns = columnsRegistry.filter((c) => c.data_type === "numeric" || c.data_type === "percentage" || c.data_type === "currency" || c.data_type === "integer");
  const factorOptions = numericColumns.length > 0
    ? numericColumns.map((c) => ({ id: c.column_id, label: c.display_label }))
    : DEFAULT_FACTOR_CANDIDATES;

  // Multi-factor composite weight helpers
  const totalWeight = factors.reduce((sum, f) => sum + (f.weight || 0), 0);

  const handleAddCompositeFactor = () => {
    if (factors.length >= 10) return;
    const available = factorOptions.find((fo) => !factors.some((fw) => fw.factor_id === fo.id));
    const factorId = available ? available.id : factorOptions[0]?.id ?? "market_cap";
    setFactors((prev) => [
      ...prev,
      { factor_id: factorId, weight: 0.2, direction: "higher_value_first", transformation: "z_score" },
    ]);
  };

  const handleRemoveCompositeFactor = (index: number) => {
    setFactors((prev) => {
      const copy = [...prev];
      copy.splice(index, 1);
      return copy.length > 0 ? copy : [{ factor_id: "market_cap", weight: 1.0, direction: "higher_value_first", transformation: "z_score" }];
    });
  };

  const handleUpdateCompositeFactor = (
    index: number,
    factor_id?: string,
    weight?: number,
    direction?: RankingDirection,
    factorTransformation?: RankingTransformation
  ) => {
    setFactors((prev) => {
      const copy = [...prev];
      copy[index] = {
        factor_id: factor_id ?? copy[index].factor_id,
        weight: weight !== undefined ? Math.max(0, weight) : copy[index].weight,
        direction: direction ?? copy[index].direction,
        transformation: factorTransformation ?? copy[index].transformation,
      };
      return copy;
    });
  };

  const handleNormalizeWeights = () => {
    if (totalWeight <= 0) return;
    setFactors((prev) =>
      prev.map((fw) => ({
        ...fw,
        weight: Number((fw.weight / totalWeight).toFixed(4)),
      }))
    );
  };

  const handleApply = () => {
    const finalFactors: RankingFactorWeight[] =
      mode === "single_factor"
        ? [
            {
              factor_id: singleFactorId,
              weight: 1.0,
              direction: singleDirection,
              transformation,
            },
          ]
        : factors;

    const spec: ScreenerRankingSpec = {
      mode,
      cohort_policy: cohortPolicy,
      method,
      factors: finalFactors,
      missing_value_policy: "exclude",
      minimum_coverage: 1.0,
      methodology_version: "1.0.0",
    };

    onApplyRanking(spec);
    onClose();
  };

  const handleClear = () => {
    onApplyRanking(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-3xl rounded-lg border border-border bg-card shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/70 px-6 py-4 bg-muted/30">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                Quantitative Factor Ranking Engine
              </h2>
              <p className="text-xs text-muted-foreground">
                Cross-Sectional Factor Normalization, Standardized Z-Scores & Multi-Factor Composite Rankings
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {/* Disclosure Banner */}
          <div className="flex items-start gap-2.5 rounded-md bg-primary/5 border border-primary/20 p-3 text-xs text-muted-foreground">
            <Info className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p>
                <strong className="text-foreground">Statistical Factor Evaluation:</strong> Factor ranking scores are relative ordinal positions and standardized sample statistics within the chosen eligible population. They do not constitute investment recommendations or expected return predictions.
              </p>
              <p className="text-[11px] text-muted-foreground/80">
                Strict complete-case policy: securities with missing metrics are excluded from factor calculation. Zero imputation is strictly prohibited.
              </p>
            </div>
          </div>

          {/* Mode Selector Tabs */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">Ranking Methodology Mode</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setMode("single_factor")}
                className={`flex items-center gap-2.5 p-3 rounded-md border text-left transition-all ${
                  mode === "single_factor"
                    ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                    : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                }`}
              >
                <Award className="h-4 w-4 shrink-0" />
                <div>
                  <div className="text-xs font-semibold text-foreground">Single Factor Ranking</div>
                  <div className="text-[11px] text-muted-foreground">
                    Rank directly by one financial metric, ratio, or technical factor
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMode("multi_factor_composite")}
                className={`flex items-center gap-2.5 p-3 rounded-md border text-left transition-all ${
                  mode === "multi_factor_composite"
                    ? "border-primary bg-primary/10 text-primary font-medium shadow-sm"
                    : "border-border/80 bg-background hover:bg-muted/40 text-muted-foreground"
                }`}
              >
                <Scale className="h-4 w-4 shrink-0" />
                <div>
                  <div className="text-xs font-semibold text-foreground">Multi-Factor Composite</div>
                  <div className="text-[11px] text-muted-foreground">
                    Combine weighted standardized Z-scores across up to 10 factors
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Mode Configuration */}
          {mode === "single_factor" ? (
            <div className="p-4 rounded-lg border border-border/70 bg-muted/20 space-y-3">
              <div className="text-xs font-semibold text-foreground">Single Factor Configuration</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Metric Selector */}
                <div className="space-y-1">
                  <label className="text-[11px] font-medium text-muted-foreground">Ranking Metric</label>
                  <select
                    aria-label="Ranking Metric"
                    value={singleFactorId}
                    onChange={(e) => setSingleFactorId(e.target.value)}
                    className="h-8 w-full rounded border border-border/80 bg-background px-2.5 text-xs font-medium text-foreground focus:border-primary focus:outline-none"
                  >
                    {factorOptions.map((fo) => (
                      <option key={fo.id} value={fo.id}>
                        {fo.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Factor Direction */}
                <div className="space-y-1">
                  <label className="text-[11px] font-medium text-muted-foreground">Rank Direction</label>
                  <select
                    aria-label="Rank Direction"
                    value={singleDirection}
                    onChange={(e) => setSingleDirection(e.target.value as RankingDirection)}
                    className="h-8 w-full rounded border border-border/80 bg-background px-2.5 text-xs font-medium text-foreground focus:border-primary focus:outline-none"
                  >
                    <option value="higher_value_first">Higher Value First (e.g. Growth, Market Cap, Margins)</option>
                    <option value="lower_value_first">Lower Value First (e.g. Valuation Ratios, Volatility)</option>
                  </select>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-lg border border-border/70 bg-muted/20 space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-semibold text-foreground">
                  Composite Factor Weights ({factors.length}/10)
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-mono font-medium ${Math.abs(totalWeight - 1.0) > 0.001 ? "text-amber-500" : "text-emerald-500"}`}>
                    Sum: {totalWeight.toFixed(2)}
                  </span>
                  {Math.abs(totalWeight - 1.0) > 0.001 && (
                    <button
                      type="button"
                      onClick={handleNormalizeWeights}
                      className="text-[10px] font-medium text-primary hover:underline"
                    >
                      Normalize to 1.0
                    </button>
                  )}
                </div>
              </div>

              {/* Factors List */}
              <div className="space-y-2">
                {factors.map((fw, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-2.5 rounded bg-background border border-border/60">
                    <span className="text-[11px] font-mono text-muted-foreground w-5 text-center">#{idx + 1}</span>

                    {/* Factor Selector */}
                    <select
                      aria-label={`Composite Factor ${idx + 1}`}
                      value={fw.factor_id}
                      onChange={(e) => handleUpdateCompositeFactor(idx, e.target.value)}
                      className="h-8 flex-1 min-w-[140px] rounded border border-border/80 bg-background px-2 text-xs font-medium text-foreground focus:border-primary focus:outline-none"
                    >
                      {factorOptions.map((fo) => (
                        <option key={fo.id} value={fo.id}>
                          {fo.label}
                        </option>
                      ))}
                    </select>

                    {/* Direction */}
                    <select
                      aria-label={`Direction ${idx + 1}`}
                      value={fw.direction}
                      onChange={(e) => handleUpdateCompositeFactor(idx, undefined, undefined, e.target.value as RankingDirection)}
                      className="h-8 w-36 rounded border border-border/80 bg-background px-2 text-[11px] text-muted-foreground focus:border-primary focus:outline-none"
                    >
                      <option value="higher_value_first">Higher First</option>
                      <option value="lower_value_first">Lower First</option>
                    </select>

                    {/* Weight Input */}
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        min="0"
                        max="10"
                        step="0.05"
                        value={fw.weight}
                        onChange={(e) => handleUpdateCompositeFactor(idx, undefined, parseFloat(e.target.value) || 0)}
                        className="h-8 w-16 rounded border border-border/80 bg-background px-2 text-xs font-mono text-right focus:border-primary focus:outline-none"
                        title="Factor Weight"
                      />
                      <span className="text-xs text-muted-foreground">wt</span>
                    </div>

                    {/* Remove */}
                    <button
                      type="button"
                      onClick={() => handleRemoveCompositeFactor(idx)}
                      className="p-1 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                      title="Remove Factor"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>

              {factors.length < 10 && (
                <button
                  type="button"
                  onClick={handleAddCompositeFactor}
                  className="flex w-full items-center justify-center gap-1.5 py-2 rounded border border-dashed border-border/80 text-xs font-medium text-muted-foreground hover:border-primary/50 hover:text-primary transition-colors bg-background"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Composite Factor ({factors.length}/10)</span>
                </button>
              )}
            </div>
          )}

          {/* Statistical Parameters: Cohort, Transformation, Method */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Cohort Policy */}
            <div className="space-y-1">
              <label className="text-[11px] font-medium text-muted-foreground">Eligible Cohort</label>
              <select
                aria-label="Eligible Cohort"
                value={cohortPolicy}
                onChange={(e) => setCohortPolicy(e.target.value)}
                className="h-8 w-full rounded border border-border/80 bg-background px-2 text-xs text-foreground focus:border-primary focus:outline-none"
              >
                <option value="filter_matched_securities">Filtered Results Subset</option>
                <option value="all_eligible_universe">Full Universe Cohort</option>
              </select>
            </div>

            {/* Transformation */}
            <div className="space-y-1">
              <label className="text-[11px] font-medium text-muted-foreground">Score Transformation</label>
              <select
                aria-label="Score Transformation"
                value={transformation}
                onChange={(e) => setTransformation(e.target.value as RankingTransformation)}
                className="h-8 w-full rounded border border-border/80 bg-background px-2 text-xs text-foreground focus:border-primary focus:outline-none"
              >
                <option value="percentile">Percentile (0.0% - 100.0%)</option>
                <option value="z_score">Standardized Z-Score (μ=0, σ=1)</option>
                <option value="raw_rank">Raw Ordinal Rank (1 to N)</option>
              </select>
            </div>

            {/* Tie-Breaker Method */}
            <div className="space-y-1">
              <label className="text-[11px] font-medium text-muted-foreground">Tie Method</label>
              <select
                aria-label="Tie Method"
                value={method}
                onChange={(e) => setMethod(e.target.value as RankingMethod)}
                className="h-8 w-full rounded border border-border/80 bg-background px-2 text-xs text-foreground focus:border-primary focus:outline-none"
              >
                <option value="dense_rank">Dense Rank (1, 2, 2, 3)</option>
                <option value="competition_rank">Competition Rank (1, 2, 2, 4)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border/70 px-6 py-3 bg-muted/20">
          <div>
            {rankingSpec && (
              <button
                type="button"
                onClick={handleClear}
                className="text-xs text-destructive hover:underline font-medium"
              >
                Clear Ranking
              </button>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-border bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleApply}
              className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Check className="h-3.5 w-3.5" />
              <span>Apply Ranking</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
