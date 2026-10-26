"use client";

import React from "react";

interface DecimalFilterInputProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  disabled?: boolean;
  hasError?: boolean;
  unitLabel?: string;
  min?: number | null;
  max?: number | null;
  ariaLabel?: string;
}

export function DecimalFilterInput({
  value,
  onChange,
  placeholder = "0.00",
  disabled = false,
  hasError = false,
  unitLabel,
  ariaLabel = "Numeric value",
}: DecimalFilterInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    // Allow empty, negative sign, decimal point, digits, intermediate typing states
    if (raw === "" || /^[-+]?([0-9]*\.?[0-9]*)?$/.test(raw)) {
      onChange(raw);
    }
  };

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
        className={`h-7 w-28 rounded border bg-background/80 px-2 text-xs font-mono transition-colors focus:outline-none focus:ring-1 ${
          hasError
            ? "border-destructive/80 focus:ring-destructive"
            : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      />
      {unitLabel && (
        <span className="ml-1.5 text-[11px] font-medium text-muted-foreground select-none">
          {unitLabel}
        </span>
      )}
    </div>
  );
}
