"use client";

import React, { useState, useEffect } from "react";
import {
  CreateNewsMonitoringRuleDTO,
  NewsAlertPriority,
  NewsDeliveryChannel,
  NewsFinancialAspect,
  NewsMonitoringRuleDTO,
  NewsMonitoringRuleType,
  NewsRulePreviewResponseDTO,
  NewsRuleValidationResponseDTO,
  NewsSentimentLabel,
  NewsTriggerPolicy,
} from "@/lib/news/types";
import {
  X,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Save,
  Clock,
  Sparkles,
  ShieldCheck,
  Building2,
  Bell,
} from "lucide-react";

interface RuleBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveRule: (dto: CreateNewsMonitoringRuleDTO) => Promise<unknown>;
  onValidateRule: (dto: CreateNewsMonitoringRuleDTO) => Promise<NewsRuleValidationResponseDTO>;
  onPreviewRule: (dto: CreateNewsMonitoringRuleDTO) => Promise<NewsRulePreviewResponseDTO>;
  initialRule?: NewsMonitoringRuleDTO | null;
}

export function RuleBuilderModal({
  isOpen,
  onClose,
  onSaveRule,
  onValidateRule,
  onPreviewRule,
  initialRule,
}: RuleBuilderModalProps) {
  // Form State
  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [ruleType, setRuleType] = useState<NewsMonitoringRuleType>("COMPANY");
  const [targetTickers, setTargetTickers] = useState<string>("");
  const [targetTopics, setTargetTopics] = useState<string>("");
  const [targetPublishers, setTargetPublishers] = useState<string>("");
  const [targetEventTypes, setTargetEventTypes] = useState<string>("");
  const [priority, setPriority] = useState<NewsAlertPriority>("HIGH");
  const [triggerPolicy, setTriggerPolicy] = useState<NewsTriggerPolicy>("ON_NEW_ARTICLE");
  const [deliveryChannels, setDeliveryChannels] = useState<NewsDeliveryChannel[]>([
    "IN_APP",
    "DURABLE_NOTIFICATION",
  ]);
  const [cooldownMinutes, setCooldownMinutes] = useState<number>(30);
  const [quietHoursEnabled, setQuietHoursEnabled] = useState<boolean>(false);
  const [quietHoursStartUtc, setQuietHoursStartUtc] = useState<string>("22:00");
  const [quietHoursEndUtc, setQuietHoursEndUtc] = useState<string>("06:00");

  // Sentiment Condition
  const [enableSentiment, setEnableSentiment] = useState<boolean>(false);
  const [sentimentLabel, setSentimentLabel] = useState<NewsSentimentLabel>("POSITIVE");
  const [sentimentMinScore, setSentimentMinScore] = useState<number>(0.5);
  const [sentimentAspect, setSentimentAspect] = useState<NewsFinancialAspect>("EARNINGS_PERFORMANCE");

  // Live Validation & Preview States
  const [validation, setValidation] = useState<NewsRuleValidationResponseDTO | null>(null);
  const [preview, setPreview] = useState<NewsRulePreviewResponseDTO | null>(null);
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [isPreviewing, setIsPreviewing] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [activePreviewTab, setActivePreviewTab] = useState<"FORM" | "PREVIEW">("FORM");

  // Sync initial rule if editing
  useEffect(() => {
    if (initialRule) {
      setName(initialRule.name);
      setDescription(initialRule.description || "");
      setRuleType(initialRule.rule_type);
      setTargetTickers(initialRule.target_tickers?.join(", ") || "");
      setTargetTopics(initialRule.target_topic_ids?.join(", ") || "");
      setTargetPublishers(initialRule.target_publisher_ids?.join(", ") || "");
      setTargetEventTypes(initialRule.target_event_types?.join(", ") || "");
      setPriority(initialRule.priority);
      setTriggerPolicy(initialRule.trigger_policy);
      setDeliveryChannels(initialRule.delivery_channels || ["IN_APP"]);
      setCooldownMinutes(initialRule.cooldown_minutes || 30);
      setQuietHoursEnabled(initialRule.quiet_hours_enabled || false);
      setQuietHoursStartUtc(initialRule.quiet_hours_start_utc || "22:00");
      setQuietHoursEndUtc(initialRule.quiet_hours_end_utc || "06:00");
      if (initialRule.sentiment_condition) {
        setEnableSentiment(true);
        setSentimentLabel(initialRule.sentiment_condition.sentiment_label);
        setSentimentMinScore(initialRule.sentiment_condition.min_score ?? 0.5);
        if (initialRule.sentiment_condition.aspect) {
          setSentimentAspect(initialRule.sentiment_condition.aspect);
        }
      } else {
        setEnableSentiment(false);
      }
    } else {
      // Default new rule
      setName("");
      setDescription("");
      setRuleType("COMPANY");
      setTargetTickers("AAPL, MSFT");
      setTargetTopics("");
      setTargetPublishers("");
      setTargetEventTypes("");
      setPriority("HIGH");
      setTriggerPolicy("ON_NEW_ARTICLE");
      setDeliveryChannels(["IN_APP", "DURABLE_NOTIFICATION"]);
      setCooldownMinutes(30);
      setQuietHoursEnabled(false);
      setEnableSentiment(false);
    }
    setPreview(null);
    setActivePreviewTab("FORM");
  }, [initialRule, isOpen]);

  // Construct current DTO
  const buildCurrentDto = (): CreateNewsMonitoringRuleDTO => {
    const parseList = (str: string) =>
      str
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

    return {
      name: name || "Draft Rule",
      description: description || null,
      rule_type: ruleType,
      target_tickers: parseList(targetTickers),
      target_topic_ids: parseList(targetTopics),
      target_publisher_ids: parseList(targetPublishers),
      target_event_types: parseList(targetEventTypes),
      priority,
      trigger_policy: triggerPolicy,
      delivery_channels: deliveryChannels,
      cooldown_minutes: cooldownMinutes,
      quiet_hours_enabled: quietHoursEnabled,
      quiet_hours_start_utc: quietHoursEnabled ? quietHoursStartUtc : null,
      quiet_hours_end_utc: quietHoursEnabled ? quietHoursEndUtc : null,
      sentiment_condition: enableSentiment
        ? {
            sentiment_label: sentimentLabel,
            min_score: sentimentMinScore,
            aspect: sentimentAspect,
          }
        : null,
    };
  };

  // Debounced live validation
  useEffect(() => {
    if (!isOpen) return;
    const timer = setTimeout(async () => {
      setIsValidating(true);
      try {
        const dto = buildCurrentDto();
        const res = await onValidateRule(dto);
        setValidation(res);
      } catch {
        // Non-blocking validation error
      } finally {
        setIsValidating(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [
    name,
    ruleType,
    targetTickers,
    targetTopics,
    targetPublishers,
    targetEventTypes,
    enableSentiment,
    sentimentLabel,
    sentimentMinScore,
    sentimentAspect,
    isOpen,
  ]);

  const handleRunPreview = async () => {
    setIsPreviewing(true);
    try {
      const dto = buildCurrentDto();
      const res = await onPreviewRule(dto);
      setPreview(res);
      setActivePreviewTab("PREVIEW");
    } catch {
      // preview error
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSaving(true);
    try {
      const dto = buildCurrentDto();
      await onSaveRule(dto);
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  const toggleChannel = (channel: NewsDeliveryChannel) => {
    setDeliveryChannels((prev) =>
      prev.includes(channel) ? prev.filter((c) => c !== channel) : [...prev, channel]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto font-mono text-xs">
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4 text-cyan-500" />
            <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 uppercase tracking-wide">
              {initialRule ? `Edit Rule: ${initialRule.name}` : "Configure New News Monitoring Rule"}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Toggle: Form vs Preview */}
        <div className="flex border-b border-zinc-200 dark:border-zinc-800 px-4 bg-zinc-50/50 dark:bg-zinc-950/50">
          <button
            onClick={() => setActivePreviewTab("FORM")}
            className={`py-2 px-3 font-semibold border-b-2 transition-colors ${
              activePreviewTab === "FORM"
                ? "border-cyan-500 text-cyan-600 dark:text-cyan-400"
                : "border-transparent text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            Configuration
          </button>
          <button
            onClick={() => setActivePreviewTab("PREVIEW")}
            className={`py-2 px-3 font-semibold border-b-2 flex items-center space-x-1.5 transition-colors ${
              activePreviewTab === "PREVIEW"
                ? "border-cyan-500 text-cyan-600 dark:text-cyan-400"
                : "border-transparent text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Historical Preview</span>
            {preview && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full bg-cyan-500/20 text-cyan-500 text-[10px]">
                {preview.preview_sample_articles.length}
              </span>
            )}
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto flex-1 space-y-4">
          {activePreviewTab === "FORM" ? (
            <form id="rule-builder-form" onSubmit={handleSave} className="space-y-4">
              {/* Validation Status Banner */}
              {validation && (
                <div
                  className={`p-2.5 rounded border flex items-start space-x-2 ${
                    validation.is_valid
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-600 dark:text-rose-400"
                  }`}
                >
                  {validation.is_valid ? (
                    <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                  )}
                  <div className="space-y-0.5">
                    <p className="font-semibold">
                      {validation.is_valid ? "Rule Definition Valid" : "Rule Validation Incomplete"}
                    </p>
                    {validation.validation_errors.map((err, i) => (
                      <p key={i} className="text-[11px] opacity-90">
                        • {err}
                      </p>
                    ))}
                    {validation.validation_warnings.map((warn, i) => (
                      <p key={i} className="text-[11px] text-amber-500">
                        ⚠ {warn}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Name & Description */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Rule Name *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Magnificent 7 Cloud & AI Alerts"
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 focus:outline-hidden focus:border-cyan-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Rule Type
                  </label>
                  <select
                    value={ruleType}
                    onChange={(e) => setRuleType(e.target.value as NewsMonitoringRuleType)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 focus:outline-hidden focus:border-cyan-500"
                  >
                    <option value="COMPANY">COMPANY (By Ticker or Entity ID)</option>
                    <option value="INSTRUMENT">INSTRUMENT (Financial Asset)</option>
                    <option value="TOPIC">TOPIC (Industry / Macro Topic)</option>
                    <option value="PUBLISHER">PUBLISHER (Specific Wire / News Outlet)</option>
                    <option value="EVENT_TYPE">EVENT_TYPE (Financial Event Classification)</option>
                    <option value="COMPOSITE">COMPOSITE (Multi-Condition Compound)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                  Description (Optional)
                </label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Rationale or operational purpose for quantitative alerting"
                  className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 focus:outline-hidden focus:border-cyan-500"
                />
              </div>

              {/* Targets */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50">
                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Target Tickers (Comma separated)
                  </label>
                  <input
                    type="text"
                    value={targetTickers}
                    onChange={(e) => setTargetTickers(e.target.value)}
                    placeholder="AAPL, MSFT, NVDA"
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Target Topics (Comma separated)
                  </label>
                  <input
                    type="text"
                    value={targetTopics}
                    onChange={(e) => setTargetTopics(e.target.value)}
                    placeholder="cloud-computing, artificial-intelligence"
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Target Event Types
                  </label>
                  <input
                    type="text"
                    value={targetEventTypes}
                    onChange={(e) => setTargetEventTypes(e.target.value)}
                    placeholder="EARNINGS_RELEASE, MERGER_ACQUISITION, DIVIDEND_DECLARATION"
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Target Publishers
                  </label>
                  <input
                    type="text"
                    value={targetPublishers}
                    onChange={(e) => setTargetPublishers(e.target.value)}
                    placeholder="reuters, bloomberg_wire, prnewswire"
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>
              </div>

              {/* Sentiment Condition Section */}
              <div className="p-3 rounded border border-purple-200 dark:border-purple-900/50 bg-purple-50/20 dark:bg-purple-950/20 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                    <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                      Target-Aware Financial Sentiment Filter
                    </span>
                  </div>
                  <input
                    type="checkbox"
                    checked={enableSentiment}
                    onChange={(e) => setEnableSentiment(e.target.checked)}
                    className="rounded text-purple-600 focus:ring-purple-500"
                  />
                </div>

                {enableSentiment && (
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-purple-200/50 dark:border-purple-900/30">
                    <div>
                      <label className="block text-[11px] text-zinc-600 dark:text-zinc-400 mb-0.5">
                        Required Polarity
                      </label>
                      <select
                        value={sentimentLabel}
                        onChange={(e) => setSentimentLabel(e.target.value as NewsSentimentLabel)}
                        className="w-full px-2 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                      >
                        <option value="POSITIVE">POSITIVE</option>
                        <option value="NEGATIVE">NEGATIVE</option>
                        <option value="NEUTRAL">NEUTRAL</option>
                        <option value="MIXED">MIXED</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] text-zinc-600 dark:text-zinc-400 mb-0.5">
                        Financial Aspect
                      </label>
                      <select
                        value={sentimentAspect}
                        onChange={(e) => setSentimentAspect(e.target.value as NewsFinancialAspect)}
                        className="w-full px-2 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                      >
                        <option value="EARNINGS_PERFORMANCE">EARNINGS_PERFORMANCE</option>
                        <option value="REVENUE_GROWTH">REVENUE_GROWTH</option>
                        <option value="PROFITABILITY">PROFITABILITY</option>
                        <option value="REGULATORY_EXPOSURE">REGULATORY_EXPOSURE</option>
                        <option value="GENERAL">GENERAL</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] text-zinc-600 dark:text-zinc-400 mb-0.5">
                        Min Confidence / Score
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.05"
                        value={sentimentMinScore}
                        onChange={(e) => setSentimentMinScore(parseFloat(e.target.value))}
                        className="w-full px-2 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Policy, Priority, Cooldown & Delivery */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Priority
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as NewsAlertPriority)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  >
                    <option value="CRITICAL">CRITICAL (Instant alert)</option>
                    <option value="HIGH">HIGH (Standard high priority)</option>
                    <option value="MEDIUM">MEDIUM (Normal dispatch)</option>
                    <option value="LOW">LOW (Digest eligible only)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Trigger Policy
                  </label>
                  <select
                    value={triggerPolicy}
                    onChange={(e) => setTriggerPolicy(e.target.value as NewsTriggerPolicy)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  >
                    <option value="ON_NEW_ARTICLE">ON_NEW_ARTICLE</option>
                    <option value="ON_EVENT_VERIFIED">ON_EVENT_VERIFIED</option>
                    <option value="ON_SENTIMENT_CHANGE">ON_SENTIMENT_CHANGE</option>
                    <option value="BATCH_HOURLY">BATCH_HOURLY</option>
                    <option value="SCHEDULED_DIGEST_ONLY">SCHEDULED_DIGEST_ONLY</option>
                  </select>
                </div>

                <div>
                  <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                    Cooldown (Minutes)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="1440"
                    value={cooldownMinutes}
                    onChange={(e) => setCooldownMinutes(parseInt(e.target.value) || 5)}
                    className="w-full px-2.5 py-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950"
                  />
                </div>
              </div>

              {/* Delivery Channels */}
              <div>
                <label className="block text-zinc-700 dark:text-zinc-300 font-semibold mb-1">
                  Delivery Channels
                </label>
                <div className="flex flex-wrap gap-3">
                  {(["IN_APP", "DURABLE_NOTIFICATION", "EMAIL", "DIGEST"] as NewsDeliveryChannel[]).map(
                    (ch) => (
                      <label key={ch} className="flex items-center space-x-1.5 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={deliveryChannels.includes(ch)}
                          onChange={() => toggleChannel(ch)}
                          className="rounded text-cyan-600 focus:ring-cyan-500"
                        />
                        <span className="text-zinc-700 dark:text-zinc-300">{ch}</span>
                      </label>
                    )
                  )}
                </div>
              </div>

              {/* Quiet Hours */}
              <div className="flex items-center space-x-3 p-2.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50">
                <input
                  type="checkbox"
                  id="qh-toggle"
                  checked={quietHoursEnabled}
                  onChange={(e) => setQuietHoursEnabled(e.target.checked)}
                  className="rounded text-cyan-600"
                />
                <label htmlFor="qh-toggle" className="text-zinc-700 dark:text-zinc-300 font-semibold">
                  Enable Quiet Hours Suppression (UTC)
                </label>
                {quietHoursEnabled && (
                  <div className="flex items-center space-x-1 ml-auto">
                    <input
                      type="time"
                      value={quietHoursStartUtc}
                      onChange={(e) => setQuietHoursStartUtc(e.target.value)}
                      className="px-2 py-0.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                    />
                    <span>to</span>
                    <input
                      type="time"
                      value={quietHoursEndUtc}
                      onChange={(e) => setQuietHoursEndUtc(e.target.value)}
                      className="px-2 py-0.5 rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900"
                    />
                  </div>
                )}
              </div>
            </form>
          ) : (
            /* Historical Preview Tab */
            <div className="space-y-4">
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded text-amber-700 dark:text-amber-400 text-xs">
                <strong>Non-Retroactive Bounded Preview:</strong> {preview?.disclaimer ||
                  "Historical rule preview is bounded and non-retroactive; no retroactive alert notifications are generated."}
              </div>

              {preview ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2.5 rounded bg-zinc-100 dark:bg-zinc-800">
                    <span>
                      Estimated Weekly Matches:{" "}
                      <strong>{preview.estimated_matching_volume_per_week}</strong>
                    </span>
                    <span>
                      Sample Articles:{" "}
                      <strong>{preview.preview_sample_articles.length}</strong>
                    </span>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">
                      Sample Matching Articles
                    </h4>
                    {preview.preview_sample_articles.length === 0 ? (
                      <p className="text-zinc-500">No matching sample articles found.</p>
                    ) : (
                      preview.preview_sample_articles.map((art) => (
                        <div
                          key={art.article_id}
                          className="p-2.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 space-y-1"
                        >
                          <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                            {art.headline}
                          </div>
                          <div className="text-[11px] text-zinc-500 flex items-center space-x-2">
                            <span>{art.publisher_name}</span>
                            <span>•</span>
                            <span>{art.published_at}</span>
                          </div>
                          {art.permitted_excerpt && (
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 line-clamp-2">
                              {art.permitted_excerpt}
                            </p>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-zinc-500 space-y-2">
                  <p>Click below to compute a bounded historical match preview.</p>
                  <button
                    type="button"
                    onClick={handleRunPreview}
                    disabled={isPreviewing}
                    className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded bg-cyan-600 text-white font-semibold"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>{isPreviewing ? "Computing..." : "Run Preview"}</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50 dark:bg-zinc-950">
          <button
            type="button"
            onClick={handleRunPreview}
            disabled={isPreviewing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 hover:bg-zinc-100 dark:hover:bg-zinc-800 font-semibold transition-colors"
          >
            <Eye className="w-3.5 h-3.5 text-cyan-500" />
            <span>{isPreviewing ? "Evaluating..." : "Preview Matches"}</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="rule-builder-form"
              disabled={Boolean(isSaving || (validation && !validation.is_valid))}
              className="flex items-center space-x-1.5 px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition-colors disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{isSaving ? "Saving..." : initialRule ? "Update Rule" : "Create Rule"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
