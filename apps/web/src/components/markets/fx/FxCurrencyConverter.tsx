"use client";

import React, { useEffect } from "react";
import { useFxConversion } from "@/hooks/markets/useFxConversion";
import {
  CurrencyItem,
  formatFxFreshnessBadge,
  formatMoneyAmount,
  FxConversionMode,
} from "@/lib/markets/fx";
import {
  AlertCircle,
  ArrowLeftRight,
  Calculator,
} from "lucide-react";

export interface FxCurrencyConverterProps {
  currencies: CurrencyItem[];
  defaultFrom?: string;
  defaultTo?: string;
}

export function FxCurrencyConverter({
  currencies,
  defaultFrom = "EUR",
  defaultTo = "USD",
}: FxCurrencyConverterProps) {
  const {
    amount,
    setAmount,
    fromCurrency,
    setFromCurrency,
    toCurrency,
    setToCurrency,
    mode,
    setMode,
    result,
    isLoading,
    isError,
    error,
    convert,
    swapCurrencies,
  } = useFxConversion({
    initialAmount: "100",
    initialFromCurrency: defaultFrom,
    initialToCurrency: defaultTo,
  });

  // Run initial conversion when mounted
  useEffect(() => {
    convert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    convert();
  };

  const destMeta = currencies.find((c) => c.code === toCurrency);
  const fromMeta = currencies.find((c) => c.code === fromCurrency);
  const minorUnits = destMeta?.minor_units ?? 2;
  const destSymbol = destMeta?.symbol || "";

  const freshness = formatFxFreshnessBadge(result?.freshness_status || "UNKNOWN");

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-4 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[var(--atlas-border-subtle)] pb-2.5 mb-3.5">
        <div className="flex items-center gap-2">
          <Calculator className="h-4 w-4 text-emerald-400" aria-hidden="true" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
            Indicative Currency Converter
          </h2>
        </div>
        <span className="text-[10px] font-mono text-[var(--atlas-text-tertiary)] bg-zinc-800/80 px-2 py-0.5 rounded border border-zinc-700/60">
          Read-Only / Non-Executable
        </span>
      </div>

      {/* Form */}
      <form onSubmit={handleFormSubmit} className="space-y-3">
        {/* Amount */}
        <div>
          <label
            htmlFor="converter-amount"
            className="block text-[11px] font-medium text-[var(--atlas-text-secondary)] mb-1"
          >
            Conversion Amount
          </label>
          <div className="relative">
            <input
              id="converter-amount"
              type="number"
              step="any"
              min="0.000001"
              max="1000000000000"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="e.g. 100"
              className="w-full px-3 py-1.5 text-xs font-mono bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-mono text-[var(--atlas-text-tertiary)] pointer-events-none">
              {fromCurrency}
            </span>
          </div>
        </div>

        {/* Currency Selectors & Swap Button */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-2 items-center">
          {/* From Currency */}
          <div>
            <label
              htmlFor="converter-from-currency"
              className="block text-[10px] text-[var(--atlas-text-tertiary)] mb-0.5"
            >
              From Currency
            </label>
            <select
              id="converter-from-currency"
              value={fromCurrency}
              onChange={(e) => setFromCurrency(e.target.value)}
              className="w-full py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 cursor-pointer font-mono"
            >
              {currencies.map((c) => (
                <option key={`from-${c.code}`} value={c.code}>
                  {c.code} - {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <div className="pt-4 flex justify-center">
            <button
              type="button"
              onClick={swapCurrencies}
              disabled={isLoading}
              aria-label="Swap from and to currencies"
              title="Swap Currencies"
              className="p-1.5 rounded text-[var(--atlas-text-secondary)] hover:text-emerald-400 bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
            >
              <ArrowLeftRight className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          </div>

          {/* To Currency */}
          <div>
            <label
              htmlFor="converter-to-currency"
              className="block text-[10px] text-[var(--atlas-text-tertiary)] mb-0.5"
            >
              To Currency
            </label>
            <select
              id="converter-to-currency"
              value={toCurrency}
              onChange={(e) => setToCurrency(e.target.value)}
              className="w-full py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 cursor-pointer font-mono"
            >
              {currencies.map((c) => (
                <option key={`to-${c.code}`} value={c.code}>
                  {c.code} - {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Mode Selector */}
        <div className="flex items-center justify-between text-[11px] pt-1">
          <label htmlFor="converter-mode" className="text-[var(--atlas-text-tertiary)]">
            Rate Basis:
          </label>
          <select
            id="converter-mode"
            value={mode}
            onChange={(e) => setMode(e.target.value as FxConversionMode)}
            className="py-1 px-2 text-[11px] bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-secondary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 cursor-pointer"
          >
            <option value="INDICATIVE_MID">Indicative Midpoint</option>
            <option value="QUOTE_SIDE_ILLUSTRATION">Quote-Side (Bid/Ask)</option>
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-1.5 px-3 rounded text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50 disabled:opacity-50 mt-1 cursor-pointer"
        >
          {isLoading ? "Calculating..." : "Convert"}
        </button>
      </form>

      {/* Error state */}
      {isError && (
        <div className="mt-3 p-3 bg-rose-500/10 border border-rose-500/20 rounded text-rose-400 text-xs flex items-start gap-2">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold block">Conversion Unavailable</span>
            <p className="text-[11px] leading-relaxed text-rose-300">
              {error?.message || "Exchange rate observation not available for this pair."}
            </p>
          </div>
        </div>
      )}

      {/* Success Result Card */}
      {result && !isError && (
        <div className="mt-3.5 p-3.5 bg-[var(--atlas-surface-card)]/70 border border-emerald-500/20 rounded space-y-2.5">
          {/* Output Display */}
          <div>
            <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">
              Indicative Converted Amount
            </div>
            <div className="text-xl sm:text-2xl font-bold font-mono text-emerald-400 tabular-nums">
              {formatMoneyAmount(result.output_amount, minorUnits, destSymbol)} {result.to_currency}
            </div>
            <div className="text-[11px] font-mono text-[var(--atlas-text-secondary)] mt-0.5">
              {formatMoneyAmount(result.input_amount, fromMeta?.minor_units ?? 2)} {result.from_currency} =
            </div>
          </div>

          {/* Rate & Meta Details */}
          <div className="text-[10px] font-mono text-[var(--atlas-text-tertiary)] border-t border-[var(--atlas-border-subtle)] pt-2 space-y-1">
            <div className="flex items-center justify-between">
              <span>Rate Basis:</span>
              <span className="text-[var(--atlas-text-secondary)]">
                {result.rate_kind}
                {result.quote_side ? ` (${result.quote_side})` : ""}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Rate Used:</span>
              <span className="text-[var(--atlas-text-primary)] font-semibold">
                {Number(result.rate_used).toFixed(6)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Direction:</span>
              <span className="text-sky-400">{result.calculation_direction}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Freshness:</span>
              <span className={freshness.badgeClass}>{freshness.label}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Provider:</span>
              <span>{result.provider}</span>
            </div>
          </div>

          {/* Institutional Disclaimer */}
          <div className="text-[10px] text-[var(--atlas-text-tertiary)] leading-tight border-t border-[var(--atlas-border-subtle)] pt-2">
            {result.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
