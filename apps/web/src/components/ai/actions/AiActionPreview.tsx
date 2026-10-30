"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";
import { AiActionApproval } from "./AiActionApproval";
import { AiActionDiff } from "./AiActionDiff";
import { ChartActionPreview } from "./charts/ChartActionPreview";
import { PortfolioScenarioPreview } from "./portfolios/PortfolioScenarioPreview";
import { RiskActionPreview } from "./risk/RiskActionPreview";
import { ScreenerActionPreview } from "./screeners/ScreenerActionPreview";

interface AiActionPreviewProps {
  action: ActionDTO;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
  isLoading?: boolean;
}

export function AiActionPreview({
  action,
  onApprove,
  onDeny,
  isLoading = false,
}: AiActionPreviewProps) {
  const renderDomainPreview = () => {
    switch (action.target_module) {
      case "charts":
        return <ChartActionPreview action={action} />;
      case "screeners":
        return <ScreenerActionPreview action={action} />;
      case "portfolios":
        return <PortfolioScenarioPreview action={action} />;
      case "risk":
        return <RiskActionPreview action={action} />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4 p-3 rounded-lg border border-neutral-800 bg-neutral-900/30">
      {/* 1. Domain Configuration Overview */}
      {renderDomainPreview()}

      {/* 2. Before/After Field Diffs */}
      {action.preview && action.preview.diffs.length > 0 && (
        <div className="space-y-1.5">
          <div className="text-xs font-medium text-neutral-400">Proposed State Modifications:</div>
          <AiActionDiff diffs={action.preview.diffs} />
        </div>
      )}

      {/* 3. Explicit Approval & Security Verification */}
      <AiActionApproval
        action={action}
        onApprove={onApprove}
        onDeny={onDeny}
        isLoading={isLoading}
      />
    </div>
  );
}

