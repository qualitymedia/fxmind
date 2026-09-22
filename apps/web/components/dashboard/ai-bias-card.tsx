"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface AIBiasCardProps {
  bias?: "BULLISH" | "BEARISH" | "NEUTRAL";
  confidence?: number;
}

export function AIBiasCard({ bias = "BULLISH", confidence = 0.68 }: AIBiasCardProps) {
  const isBull = bias === "BULLISH";
  const isBear = bias === "BEARISH";

  const colorClass = isBull
    ? "text-positive"
    : isBear
    ? "text-negative"
    : "text-text-secondary";

  const bgLightClass = isBull
    ? "bg-positive-light"
    : isBear
    ? "bg-negative-light"
    : "bg-background";

  const Icon = isBull ? TrendingUp : isBear ? TrendingDown : Minus;
  const percent = Math.round(confidence * 100);

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card flex flex-col justify-between space-y-2">
      <div className="flex items-center justify-between">
        <div>
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
        </div>

        <div className="text-right">
          <span className="text-lg font-bold font-display text-text-primary">
            {percent}%
          </span>
          <span className="text-[9px] text-text-secondary block leading-none">
            Confidence
          </span>
        </div>
      </div>

      <div className="w-full bg-background rounded-full h-1 overflow-hidden border border-border">
        <div
          className={`h-full transition-all duration-500 rounded-full ${
            isBull ? "bg-positive" : isBear ? "bg-negative" : "bg-text-secondary"
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
