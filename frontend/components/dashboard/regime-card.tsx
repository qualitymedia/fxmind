"use client";

import { Activity, TrendingUp, Minus, Zap, Moon } from "lucide-react";

interface RegimeCardProps {
  regime?: "TRENDING" | "RANGING" | "HIGH_VOLATILITY" | "ILLIQUID";
}

const REGIME_CONFIG = {
  TRENDING: {
    subtitle: "Strong Directional Move",
    hint: "VP-POC Retest or Trend-Follow",
    icon: TrendingUp,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  RANGING: {
    subtitle: "Value Area Consolidation",
    hint: "Value Area Rotation (80% Rule)",
    icon: Minus,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  HIGH_VOLATILITY: {
    subtitle: "Elevated ATR / Spread",
    hint: "Wider stops, reduced sizing",
    icon: Zap,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  ILLIQUID: {
    subtitle: "Asian Session Low Vol",
    hint: "Trailing limit entry if ≥ 80%",
    icon: Moon,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/20",
  },
};

export function RegimeCard({ regime }: RegimeCardProps) {
  const cfg = regime ? REGIME_CONFIG[regime] : null;
  const Icon = cfg?.icon;

  return (
    <div className={`min-h-[108px] bg-card border ${cfg?.border ?? "border-border"} rounded-xl p-2.5 shadow-card flex items-center justify-between`}>
      <div className="min-w-0 flex-1">
        <span className="text-[9px] font-bold text-text-secondary uppercase tracking-wider block">
          Regime
        </span>
        <span className={`text-base font-bold font-display block mt-0.5 ${cfg?.color ?? "text-text-secondary"}`}>
          {regime ?? "—"}
        </span>
        <span className="text-[9px] text-text-secondary block leading-tight">
          {cfg?.subtitle ?? "Waiting for analysis"}
        </span>
      </div>

      {cfg && Icon && (
        <div className={`p-2 rounded-lg flex-shrink-0 ml-2 ${cfg.bg} ${cfg.color}`}>
          <Icon className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
