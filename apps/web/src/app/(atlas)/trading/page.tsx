import { ATLAS_MODULES } from "@/config/atlas-modules";
import { BacktestingLab } from "@/components/trading/backtesting";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.trading.label} | ATLAS Quantitative Backtesting Lab`,
    description:
      "Institutional-grade NautilusTrader historical backtesting, fill simulation, slippage modeling, and strategy research.",
  };
}

export default function TradingPage() {
  return <BacktestingLab />;
}
