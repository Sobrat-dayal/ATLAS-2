import { ATLAS_MODULES } from "@/config/atlas-modules";
import { Metadata } from "next";

export function generateMetadata(): Metadata {
  return {
    title: `${ATLAS_MODULES.home.label} | ATLAS`
  };
}

export default function HomeLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
