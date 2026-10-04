"use client";

import { Bell, Bot, User } from "lucide-react";
import { GlobalSearch } from "./GlobalSearch";
import { useEffect, useState } from "react";
import { useShellState } from "@/hooks/shell/useShellState";
import { DevAppearanceSwitcher } from "./DevAppearanceSwitcher";
import { BackgroundQuickControl } from "./BackgroundQuickControl";

export function TopBar() {
  const [utcTime, setUtcTime] = useState("");
  const { agentDockOpen, setAgentDockOpen } = useShellState();

  useEffect(() => {
    // Client-side rendering of UTC time to avoid hydration mismatch
    const updateTime = () => {
      const now = new Date();
      setUtcTime(`UTC ${now.toISOString().substring(11, 19)}`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-11 shrink-0 items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-3">
      {/* Brand area */}
      <div className="flex items-center space-x-4">
        <span className="font-bold tracking-widest text-atlas-text-primary">ATLAS</span>
      </div>

      {/* Center Global Search */}
      <div className="flex flex-1 justify-center px-6 max-w-3xl">
        <GlobalSearch />
      </div>

      {/* Right utilities */}
      <div className="flex items-center space-x-3">
        {utcTime && <span className="text-xs text-atlas-text-secondary font-mono tracking-wider mr-2 hidden lg:block">{utcTime}</span>}
        
        {/* ATLAS AI Hook */}
        <button className="flex items-center gap-1.5 rounded-sm bg-atlas-surface-selected px-2 py-1 text-xs font-medium text-atlas-accent hover:bg-atlas-surface-hover transition-colors">
          <Bot className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">ATLAS AI</span>
        </button>

        {/* Notifications Hook */}
        <button className="relative rounded-sm p-1.5 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-atlas-accent"></span>
        </button>

        {/* Agent Dock Hook (Mobile/Alternative) */}
        {!agentDockOpen && (
          <button 
            onClick={() => setAgentDockOpen(true)}
            className="rounded-sm p-1.5 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors hidden md:block"
            title="Open Agent Dock"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="15" x2="15" y1="3" y2="21"/></svg>
          </button>
        )}

        <BackgroundQuickControl />
        <DevAppearanceSwitcher />

        {/* User Profile Hook */}
        <button className="flex h-6 w-6 items-center justify-center rounded-full bg-atlas-surface-2 text-xs font-medium text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors">
          <User className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
