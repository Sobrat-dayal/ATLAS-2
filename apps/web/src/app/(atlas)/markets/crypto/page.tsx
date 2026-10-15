import { Metadata } from "next";
import { CryptoMarketsPage } from "@/components/markets/crypto";

export function generateMetadata(): Metadata {
  return {
    title: "Cryptocurrency Markets | ATLAS",
    description:
      "Global digital asset discovery, exchange-aware spot markets, digital asset intelligence, real-time trading pairs, and professional crypto terminal.",
  };
}

export default function CryptoRoute() {
  return <CryptoMarketsPage />;
}
