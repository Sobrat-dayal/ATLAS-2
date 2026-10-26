import { ATLAS_MODULES } from "@/config/atlas-modules";
import { ScreenerWorkspace } from "@/components/screeners";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.screeners.label} | ATLAS`
  };
}

export default function ScreenersPage() {
  return <ScreenerWorkspace />;
}
