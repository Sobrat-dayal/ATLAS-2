"use client";

import { Bell, Bot, User } from "lucide-react";
import { GlobalSearch } from "./GlobalSearch";
import { useEffect, useState } from "react";
import { useShellState } from "@/hooks/shell/useShellState";

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
    <div className="flex h-11 shrink-0 items-center justify-between border-b border-[#1E2330] bg-[#0F131C] px-3">
      {/* Brand area */}
      <div className="flex items-center space-x-4">
        <span className="font-bold tracking-widest text-white">ATLAS</span>
      </div>

      {/* Center Global Search */}
      <div className="flex flex-1 justify-center px-6 max-w-3xl">
        <GlobalSearch />
      </div>

      {/* Right utilities */}
      <div className="flex items-center space-x-3">
        {utcTime && <span className="text-xs text-gray-400 font-mono tracking-wider mr-2 hidden lg:block">{utcTime}</span>}
        
        {/* ATLAS AI Hook */}
        <button className="flex items-center gap-1.5 rounded-sm bg-[#1E2B4D] px-2 py-1 text-xs font-medium text-[#60A5FA] hover:bg-[#25345C] transition-colors">
          <Bot className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">ATLAS AI</span>
        </button>

        {/* Notifications Hook */}
        <button className="relative rounded-sm p-1.5 text-gray-400 hover:bg-[#1A202E] hover:text-white transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-blue-500"></span>
        </button>

        {/* Agent Dock Hook (Mobile/Alternative) */}
        {!agentDockOpen && (
          <button 
            onClick={() => setAgentDockOpen(true)}
            className="rounded-sm p-1.5 text-gray-400 hover:bg-[#1A202E] hover:text-white transition-colors hidden md:block"
            title="Open Agent Dock"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="15" x2="15" y1="3" y2="21"/></svg>
          </button>
        )}

        {/* User Profile Hook */}
        <button className="flex h-6 w-6 items-center justify-center rounded-full bg-[#1E2330] text-xs font-medium text-gray-300 hover:bg-[#252A38] transition-colors">
          <User className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
