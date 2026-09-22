"use client";

import { Activity } from "lucide-react";

interface RegimeCardProps {
  regime?: "TRENDING" | "RANGING" | "HIGH_VOLATILITY" | "ILLIQUID";
}

export function RegimeCard({ regime = "TRENDING" }: RegimeCardProps) {
  const subtitleMap = {
    TRENDING: "Strong Trend",
    RANGING: "Consolidation",
    HIGH_VOLATILITY: "High ATR",
    ILLIQUID: "Low Volume",
  };

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card flex items-center justify-between">
      <div>
        <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
          Market Regime
        </span>
        <span className="text-base font-bold font-display text-text-primary block mt-0.5">
          {regime}
        </span>
        <span className="text-[10px] text-text-secondary block">
          {subtitleMap[regime] || "Normal"}
        </span>
      </div>

      <div className="p-2 rounded-lg bg-primary/10 text-primary">
        <Activity className="w-4 h-4" />
      </div>
    </div>
  );
}
