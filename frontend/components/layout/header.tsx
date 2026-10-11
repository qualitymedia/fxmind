"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Market overview",
  "/signals": "Signal history",
  "/calendar": "Insights",
  "/performance": "Performance",
  "/settings": "Settings",
  "/trade": "Broker connection",
};

export function Header() {
  const [utcTime, setUtcTime] = useState<string>("");
  const pathname = usePathname();
  const pageTitle = PAGE_TITLES[pathname] ?? "Market desk";

  useEffect(() => {
    const updateTime = () => {
      setUtcTime(new Intl.DateTimeFormat("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        timeZone: "UTC",
        timeZoneName: "short",
      }).format(new Date()));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="relative z-40 flex h-14 flex-shrink-0 items-center justify-between border-b border-border bg-card/95 px-4 backdrop-blur sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <span className="hidden text-[10px] font-bold tracking-[0.12em] text-text-muted sm:inline">FXMIND</span>
        <span className="hidden h-4 w-px bg-border sm:block" />
        <h1 className="truncate font-display text-sm font-bold text-text-primary">{pageTitle}</h1>
      </div>
      <div className="flex items-center gap-3 sm:gap-5">
        <span className="hidden rounded-sm border border-border bg-background px-2 py-1 font-mono text-[11px] font-semibold text-text-secondary sm:inline-flex">GBP/USD</span>
        <div className="flex items-center gap-2 border-l border-border pl-3 sm:pl-5">
          <span className="text-[10px] font-semibold uppercase text-text-muted">UTC</span>
          <time className="min-w-[5.5rem] font-mono text-xs font-medium tabular-nums text-text-primary">{utcTime || "--:--:-- UTC"}</time>
        </div>
      </div>
    </header>
  );
}
