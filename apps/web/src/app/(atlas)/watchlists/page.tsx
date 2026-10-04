import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ModuleFoundation } from "@/components/modules/ModuleFoundation";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.watchlists.label} | ATLAS`
  };
}

export default function WatchlistsPage() {
  return <ModuleFoundation module={ATLAS_MODULES.watchlists} />;
}
