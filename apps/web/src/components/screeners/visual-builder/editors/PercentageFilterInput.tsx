"use client";

import React from "react";

interface PercentageFilterInputProps {
  value: string;
  onChange: (val: string) => void;
  unitKind?: "percent" | "multiple" | string;
  placeholder?: string;
  disabled?: boolean;
  hasError?: boolean;
  ariaLabel?: string;
}

export function PercentageFilterInput({
  value,
  onChange,
  unitKind = "percent",
  placeholder = "0.0",
  disabled = false,
  hasError = false,
  ariaLabel = "Rate or multiple value",
}: PercentageFilterInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "" || /^[-+]?([0-9]*\.?[0-9]*)?$/.test(raw)) {
      onChange(raw);
    }
  };

  const suffix = unitKind === "multiple" ? "x" : "%";

  return (
    <div className="relative flex items-center">
      <input
        type="text"
        inputMode="decimal"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        aria-label={ariaLabel}
        className={`h-7 w-20 rounded-l border bg-background/80 px-2 text-xs font-mono transition-colors focus:outline-none focus:ring-1 ${
          hasError
            ? "border-destructive/80 focus:ring-destructive"
            : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      />
      <div className="flex h-7 items-center justify-center rounded-r border border-l-0 border-border/60 bg-muted/40 px-2 text-xs font-mono font-medium text-muted-foreground select-none">
        {suffix}
      </div>
    </div>
  );
}
