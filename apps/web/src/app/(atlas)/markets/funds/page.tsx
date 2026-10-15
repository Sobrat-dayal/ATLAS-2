import { Metadata } from "next";
import { FundsPage } from "@/components/markets/funds";

export function generateMetadata(): Metadata {
  return {
    title: "ETFs & Funds Markets | ATLAS",
    description:
      "Global fund discovery, ETF intelligence, NAV-aware market data, and professional investment fund explorer.",
  };
}

export default function FundsRoute() {
  return <FundsPage />;
}
