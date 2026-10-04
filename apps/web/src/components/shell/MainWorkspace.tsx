"use client";

import { ReactNode } from "react";

interface MainWorkspaceProps {
  children: ReactNode;
}

export function MainWorkspace({ children }: MainWorkspaceProps) {
  return (
    <main className="flex-1 overflow-y-auto overflow-x-hidden bg-[#0A0D14] relative">
      <div className="h-full w-full">
        {children}
      </div>
    </main>
  );
}
