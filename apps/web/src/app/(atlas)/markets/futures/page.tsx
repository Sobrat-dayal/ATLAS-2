import { Metadata } from "next";
import { FuturesMarketsPage } from "@/components/markets/futures";

export function generateMetadata(): Metadata {
  return {
    title: "Futures & Commodities Markets | ATLAS",
    description:
      "Global commodity intelligence, exchange-traded futures, contract discovery, settlement data, expiration management and professional derivatives market terminal.",
  };
}

export default function FuturesRoute() {
  return <FuturesMarketsPage />;
}
