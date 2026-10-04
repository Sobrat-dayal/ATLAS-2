import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.agents.label} | ATLAS`
  };
}

export default function AgentsPage() {
  return <ModuleFoundation module={ATLAS_MODULES.agents} />;
}
