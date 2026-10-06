"use client";

import { Star, ShieldCheck, Target, AlertTriangle } from "lucide-react";

interface SetupQualityCardProps {
  quality?: string;
  riskReward?: number | null;
  entryLow?: number | null;
  entryHigh?: number | null;
  stopLoss?: number | null;
  takeProfit?: number | null;
}

export function SetupQualityCard({
  quality = "Key Watch Levels",
  riskReward = 2.4,
  entryLow,
  entryHigh,
  stopLoss,
  takeProfit,
}: SetupQualityCardProps) {
  const isHighQuality = quality === "Very Strong" || quality === "Strong";

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card space-y-2.5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <div className="p-1 rounded bg-amber-500/10 text-amber-500">
            <Star className="w-3.5 h-3.5 fill-amber-500/30" />
          </div>
          <span className="text-xs font-bold font-display text-text-primary uppercase tracking-wider">
            SETUP QUALITY
          </span>
        </div>

        <span
          className={`px-1.5 py-0.5 text-[9px] font-bold rounded uppercase ${
            isHighQuality
              ? "bg-positive/10 text-positive border border-positive/30"
              : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
          }`}
        >
          {quality}
        </span>
      </div>

      {/* Main Grade & R:R Summary */}
      <div className="bg-background/50 border border-border/60 p-2 rounded-lg flex items-center justify-between">
        <div>
          <span className="text-[9px] text-text-muted uppercase block">Execution Rating</span>
          <span className="text-sm font-bold font-display text-text-primary uppercase">
            {quality}
          </span>
        </div>
        <div className="text-right">
          <span className="text-[9px] text-text-muted uppercase block">Risk / Reward</span>
          <span className="text-xs font-mono font-bold text-text-primary">
            {riskReward != null ? `1 : ${riskReward.toFixed(1)}` : "1 : 2.0"}
          </span>
        </div>
      </div>

      {/* Key Watch Levels summary */}
      <div className="grid grid-cols-2 gap-1.5 text-[9px] font-mono">
        <div className="bg-background/40 p-1.5 rounded border border-border/40">
          <span className="text-text-muted text-[8px] uppercase block">SL Protect</span>
          <span className="text-rose-400 font-bold">
            {stopLoss ? stopLoss.toFixed(4) : "Dynamic SL"}
          </span>
        </div>
        <div className="bg-background/40 p-1.5 rounded border border-border/40">
          <span className="text-text-muted text-[8px] uppercase block">TP Target</span>
          <span className="text-emerald-400 font-bold">
            {takeProfit ? takeProfit.toFixed(4) : "Dynamic TP"}
          </span>
        </div>
      </div>
    </div>
  );
}
