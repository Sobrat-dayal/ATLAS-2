"use client";

import React, { useMemo, useRef, useState, useEffect } from "react";
import { Check, ChevronDown, Search, X } from "lucide-react";

export interface EnumOption {
  value: string;
  label: string;
  count?: number;
}

interface EnumFilterSelectProps {
  value: string; // comma-separated or single value
  isMulti?: boolean;
  options: EnumOption[];
  onChange: (val: string) => void;
  placeholder?: string;
  disabled?: boolean;
  hasError?: boolean;
}

export function EnumFilterSelect({
  value,
  isMulti = true,
  options,
  onChange,
  placeholder = "Select options...",
  disabled = false,
  hasError = false,
}: EnumFilterSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const popoverRef = useRef<HTMLDivElement>(null);

  const selectedValues = useMemo(() => {
    if (!value || !value.trim()) return [];
    return value
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }, [value]);

  const filteredOptions = useMemo(() => {
    if (!searchTerm.trim()) return options;
    const term = searchTerm.toLowerCase();
    return options.filter(
      (opt) =>
        opt.label.toLowerCase().includes(term) || opt.value.toLowerCase().includes(term)
    );
  }, [options, searchTerm]);

  // Click outside listener
  useEffect(() => {
    function handleClickOutside(evt: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(evt.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const toggleOption = (optVal: string) => {
    if (isMulti) {
      const next = selectedValues.includes(optVal)
        ? selectedValues.filter((v) => v !== optVal)
        : [...selectedValues, optVal];
      onChange(next.join(", "));
    } else {
      onChange(optVal);
      setIsOpen(false);
    }
  };

  const clearSelection = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange("");
  };

  return (
    <div className="relative inline-block" ref={popoverRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        className={`flex h-7 min-w-36 max-w-64 items-center justify-between gap-1.5 rounded border bg-background/80 px-2 text-xs transition-colors focus:outline-none focus:ring-1 ${
          hasError
            ? "border-destructive/80 focus:ring-destructive"
            : "border-border/60 hover:border-border focus:border-primary focus:ring-primary/40"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <span className="truncate text-left font-mono">
          {selectedValues.length === 0 ? (
            <span className="text-muted-foreground">{placeholder}</span>
          ) : selectedValues.length === 1 ? (
            options.find((o) => o.value === selectedValues[0])?.label || selectedValues[0]
          ) : (
            <span className="inline-flex items-center gap-1 font-medium text-foreground">
              {selectedValues.length} selected
            </span>
          )}
        </span>

        <div className="flex items-center gap-1 text-muted-foreground">
          {selectedValues.length > 0 && !disabled && (
            <span
              onClick={clearSelection}
              role="button"
              tabIndex={0}
              aria-label="Clear selection"
              className="rounded p-0.5 hover:bg-muted hover:text-foreground"
            >
              <X className="h-3 w-3" />
            </span>
          )}
          <ChevronDown className={`h-3 w-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </div>
      </button>

      {/* Popover Dropdown */}
      {isOpen && (
        <div className="absolute left-0 top-full z-50 mt-1 max-h-60 w-56 overflow-hidden rounded-md border border-border bg-popover text-popover-foreground shadow-lg animate-in fade-in-0 zoom-in-95">
          {/* Search inside */}
          <div className="flex items-center border-b border-border/50 px-2 py-1.5">
            <Search className="mr-1.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search options..."
              aria-label="Search filter options"
              className="w-full bg-transparent text-xs focus:outline-none"
              autoFocus
            />
          </div>

          {/* Options List */}
          <div className="max-h-48 overflow-y-auto p-1 text-xs">
            {filteredOptions.length === 0 ? (
              <div className="py-2 text-center text-[11px] text-muted-foreground">
                No matching options
              </div>
            ) : (
              filteredOptions.map((opt) => {
                const isSelected = selectedValues.includes(opt.value);
                return (
                  <div
                    key={opt.value}
                    onClick={() => toggleOption(opt.value)}
                    role="option"
                    aria-selected={isSelected}
                    className={`flex cursor-pointer items-center justify-between rounded px-2 py-1.5 transition-colors ${
                      isSelected
                        ? "bg-primary/10 text-primary font-medium"
                        : "hover:bg-muted/70 text-foreground"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <div
                        className={`flex h-3.5 w-3.5 items-center justify-center rounded border text-[10px] ${
                          isSelected
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-border/80"
                        }`}
                      >
                        {isSelected && <Check className="h-2.5 w-2.5 stroke-[3]" />}
                      </div>
                      <span className="truncate">{opt.label}</span>
                    </div>
                    {opt.count !== undefined && (
                      <span className="ml-2 font-mono text-[10px] text-muted-foreground">
                        {opt.count}
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
