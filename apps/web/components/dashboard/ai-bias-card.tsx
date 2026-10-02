"use client";

import { TrendingUp, TrendingDown, Minus, Shield } from "lucide-react";

interface AIBiasCardProps {
  bias?: "BULLISH" | "BEARISH" | "NEUTRAL";
  confidence?: number;
}

const TIER = (c: number) =>
  c >= 0.78 ? { label: "VERY HIGH", ring: "stroke-emerald-400", text: "text-emerald-400" }
  : c >= 0.65 ? { label: "HIGH", ring: "stroke-blue-400", text: "text-blue-400" }
  : c >= 0.58 ? { label: "MODERATE", ring: "stroke-amber-400", text: "text-amber-400" }
  : { label: "LOW", ring: "stroke-red-400", text: "text-red-400" };

export function AIBiasCard({ bias = "BULLISH", confidence = 0.68 }: AIBiasCardProps) {
  const isBull = bias === "BULLISH";
  const isBear = bias === "BEARISH";

  const colorClass = isBull ? "text-positive" : isBear ? "text-negative" : "text-text-secondary";
  const bgLightClass = isBull ? "bg-positive-light" : isBear ? "bg-negative-light" : "bg-background";
  const Icon = isBull ? TrendingUp : isBear ? TrendingDown : Minus;
  const percent = Math.round(confidence * 100);
  const tier = TIER(confidence);

  // Circular ring math (r=16, circumference=100.5)
  const radius = 16;
  const circ = 2 * Math.PI * radius;
  const dash = (percent / 100) * circ;

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card flex items-center justify-between gap-3">
      {/* Left: bias label */}
      <div className="min-w-0 flex-1">
        <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
          AI Market Bias
        </span>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className={`text-base font-bold font-display tracking-tight ${colorClass}`}>
            {bias}
          </span>
          <div className={`p-0.5 rounded ${bgLightClass} ${colorClass}`}>
            <Icon className="w-3.5 h-3.5" />
          </div>
        </div>
        <span className={`text-[10px] font-bold mt-1 block ${tier.text}`}>
          {tier.label} CONFIDENCE
        </span>
      </div>

      {/* Right: radial confidence ring */}
      <div className="flex-shrink-0 relative w-12 h-12">
        <svg viewBox="0 0 40 40" className="w-full h-full -rotate-90">
          {/* Track */}
          <circle
            cx="20" cy="20" r={radius}
            fill="none"
            className="stroke-border"
            strokeWidth="3"
          />
          {/* Progress */}
          <circle
            cx="20" cy="20" r={radius}
            fill="none"
            className={`${tier.ring} transition-all duration-700`}
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-[11px] font-bold font-mono ${tier.text}`}>{percent}%</span>
        </div>
      </div>
    </div>
  );
}
