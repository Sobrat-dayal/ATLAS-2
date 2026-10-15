import { Metadata } from "next";
import { BondsPage } from "@/components/markets/bonds";

export function generateMetadata(): Metadata {
  return {
    title: "Bonds & Fixed-Income Markets | ATLAS",
    description:
      "Global bond discovery, sovereign and corporate debt markets, coupon intelligence, yield observations, clean/dirty pricing, and professional fixed-income terminal.",
  };
}

export default function BondsRoute() {
  return <BondsPage />;
}
