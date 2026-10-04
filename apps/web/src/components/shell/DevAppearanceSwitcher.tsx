"use client";

import { useState, useRef, useEffect } from "react";
import { useAppearance, AtlasTheme, AtlasDensity, AtlasAccent } from "@/hooks/appearance";
import { Palette, X } from "lucide-react";

export function DevAppearanceSwitcher() {
  const { theme, setTheme, density, setDensity, accent, setAccent, resetAppearance } = useAppearance();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  if (process.env.NODE_ENV === "production") {
    // Hidden in production, wait for Stage 9 Settings UI
    return null; 
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex h-6 w-6 items-center justify-center rounded-sm text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
        title="Dev Appearance Preview"
      >
        <Palette className="h-3.5 w-3.5" />
      </button>

      {open && (
        <div className="absolute right-0 top-8 z-50 w-64 rounded-md border border-atlas-border-default bg-atlas-surface-1 p-3 shadow-xl">
          <div className="mb-3 flex items-center justify-between border-b border-atlas-border-default pb-2">
            <h3 className="text-xs font-semibold uppercase text-atlas-text-primary">Dev Appearance</h3>
            <button onClick={() => setOpen(false)} className="text-atlas-text-muted hover:text-atlas-text-primary">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-atlas-text-secondary">Theme</label>
              <div className="grid grid-cols-2 gap-1.5">
                {(["system", "dark", "light", "terminal"] as AtlasTheme[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`rounded-sm px-2 py-1 text-xs capitalize transition-colors ${
                      theme === t ? "bg-atlas-surface-selected text-atlas-accent" : "bg-atlas-surface-2 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-medium text-atlas-text-secondary">Density</label>
              <div className="grid grid-cols-3 gap-1.5">
                {(["compact", "default", "comfortable"] as AtlasDensity[]).map((d) => (
                  <button
                    key={d}
                    onClick={() => setDensity(d)}
                    className={`rounded-sm px-2 py-1 text-[10px] capitalize transition-colors ${
                      density === d ? "bg-atlas-surface-selected text-atlas-accent" : "bg-atlas-surface-2 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-medium text-atlas-text-secondary">Accent</label>
              <div className="grid grid-cols-2 gap-1.5">
                {(["blue", "cyan", "emerald", "amber"] as AtlasAccent[]).map((a) => (
                  <button
                    key={a}
                    onClick={() => setAccent(a)}
                    className={`rounded-sm px-2 py-1 text-xs capitalize transition-colors flex items-center gap-1.5 ${
                      accent === a ? "bg-atlas-surface-selected text-atlas-text-primary" : "bg-atlas-surface-2 text-atlas-text-muted hover:bg-atlas-surface-hover"
                    }`}
                  >
                    <div 
                      className="h-2 w-2 rounded-full" 
                      style={{ 
                        backgroundColor: a === 'blue' ? 'var(--atlas-accent)' : 
                                         a === 'cyan' ? '#18BCEB' : 
                                         a === 'emerald' ? '#10B981' : '#F59E0B'
                      }}
                    />
                    {a}
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-atlas-border-default pt-3">
              <button
                onClick={resetAppearance}
                className="w-full rounded-sm bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
              >
                Reset to Defaults
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
