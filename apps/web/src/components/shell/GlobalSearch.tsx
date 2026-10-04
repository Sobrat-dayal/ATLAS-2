"use client";

import { useEffect, useRef, useState } from "react";
import { Search } from "lucide-react";

export function GlobalSearch() {
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape" && document.activeElement === inputRef.current) {
        inputRef.current?.blur();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="relative flex max-w-lg flex-1 items-center">
      <div
        className={`flex w-full items-center rounded-sm border px-2 py-1 transition-colors ${
          focused ? "border-[#60A5FA] bg-[#1A202E]" : "border-[#1E2330] bg-[#141824]"
        }`}
      >
        <Search className="mr-2 h-3.5 w-3.5 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          placeholder="Search companies, tickers, markets, news, research... (Ctrl+K)"
          className="w-full bg-transparent text-sm text-gray-200 placeholder-gray-500 outline-none"
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
        <div className="ml-2 flex items-center gap-1 rounded bg-[#1E2330] px-1.5 py-0.5 text-[10px] text-gray-400">
          <span>⌘K</span>
        </div>
      </div>
    </div>
  );
}
