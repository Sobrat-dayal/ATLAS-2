"use client";

import React, { useState } from "react";
import {
  AlertCircle,
  CornerDownLeft,
  Loader2,
  Sparkles,
  Terminal,
} from "lucide-react";
import {
  FilterCriterion,
  NLTranslationProposal,
  SortCriterion,
  UniverseSelection,
} from "@/lib/screeners/types";
import { clarifyNLQuery, translateNLQuery } from "@/lib/screeners/api";
import { TranslationReviewPanel } from "./TranslationReviewPanel";

interface NaturalLanguageScreenerProps {
  onTransferToBuilder: (filters: FilterCriterion[], universe: UniverseSelection) => void;
  onApplyAndRun: (
    filters: FilterCriterion[],
    universe: UniverseSelection,
    sort: SortCriterion[]
  ) => void;
  currencyPolicy?: string;
}

const EXAMPLE_PROMPTS = [
  {
    title: "Indian Large-Cap Growth & Value",
    prompt:
      "Find large-cap Indian companies with revenue growth above 15%, positive free cash flow, P/E below 25 and a share price above the 200-day moving average.",
  },
  {
    title: "US Tech Leaders",
    prompt:
      "Find US technology companies with market cap over 50 billion USD, operating margin at least 25%, debt to equity below 0.8 and RSI below 60.",
  },
  {
    title: "European Cash Flow & Dividend",
    prompt:
      "Find European stocks with dividend yield above 4%, positive net income, and price above 50-day moving average.",
  },
  {
    title: "Indian Mid-Cap Range",
    prompt:
      "Find Indian stocks with market cap between 5000 crore and 20000 crore INR, revenue growth over 20% and relative volume above 1.5.",
  },
];

const MAX_CHARS = 1000;

export function NaturalLanguageScreener({
  onTransferToBuilder,
  onApplyAndRun,
  currencyPolicy = "USD",
}: NaturalLanguageScreenerProps) {
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [isClarifying, setIsClarifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [proposal, setProposal] = useState<NLTranslationProposal | null>(null);

  const handleTranslate = async (textToTranslate?: string) => {
    const q = (textToTranslate ?? inputText).trim();
    if (!q) {
      setError("Please describe your screening requirements in plain English.");
      return;
    }
    if (q.length > MAX_CHARS) {
      setError(`Request exceeds maximum allowed length of ${MAX_CHARS} characters.`);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await translateNLQuery({
        text: q,
        currency_policy: currencyPolicy,
      });
      setProposal(res);
    } catch (err: any) {
      setError(err?.message || "Failed to translate natural-language screening instructions.");
    } finally {
      setLoading(false);
    }
  };

  const handleClarify = async (ambiguityId: string, optionId: string) => {
    if (!proposal) return;
    setIsClarifying(true);
    setError(null);

    try {
      const res = await clarifyNLQuery({
        proposal_id: proposal.proposal_id,
        original_text: proposal.original_text,
        ambiguity_id: ambiguityId,
        selected_option_id: optionId,
      });
      setProposal(res);
    } catch (err: any) {
      setError(err?.message || "Failed to resolve ambiguity.");
    } finally {
      setIsClarifying(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleTranslate();
    }
  };

  const selectPrompt = (promptText: string) => {
    setInputText(promptText);
    handleTranslate(promptText);
  };

  const charCount = inputText.length;
  const isOverLimit = charCount > MAX_CHARS;

  return (
    <div className="flex flex-col gap-5 p-6 bg-background text-foreground">
      {/* Input Console Container */}
      <div className="flex flex-col gap-3 rounded-lg border border-border/80 bg-card p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary/10 text-primary border border-primary/20">
              <Terminal className="h-3.5 w-3.5" />
            </div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">
              Natural-Language Financial Screen Translation
            </h2>
          </div>

          <div className="flex items-center gap-2 font-mono text-[11px] text-muted-foreground">
            <span className={isOverLimit ? "font-bold text-rose-500" : ""}>
              {charCount} / {MAX_CHARS}
            </span>
            <span className="hidden sm:inline">·</span>
            <span className="hidden sm:inline">Ctrl + Enter to Translate</span>
          </div>
        </div>

        {/* Textarea Input */}
        <div className="relative">
          <textarea
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
              if (error) setError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Describe the stocks you want to find using financial conditions (e.g. Find Indian large-cap stocks with revenue growth above 15%, positive free cash flow, P/E below 25 and price above the 200-day moving average)..."
            rows={3}
            className="w-full resize-none rounded-md border border-border/80 bg-background/80 p-3 text-xs leading-relaxed text-foreground placeholder:text-muted-foreground/60 transition-colors focus:border-primary focus:bg-background focus:outline-none focus:ring-1 focus:ring-primary font-sans"
          />
        </div>

        {/* Action Row & Example Chips */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          {/* Example Suggestions Chips */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-medium text-muted-foreground mr-1">
              Examples:
            </span>
            {EXAMPLE_PROMPTS.map((ex, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => selectPrompt(ex.prompt)}
                className="rounded-full border border-border/60 bg-muted/30 px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground hover:border-primary/50 hover:bg-muted/60 hover:text-foreground transition-colors"
              >
                {ex.title}
              </button>
            ))}
          </div>

          {/* Translate Button */}
          <button
            type="button"
            disabled={loading || isOverLimit || !inputText.trim()}
            onClick={() => handleTranslate()}
            className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground shadow-sm transition-all hover:bg-primary/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Translating...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                <span>Translate to Filters</span>
                <CornerDownLeft className="h-3 w-3 text-primary-foreground/60 hidden sm:inline" />
              </>
            )}
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="flex items-center gap-2 rounded-md border border-rose-500/30 bg-rose-500/10 px-3.5 py-2 text-xs text-rose-500 font-medium">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Structured Translation Review Panel */}
      {proposal && (
        <TranslationReviewPanel
          proposal={proposal}
          isClarifying={isClarifying}
          onClarify={handleClarify}
          onTransferToBuilder={onTransferToBuilder}
          onApplyAndRun={onApplyAndRun}
          onReset={() => {
            setProposal(null);
            setInputText("");
            setError(null);
          }}
        />
      )}
    </div>
  );
}
