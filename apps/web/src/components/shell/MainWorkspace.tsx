"use client";

import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useAuthorization } from "@/hooks/authorization";
import { getActiveAtlasModule } from "@/config/atlas-modules";
import { AccessDenied } from "./AccessDenied";

interface MainWorkspaceProps {
  children: ReactNode;
}

export function MainWorkspace({ children }: MainWorkspaceProps) {
  const pathname = usePathname();
  const { canViewModule, isLoading } = useAuthorization();
  
  const activeModule = getActiveAtlasModule(pathname);
  
  // Show nothing or a loader while authz is loading
  if (isLoading) {
    return (
      <main className="flex-1 overflow-y-auto overflow-x-hidden bg-atlas-bg-0 relative">
        <div className="flex h-full w-full items-center justify-center">
          {/* subtle loading state */}
        </div>
      </main>
    );
  }

  // If there's an active module and user doesn't have permission, block access
  if (activeModule && !canViewModule(activeModule.id)) {
    return (
      <main className="flex-1 overflow-y-auto overflow-x-hidden bg-atlas-bg-0 relative">
        <div className="h-full w-full">
          <AccessDenied />
        </div>
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto overflow-x-hidden bg-atlas-bg-0 relative">
      <div className="h-full w-full">
        {children}
      </div>
    </main>
  );
}
