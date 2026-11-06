import { ATLAS_MODULES } from "@/config/atlas-modules";
import { TradingCockpit } from "@/components/trading/TradingCockpit";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.trading.label} | ATLAS Quantitative Trading Cockpit`,
    description:
      "Institutional-grade NautilusTrader historical backtesting, fill simulation, paper trading sandbox, and broker execution gateways.",
  };
}

export default function TradingPage() {
  return <TradingCockpit />;
}
