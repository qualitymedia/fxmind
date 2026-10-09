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
    <div className="min-h-[108px] bg-card border border-border rounded-xl p-2.5 shadow-card space-y-2">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 min-w-0">
          <div className="p-1 rounded bg-amber-500/10 text-amber-500">
            <Star className="w-3 h-3 fill-amber-500/30" />
          </div>
          <span className="text-[9px] font-bold font-display text-text-primary uppercase tracking-wider truncate">
            SETUP
          </span>
        </div>

        <span
          className={`px-1.5 py-0.5 text-[8px] font-bold rounded uppercase ${
            isHighQuality
              ? "bg-positive/10 text-positive border border-positive/30"
              : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
          }`}
        >
          {quality}
        </span>
      </div>

      <div className="bg-background/50 border border-border/60 px-2 py-1.5 rounded-lg flex items-center justify-between gap-2">
        <div className="min-w-0">
          <span className="text-[8px] text-text-muted uppercase block">Exec</span>
          <span className="text-xs font-bold font-display text-text-primary uppercase truncate block">
            {quality}
          </span>
        </div>
        <div className="text-right min-w-0">
          <span className="text-[8px] text-text-muted uppercase block">R:R</span>
          <span className="text-[10px] font-mono font-bold text-text-primary">
            {riskReward != null ? `1 : ${riskReward.toFixed(1)}` : "1 : 2.0"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-1 text-[8px] font-mono">
        <div className="bg-background/40 px-1.5 py-1 rounded border border-border/40">
          <span className="text-text-muted uppercase block">SL</span>
          <span className="text-rose-400 font-bold">
            {stopLoss ? stopLoss.toFixed(4) : "Dynamic"}
          </span>
        </div>
        <div className="bg-background/40 px-1.5 py-1 rounded border border-border/40">
          <span className="text-text-muted uppercase block">TP</span>
          <span className="text-emerald-400 font-bold">
            {takeProfit ? takeProfit.toFixed(4) : "Dynamic"}
          </span>
        </div>
      </div>
    </div>
  );
}
