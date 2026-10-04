import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.portfolios.label} | ATLAS`
  };
}

export default function PortfoliosPage() {
  return <ModuleFoundation module={ATLAS_MODULES.portfolios} />;
}
