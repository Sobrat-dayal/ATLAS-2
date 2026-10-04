"use client";

import { usePathname } from "next/navigation";
import { getActiveAtlasModule, AtlasModuleDefinition } from "@/config/atlas-modules";
import { useMemo } from "react";

export function useCurrentAtlasModule(): AtlasModuleDefinition | undefined {
  const pathname = usePathname();
  
  return useMemo(() => {
    return getActiveAtlasModule(pathname);
  }, [pathname]);
}
