"use client";

import { Suspense } from "react";
import { CompaniesWorkspace } from "@/components/companies";
import { Loader2 } from "lucide-react";

export default function CompaniesPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-full text-xs text-atlas-text-muted gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-atlas-accent" />
          <span>Loading Companies workspace...</span>
        </div>
      }
    >
      <CompaniesWorkspace />
    </Suspense>
  );
}
