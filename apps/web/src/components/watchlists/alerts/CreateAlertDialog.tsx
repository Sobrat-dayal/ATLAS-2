"use client";

import React, { useMemo, useState } from "react";
import { AlertTriangle, Bell, Clock, HelpCircle, X } from "lucide-react";
import {
  AlertCapabilitiesResponse,
  AlertRuleType,
  CreateAlertPayload,
  QuoteMeasure,
  RecurrencePolicy,
  ReferenceMethodology,
} from "@/lib/watchlists/alerts/types";
import {
  formatConditionLabel,
  formatQuoteMeasure,
} from "@/lib/watchlists/alerts/formatting";
import { WatchlistItem } from "@/lib/watchlists/types";

interface CreateAlertDialogProps {
  isOpen: boolean;
  onClose: () => void;
  item: WatchlistItem | null;
  capabilities: AlertCapabilitiesResponse | null;
  onSubmit: (payload: CreateAlertPayload) => Promise<unknown>;
}

export function CreateAlertDialog({
  isOpen,
  onClose,
  item,
  capabilities,
  onSubmit,
}: CreateAlertDialogProps) {
  const [ruleType, setRuleType] = useState<AlertRuleType>("CROSSING_ABOVE");
  const [quoteMeasure, setQuoteMeasure] = useState<QuoteMeasure>("LAST");
  const [threshold, setThreshold] = useState<string>("");
  const [recurrence, setRecurrence] = useState<RecurrencePolicy>("RECURRING");
  const [cooldown, setCooldown] = useState<number>(300); // 5 min default
  const [referenceMethod, setReferenceMethod] =
    useState<ReferenceMethodology>("SESSION_PREVIOUS_CLOSE");
  const [expiresAt, setExpiresAt] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize threshold when item changes
  React.useEffect(() => {
    if (item?.last_price) {
      setThreshold(item.last_price);
    } else {
      setThreshold("");
    }
    setError(null);
  }, [item]);

  // Asset class allowed measures
  const allowedMeasures = useMemo(() => {
    if (!capabilities || !item) {
      return ["LAST", "BID", "ASK", "MID", "OPEN", "HIGH", "LOW", "CLOSE"] as QuoteMeasure[];
    }
    const ac = item.asset_class?.toLowerCase() || "equity";
    return capabilities.asset_class_measures[ac] || capabilities.supported_quote_measures;
  }, [capabilities, item]);

  const isPercentageRule =
    ruleType === "PERCENTAGE_CHANGE_ABOVE" ||
    ruleType === "PERCENTAGE_CHANGE_BELOW";

  const unit = isPercentageRule ? "%" : item?.quote_currency || item?.quote_unit || "USD";

  if (!isOpen || !item) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(threshold);
    if (isNaN(val)) {
      setError("Please enter a valid numeric threshold.");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const payload: CreateAlertPayload = {
        watchlist_item_id: item.id,
        instrument_entity_id: item.instrument_entity_id,
        market_series_identity: item.market_series_id || item.symbol,
        symbol: item.symbol,
        rule_type: ruleType,
        quote_measure: quoteMeasure,
        threshold_decimal: val,
        threshold_unit: unit,
        reference_methodology: isPercentageRule ? referenceMethod : null,
        recurrence_policy: recurrence,
        cooldown_seconds: recurrence === "RECURRING" ? cooldown : 0,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
        notes: notes.trim() || null,
      };

      await onSubmit(payload);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create alert";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-alert-title"
    >
      <div className="w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/80 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-sky-400" />
            <h2 id="create-alert-title" className="text-sm font-semibold text-zinc-100">
              Create Watchlist Alert
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-zinc-400 hover:text-zinc-200 rounded hover:bg-zinc-800 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Target Instrument & Live Observation Preview */}
          <div className="p-3 bg-zinc-900/50 border border-zinc-800 rounded space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-bold text-zinc-100 text-sm">{item.symbol}</span>
                <span className="ml-2 text-zinc-400">{item.display_name}</span>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold bg-zinc-800 text-zinc-300">
                {item.asset_class}
              </span>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-zinc-800/60 text-[11px]">
              <span className="text-zinc-400">Current Quote ({item.quote_measure || "LAST"}):</span>
              <div className="flex items-center gap-2">
                <span className="font-bold text-zinc-100">
                  {item.last_price ? `${item.last_price} ${item.quote_currency || "USD"}` : "N/A"}
                </span>
                <span
                  className={`px-1 py-0.2 rounded text-[9px] uppercase font-semibold ${
                    item.delivery_delay_status === "realtime"
                      ? "text-emerald-400 bg-emerald-950/60"
                      : "text-amber-400 bg-amber-950/60"
                  }`}
                >
                  {item.delivery_delay_status || "Standard"}
                </span>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-2.5 bg-rose-950/50 border border-rose-800 rounded text-rose-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Condition & Measure Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Condition Type
              </label>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value as AlertRuleType)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                <option value="CROSSING_ABOVE">{formatConditionLabel("CROSSING_ABOVE")}</option>
                <option value="CROSSING_BELOW">{formatConditionLabel("CROSSING_BELOW")}</option>
                <option value="PRICE_ABOVE">{formatConditionLabel("PRICE_ABOVE")}</option>
                <option value="PRICE_BELOW">{formatConditionLabel("PRICE_BELOW")}</option>
                <option value="PERCENTAGE_CHANGE_ABOVE">
                  {formatConditionLabel("PERCENTAGE_CHANGE_ABOVE")}
                </option>
                <option value="PERCENTAGE_CHANGE_BELOW">
                  {formatConditionLabel("PERCENTAGE_CHANGE_BELOW")}
                </option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Quote Measure
              </label>
              <select
                value={quoteMeasure}
                onChange={(e) => setQuoteMeasure(e.target.value as QuoteMeasure)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                {allowedMeasures.map((m) => (
                  <option key={m} value={m}>
                    {formatQuoteMeasure(m)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Reference methodology (for percentage rules) */}
          {isPercentageRule && (
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Reference Methodology
              </label>
              <select
                value={referenceMethod}
                onChange={(e) => setReferenceMethod(e.target.value as ReferenceMethodology)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                <option value="SESSION_PREVIOUS_CLOSE">Session Previous Close</option>
                <option value="ROLLING_24H">Rolling 24-Hour Benchmark</option>
                <option value="PREVIOUS_NAV">Previous NAV Valuation</option>
              </select>
            </div>
          )}

          {/* Threshold & Unit */}
          <div>
            <label className="block text-[11px] font-medium text-zinc-400 mb-1">
              Threshold ({unit})
            </label>
            <div className="relative">
              <input
                type="number"
                step="any"
                required
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                placeholder={isPercentageRule ? "e.g. 5.0" : "e.g. 185.50"}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-sky-500"
              />
              <span className="absolute right-2.5 top-1.5 text-zinc-400 text-[11px]">
                {unit}
              </span>
            </div>
          </div>

          {/* Recurrence & Cooldown */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Recurrence Policy
              </label>
              <select
                value={recurrence}
                onChange={(e) => setRecurrence(e.target.value as RecurrencePolicy)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                <option value="RECURRING">Recurring (Re-arms on move)</option>
                <option value="ONE_SHOT">One-Shot (Auto-Disables)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Cooldown Window
              </label>
              <select
                disabled={recurrence === "ONE_SHOT"}
                value={cooldown}
                onChange={(e) => setCooldown(parseInt(e.target.value, 10))}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500 disabled:opacity-40"
              >
                <option value={0}>None (Instant Re-Arm)</option>
                <option value={60}>1 Minute</option>
                <option value={300}>5 Minutes</option>
                <option value={900}>15 Minutes</option>
                <option value={3600}>1 Hour</option>
                <option value={86400}>1 Day</option>
              </select>
            </div>
          </div>

          {/* Optional Expiration */}
          <div>
            <label className="block text-[11px] font-medium text-zinc-400 mb-1 flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-400" />
              <span>Optional Expiration (UTC)</span>
            </label>
            <input
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Financial Semantics Note */}
          <div className="p-2.5 bg-zinc-900/40 border border-zinc-800 rounded flex items-start gap-2 text-[10px] text-zinc-400">
            <HelpCircle className="w-3.5 h-3.5 mt-0.5 text-sky-400 shrink-0" />
            <span>
              Crossing alerts establish a genuine market baseline before arming. If current
              quote is already across threshold, it will not trigger a false alert until
              price transitions from the opposite side.
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-1.5 rounded bg-sky-600 text-white font-medium hover:bg-sky-500 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Bell className="w-3.5 h-3.5" />
              <span>{submitting ? "Creating..." : "Arm Alert"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
