"use client";

import React from "react";

interface MonetaryFilterInputProps {
  value: string;
  currency?: string | null;
  magnitude?: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS";
  currencyOptions?: string[];
  magnitudeOptions?: string[];
  onChangeValue: (val: string) => void;
  onChangeCurrency?: (cur: string) => void;
  onChangeMagnitude?: (mag: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS") => void;
  disabled?: boolean;
  hasError?: boolean;
  ariaLabel?: string;
}

const DEFAULT_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"];
const DEFAULT_MAGNITUDES: Array<"UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS"> = [
  "UNITS",
  "MILLIONS",
  "BILLIONS",
  "TRILLIONS",
];

const MAGNITUDE_LABELS: Record<string, string> = {
  UNITS: "1x",
  THOUSANDS: "K",
  MILLIONS: "M",
  BILLIONS: "B",
  TRILLIONS: "T",
};

export function MonetaryFilterInput({
  value,
  currency = "USD",
  magnitude = "UNITS",
  currencyOptions = DEFAULT_CURRENCIES,
  magnitudeOptions,
  onChangeValue,
  onChangeCurrency,
  onChangeMagnitude,
  disabled = false,
  hasError = false,
  ariaLabel = "Monetary amount",
}: MonetaryFilterInputProps) {
  const allowedMagnitudes = (magnitudeOptions as typeof DEFAULT_MAGNITUDES) || DEFAULT_MAGNITUDES;

  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "" || /^[-+]?([0-9]*\.?[0-9]*)?$/.test(raw)) {
      onChangeValue(raw);
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {/* Currency Selector */}
      {onChangeCurrency && currencyOptions.length > 1 && (
        <select
          value={currency || "USD"}
          onChange={(e) => onChangeCurrency(e.target.value)}
          disabled={disabled}
          aria-label="Filter currency"
          className="h-7 rounded border border-border/60 bg-background/80 px-1.5 text-[11px] font-mono text-muted-foreground transition-colors hover:border-border focus:border-primary focus:outline-none"
        >
          {currencyOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      )}

      {/* Numeric Amount Input */}
      <div className="relative flex items-center">
        <input
          type="text"
          inputMode="decimal"
          value={value}
          onChange={handleValueChange}
          placeholder="0.00"
          disabled={disabled}
          aria-label={ariaLabel}
          className={`h-7 w-24 rounded border bg-background/80 px-2 text-xs font-mono transition-colors focus:outline-none focus:ring-1 ${
            hasError
              ? "border-destructive/80 focus:ring-destructive"
              : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
          } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        />
      </div>

      {/* Magnitude Buttons */}
      {onChangeMagnitude && allowedMagnitudes.length > 1 && (
        <div className="flex items-center rounded border border-border/50 bg-muted/20 p-0.5">
          {allowedMagnitudes.map((mag) => {
            const isSelected = magnitude === mag;
            return (
              <button
                key={mag}
                type="button"
                onClick={() => onChangeMagnitude(mag)}
                disabled={disabled}
                aria-label={`Scale ${mag}`}
                className={`rounded px-1.5 py-0.5 text-[10px] font-mono transition-colors ${
                  isSelected
                    ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {MAGNITUDE_LABELS[mag] || mag}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
