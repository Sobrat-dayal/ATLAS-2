import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.intelligence.label} | ATLAS`
  };
}

export default function IntelligencePage() {
  return <ModuleFoundation module={ATLAS_MODULES.intelligence} />;
}
