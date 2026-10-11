"use client";

import { VolumeProfileData } from "@/lib/useDashboardData";
import { BarChart2, Layers, Compass, ArrowUpRight, ArrowDownRight, Anchor } from "lucide-react";

interface VolumeProfileCardProps {
  volumeProfile: VolumeProfileData | null;
  currentPrice?: number;
}

export function VolumeProfileCard({ volumeProfile, currentPrice }: VolumeProfileCardProps) {
  if (!volumeProfile) {
    return (
      <div className="bg-card border border-border rounded-xl p-4 shadow-card animate-pulse">
        <div className="h-4 bg-card-secondary rounded w-1/3 mb-3" />
        <div className="h-8 bg-card-secondary rounded w-2/3 mb-2" />
        <div className="h-4 bg-card-secondary rounded w-1/2" />
      </div>
    );
  }

  const { poc, vah, val, price_position, dist_to_poc_pips, bins } = volumeProfile;

  // Position badge styling
  const posBadge =
    price_position === "ABOVE_VAH"
      ? {
          label: "Above VAH (Premium / Rejection Watch)",
          color: "text-amber-400 bg-amber-500/10 border-amber-500/30",
        }
      : price_position === "BELOW_VAL"
      ? {
          label: "Below VAL (Discount / Reversion Watch)",
          color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
        }
      : {
          label: "Inside Value Area (Fair Value 70%)",
          color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
        };

  return (
    <div className="bg-card border border-border rounded-xl p-4 shadow-card hover:border-primary/30 transition-all flex flex-col justify-between">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center border border-amber-500/20">
              <Anchor className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-text-muted block leading-none">
                Volume Profile
              </span>
              <span className="text-xs font-semibold text-text-primary">
                24H Rolling POC & 70% Value Area
              </span>
            </div>
          </div>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${posBadge.color}`}>
            {price_position}
          </span>
        </div>

        {/* POC Hero Stat */}
        <div className="mt-3 p-3 rounded-lg bg-background border border-border/80 flex items-center justify-between">
          <div>
            <div className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1">
              <span>● Point of Control (POC)</span>
            </div>
            <div className="text-xl font-bold font-mono text-text-primary tracking-tight mt-0.5">
              {poc.toFixed(5)}
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] text-text-muted block">Distance to POC</span>
            <span
              className={`text-xs font-mono font-bold flex items-center justify-end gap-0.5 ${
                dist_to_poc_pips > 0
                  ? "text-emerald-400"
                  : dist_to_poc_pips < 0
                  ? "text-red-400"
                  : "text-text-secondary"
              }`}
            >
              {dist_to_poc_pips > 0 ? (
                <ArrowUpRight className="w-3.5 h-3.5" />
              ) : (
                <ArrowDownRight className="w-3.5 h-3.5" />
              )}
              {Math.abs(dist_to_poc_pips).toFixed(1)} pips
            </span>
          </div>
        </div>

        {/* Value Area High & Low Grid */}
        <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
          <div className="p-2.5 rounded-lg bg-background border border-cyan-500/20">
            <span className="text-[10px] font-semibold text-cyan-400 block uppercase">
              VAH (Value Area High)
            </span>
            <span className="font-mono font-bold text-text-primary text-sm mt-0.5 block">
              {vah.toFixed(5)}
            </span>
            <span className="text-[10px] text-text-muted">Upper 70% boundary</span>
          </div>

          <div className="p-2.5 rounded-lg bg-background border border-purple-500/20">
            <span className="text-[10px] font-semibold text-purple-400 block uppercase">
              VAL (Value Area Low)
            </span>
            <span className="font-mono font-bold text-text-primary text-sm mt-0.5 block">
              {val.toFixed(5)}
            </span>
            <span className="text-[10px] text-text-muted">Lower 70% boundary</span>
          </div>
        </div>

        {/* Mini Volume Distribution Histogram */}
        {bins && bins.length > 0 && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-[10px] text-text-muted mb-1 font-mono">
              <span>Volume Distribution Profile</span>
              <span>70% Value Area Range</span>
            </div>
            <div className="space-y-1 bg-background/60 p-2 rounded-lg border border-border">
              {bins.slice(-8).map((b, idx) => (
                <div key={idx} className="flex items-center gap-2 text-[10px] font-mono">
                  <span
                    className={`w-14 truncate ${
                      b.is_poc
                        ? "text-amber-400 font-bold"
                        : b.is_value_area
                        ? "text-cyan-300"
                        : "text-text-muted"
                    }`}
                  >
                    {b.price.toFixed(4)}
                  </span>
                  <div className="flex-1 bg-card-secondary h-2 rounded-full overflow-hidden relative">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        b.is_poc
                          ? "bg-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.6)]"
                          : b.is_value_area
                          ? "bg-cyan-500/60"
                          : "bg-slate-600/40"
                      }`}
                      style={{ width: `${Math.min(100, Math.max(6, b.percentage))}%` }}
                    />
                  </div>
                  <span className="w-7 text-right text-[9px] text-text-muted">
                    {b.percentage.toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Insight */}
      <div className="mt-3 pt-2 border-t border-border flex items-center justify-between text-[11px] text-text-muted">
        <span className="flex items-center gap-1.5 text-text-secondary">
          <Compass className="w-3.5 h-3.5 text-primary" />
          {posBadge.label}
        </span>
        <span className="text-[10px] text-text-muted font-mono">Market Profile Rule</span>
      </div>
    </div>
  );
}
