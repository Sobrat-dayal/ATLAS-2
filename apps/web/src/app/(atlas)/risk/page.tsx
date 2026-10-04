import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.risk.label} | ATLAS`
  };
}

export default function RiskPage() {
  return <ModuleFoundation module={ATLAS_MODULES.risk} />;
}
