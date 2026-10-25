"use client";

import { Button } from "@/design-system";
import { AlertCircle, RefreshCw } from "lucide-react";

export interface CompanyErrorStateProps {
  error: Error | string;
  onRetry?: () => void;
  className?: string;
}

export function CompanyErrorState({ error, onRetry, className = "" }: CompanyErrorStateProps) {
  const message = typeof error === "string" ? error : error.message;

  return (
    <div
      role="alert"
      className={`bg-atlas-surface-1 border border-atlas-negative/30 rounded-sm p-8 text-center max-w-xl mx-auto my-12 space-y-4 ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-atlas-negative/10 text-atlas-negative flex items-center justify-center mx-auto">
        <AlertCircle className="w-6 h-6" />
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-atlas-text-primary">
          Unable to Load Company Overview
        </h3>
        <p className="text-xs text-atlas-text-secondary leading-relaxed font-mono">
          {message}
        </p>
      </div>

      {onRetry && (
        <div className="pt-2">
          <Button variant="secondary" size="sm" onClick={onRetry} className="gap-1.5 text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Query</span>
          </Button>
        </div>
      )}
    </div>
  );
}
