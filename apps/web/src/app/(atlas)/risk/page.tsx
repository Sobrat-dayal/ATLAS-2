import { Metadata } from "next";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { RiskTerminalWorkspace } from "@/components/risk/RiskTerminalWorkspace";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.risk.label} | ATLAS`,
    description: "Institutional-Grade Financial Risk Management Terminal: Volatility, Drawdown Analytics, Benchmark Sensitivity, and Euler Risk Decomposition.",
  };
}

export default function RiskPage() {
  return <RiskTerminalWorkspace />;
}
