"use client";

import { Bot, Calculator, Compass, Sparkles, TrendingUp } from "lucide-react";

interface AtlasAiEmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

const SAMPLE_PROMPTS = [
  {
    icon: TrendingUp,
    title: "Duration vs Convexity",
    prompt: "Explain the mathematical difference between Modified Duration and Convexity in fixed income analysis.",
  },
  {
    icon: Calculator,
    title: "Sharpe Ratio Math",
    prompt: "Calculate Sharpe ratio with return 12%, risk free 3%, and portfolio volatility 15%.",
  },
  {
    icon: Compass,
    title: "VaR vs CVaR",
    prompt: "Compare Value at Risk (VaR) and Conditional VaR (Expected Shortfall) for fat-tailed distributions.",
  },
  {
    icon: Bot,
    title: "Risk Engine Guidance",
    prompt: "Where can I find portfolio factor risk models, stress tests, and scenario simulations?",
  },
];

export function AtlasAiEmptyState({ onSelectPrompt }: AtlasAiEmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-6 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-atlas-surface-2 border border-atlas-border-default mb-3 text-atlas-accent shadow-sm">
        <Bot className="h-6 w-6" />
      </div>

      <h3 className="text-sm font-semibold text-atlas-text-primary mb-1">
        ATLAS Financial Intelligence V1
      </h3>
      <p className="text-xs text-atlas-text-secondary max-w-xs mb-6">
        Ask financial questions, compute quantitative formulas, or request guidance across the 20 ATLAS modules.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
        {SAMPLE_PROMPTS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className="flex items-start gap-2.5 rounded border border-atlas-border-default bg-atlas-surface-1 p-2.5 text-left text-xs transition-all hover:border-atlas-accent hover:bg-atlas-surface-hover group"
            >
              <Icon className="h-4 w-4 shrink-0 text-atlas-accent mt-0.5" />
              <div>
                <span className="font-medium text-atlas-text-primary block group-hover:text-atlas-accent">
                  {item.title}
                </span>
                <span className="text-[11px] text-atlas-text-muted line-clamp-2">
                  {item.prompt}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

