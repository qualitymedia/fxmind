"use client";

import { useEffect, useState } from "react";
import { Search, Bell, Activity } from "lucide-react";

export function Header() {
  const [utcTime, setUtcTime] = useState<string>("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(
        now.toISOString().substring(11, 19) + " UTC"
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-card border-b border-border px-6 flex items-center justify-between flex-shrink-0">
      {/* Search Input */}
      <div className="relative w-80">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          placeholder="Search symbols, signals, or features..."
          className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-2 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {/* Header Right Actions */}
      <div className="flex items-center gap-6">
        {/* Live Status Indicator */}
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span className="w-2 h-2 rounded-full bg-positive animate-pulse" />
          <span className="font-semibold text-text-primary">Live</span>
          <span className="text-text-muted font-mono">{utcTime || "Syncing..."}</span>
        </div>


        {/* Notifications Icon */}
        <button className="relative text-text-secondary hover:text-text-primary p-2 rounded-lg hover:bg-background transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-negative" />
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-3 pl-4 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center border border-primary/20">
            JD
          </div>
          <div className="text-left">
            <span className="text-xs font-semibold text-text-primary block leading-none">
              John Doe
            </span>
            <span className="text-[11px] text-text-secondary block mt-0.5 leading-none">
              Analyst
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
