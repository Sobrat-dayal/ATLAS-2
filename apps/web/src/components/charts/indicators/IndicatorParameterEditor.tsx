"use client";

/**
 * Indicator Parameter Editor Dialog Component (Stage 69).
 *
 * Allows users to edit calculation parameters, stroke colors, and line widths
 * for an active technical indicator instance with inline authoritative validation.
 */

import React, { useState } from "react";
import { Check, Sliders, X } from "lucide-react";
import {
  IndicatorDefinition,
  IndicatorInstanceConfig,
} from "@/lib/charts";

const COLOR_OPTIONS = [
  "#38bdf8", // Sky 400
  "#10b981", // Emerald 500
  "#f59e0b", // Amber 500
  "#ef4444", // Red 500
  "#ec4899", // Pink 500
  "#a855f7", // Purple 500
  "#e2e8f0", // Slate 200
  "#eab308", // Yellow 500
];

export interface IndicatorParameterEditorProps {
  isOpen: boolean;
  onClose: () => void;
  instance: IndicatorInstanceConfig | null;
  definition: IndicatorDefinition | null | undefined;
  onSave: (
    instanceId: string,
    updates: {
      parameters: Record<string, unknown>;
      color?: string | null;
      line_width?: number | null;
    }
  ) => void;
}

export function IndicatorParameterEditor({
  isOpen,
  onClose,
  instance,
  definition,
  onSave,
}: IndicatorParameterEditorProps) {
  if (!isOpen || !instance || !definition) return null;

  return (
    <EditorContent
      instance={instance}
      definition={definition}
      onClose={onClose}
      onSave={onSave}
    />
  );
}

function EditorContent({
  instance,
  definition,
  onClose,
  onSave,
}: {
  instance: IndicatorInstanceConfig;
  definition: IndicatorDefinition;
  onClose: () => void;
  onSave: IndicatorParameterEditorProps["onSave"];
}) {
  const [params, setParams] = useState<Record<string, unknown>>({
    ...instance.parameters,
  });
  const [color, setColor] = useState<string>(instance.color || definition.default_color);
  const [lineWidth, setLineWidth] = useState<number>(instance.line_width || 2);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleParamChange = (name: string, value: unknown, min?: number | null, max?: number | null) => {
    const updated = { ...params, [name]: value };
    setParams(updated);

    const newErrors = { ...errors };
    if (typeof value === "number") {
      if (min != null && value < min) {
        newErrors[name] = `Value must be at least ${min}`;
      } else if (max != null && value > max) {
        newErrors[name] = `Value must be at most ${max}`;
      } else {
        delete newErrors[name];
      }
    } else {
      delete newErrors[name];
    }
    setErrors(newErrors);
  };

  const hasErrors = Object.keys(errors).length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hasErrors) return;

    onSave(instance.instance_id, {
      parameters: params,
      color,
      line_width: lineWidth,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div
        className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden text-zinc-100 font-sans"
        role="dialog"
        aria-modal="true"
        aria-label={`Configure ${definition.display_name}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/80 bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100 font-mono">
              {definition.display_name.toUpperCase()} SETTINGS
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-100 p-1 rounded hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4 text-xs">
          {/* Dynamic Parameters */}
          <div className="space-y-3">
            <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-400 font-semibold border-b border-zinc-800 pb-1">
              Calculation Parameters
            </div>

            {definition.parameters.map((p) => {
              const currentVal = params[p.name] ?? p.default;
              const error = errors[p.name];

              return (
                <div key={p.name} className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <label htmlFor={`param-${p.name}`} className="font-mono text-zinc-300 capitalize">
                      {p.name}
                    </label>
                    {p.min_value != null && p.max_value != null && (
                      <span className="text-[10px] text-zinc-500 font-mono">
                        ({p.min_value} - {p.max_value})
                      </span>
                    )}
                  </div>

                  {p.type === "INTEGER" || p.type === "DECIMAL" ? (
                    <input
                      id={`param-${p.name}`}
                      type="number"
                      step={p.type === "INTEGER" ? "1" : "any"}
                      min={p.min_value ?? undefined}
                      max={p.max_value ?? undefined}
                      value={typeof currentVal === "number" ? currentVal : ""}
                      onChange={(e) =>
                        handleParamChange(
                          p.name,
                          p.type === "INTEGER" ? parseInt(e.target.value, 10) : parseFloat(e.target.value),
                          p.min_value,
                          p.max_value
                        )
                      }
                      className={`w-full px-2.5 py-1.5 bg-zinc-900 border rounded font-mono text-zinc-100 focus:outline-none ${
                        error
                          ? "border-rose-500 focus:border-rose-400"
                          : "border-zinc-800 focus:border-cyan-500"
                      }`}
                    />
                  ) : p.type === "STRING" && p.allowed_values ? (
                    <select
                      id={`param-${p.name}`}
                      value={String(currentVal)}
                      onChange={(e) => handleParamChange(p.name, e.target.value)}
                      className="w-full px-2.5 py-1.5 bg-zinc-900 border border-zinc-800 rounded font-mono text-zinc-100 focus:outline-none focus:border-cyan-500"
                    >
                      {p.allowed_values.map((opt) => (
                        <option key={String(opt)} value={String(opt)}>
                          {String(opt)}
                        </option>
                      ))}
                    </select>
                  ) : null}

                  {error && <span className="text-[11px] text-rose-400 font-mono">{error}</span>}
                  {p.description && (
                    <span className="text-[10px] text-zinc-500">{p.description}</span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Visual Style Settings */}
          <div className="space-y-3 pt-2">
            <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-400 font-semibold border-b border-zinc-800 pb-1">
              Visual Appearance
            </div>

            {/* Color */}
            <div className="space-y-1.5">
              <label className="font-mono text-zinc-300">Stroke Color</label>
              <div className="flex flex-wrap items-center gap-2">
                {COLOR_OPTIONS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setColor(c)}
                    style={{ backgroundColor: c }}
                    className={`w-6 h-6 rounded-full border flex items-center justify-center transition-transform ${
                      color === c ? "border-white scale-110 shadow" : "border-transparent opacity-80 hover:opacity-100"
                    }`}
                    aria-label={`Select color ${c}`}
                  >
                    {color === c && <Check className="w-3.5 h-3.5 text-black stroke-[3]" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Line Width */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="font-mono text-zinc-300">Line Width</label>
                <span className="text-zinc-400 font-mono">{lineWidth}px</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={lineWidth}
                onChange={(e) => setLineWidth(parseInt(e.target.value, 10))}
                className="w-full accent-cyan-500 bg-zinc-800 h-1 rounded cursor-pointer"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-zinc-800 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded text-xs text-zinc-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={hasErrors}
              className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded text-xs font-medium font-mono transition-colors"
            >
              Apply Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
