"use client";

import React from "react";

interface RangeFilterInputProps {
  minValue: string;
  maxValue: string;
  onChangeMin: (val: string) => void;
  onChangeMax: (val: string) => void;
  unitLabel?: string;
  disabled?: boolean;
  hasError?: boolean;
}

export function RangeFilterInput({
  minValue,
  maxValue,
  onChangeMin,
  onChangeMax,
  unitLabel,
  disabled = false,
  hasError = false,
}: RangeFilterInputProps) {
  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "" || /^[-+]?([0-9]*\.?[0-9]*)?$/.test(raw)) {
      onChangeMin(raw);
    }
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "" || /^[-+]?([0-9]*\.?[0-9]*)?$/.test(raw)) {
      onChangeMax(raw);
    }
  };

  return (
    <div className="flex items-center gap-1.5">
      <input
        type="text"
        inputMode="decimal"
        value={minValue}
        onChange={handleMinChange}
        placeholder="Min"
        disabled={disabled}
        aria-label="Range lower bound"
        className={`h-7 w-20 rounded border bg-background/80 px-2 text-xs font-mono transition-colors focus:outline-none focus:ring-1 ${
          hasError
            ? "border-destructive/80 focus:ring-destructive"
            : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      />
      <span className="text-[11px] font-medium text-muted-foreground select-none">to</span>
      <input
        type="text"
        inputMode="decimal"
        value={maxValue}
        onChange={handleMaxChange}
        placeholder="Max"
        disabled={disabled}
        aria-label="Range upper bound"
        className={`h-7 w-20 rounded border bg-background/80 px-2 text-xs font-mono transition-colors focus:outline-none focus:ring-1 ${
          hasError
            ? "border-destructive/80 focus:ring-destructive"
            : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      />
      {unitLabel && (
        <span className="text-[11px] font-medium text-muted-foreground select-none">
          {unitLabel}
        </span>
      )}
    </div>
  );
}
