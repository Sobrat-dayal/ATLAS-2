import { Metadata } from "next";
import { FxPage } from "@/components/markets/fx";

export function generateMetadata(): Metadata {
  return {
    title: "FX Markets | ATLAS",
    description:
      "Global foreign exchange intelligence, currency pair discovery, spot exchange rates, bid/ask analytics, and indicative currency conversion.",
  };
}

export default function FxRoute() {
  return <FxPage />;
}
