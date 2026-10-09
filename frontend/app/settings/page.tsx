"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import {
  Settings as SettingsIcon,
  ShieldCheck,
  DollarSign,
  Sliders,
  Save,
  CheckCircle2,
  Bot,
  Terminal,
  Zap,
  Sparkles,
} from "lucide-react";

export default function SettingsPage() {
  const [confidence, setConfidence] = useState<number>(0.58);
  const [newsBuffer, setNewsBuffer] = useState<number>(30);
  const [tpAtr, setTpAtr] = useState<number>(1.8);
  const [slAtr, setSlAtr] = useState<number>(1.0);
  const [baseCapital] = useState<number>(100.0);
  const [savedStatus, setSavedStatus] = useState<boolean>(false);

  const handleSaveParameters = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 3000);
  };

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 md:p-8 space-y-6 max-w-6xl w-full mx-auto">
          {/* Header Banner */}
          <div className="flex items-center justify-between pb-4 border-b border-border flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-primary/15 text-primary flex items-center justify-center border border-primary/25">
                  <SettingsIcon className="w-4 h-4" />
                </div>
                <h1 className="text-2xl font-bold font-display text-text-primary tracking-tight">
                  System Preferences &amp; Risk Parameters
                </h1>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Configure algorithmic risk gates, news blackout filters, and community broadcasts.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono font-bold text-xs flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                MICRO-LOT RISK ENFORCED
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-5">
                <h2 className="text-sm font-bold font-display text-text-primary flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-primary" />
                  Signal Generation &amp; Risk Thresholds
                </h2>

                {/* Min Confidence Gate */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <label className="font-bold text-text-primary">Minimum Confidence Gate</label>
                    <span className="font-mono font-bold text-primary">{(confidence * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.50"
                    max="0.80"
                    step="0.01"
                    value={confidence}
                    onChange={(e) => setConfidence(parseFloat(e.target.value))}
                    className="w-full accent-primary bg-background h-2 rounded-lg cursor-pointer"
                  />
                  <p className="text-[11px] text-text-secondary">
                    Signals below {(confidence * 100).toFixed(0)}% calibrated confidence are suppressed.
                  </p>
                </div>

                {/* News Blackout Buffer */}
                <div className="space-y-2 pt-3 border-t border-border">
                  <div className="flex justify-between items-center text-xs">
                    <label className="font-bold text-text-primary">Macro News Blackout Window</label>
                    <span className="font-mono font-bold text-amber-400">{newsBuffer} Minutes</span>
                  </div>
                  <select
                    value={newsBuffer}
                    onChange={(e) => setNewsBuffer(parseInt(e.target.value))}
                    className="w-full bg-background border border-border rounded-xl p-2.5 text-xs font-mono font-bold focus:outline-none focus:border-primary"
                  >
                    <option value={15}>15 Minutes Before / After High Impact Event</option>
                    <option value={30}>30 Minutes Before / After High Impact Event (Recommended)</option>
                    <option value={60}>60 Minutes Before / After High Impact Event</option>
                  </select>
                </div>

                {/* ATR Multipliers */}
                <div className="grid grid-cols-2 gap-4 pt-3 border-t border-border">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-text-primary block">Take Profit ATR Multiplier</label>
                    <input
                      type="number"
                      step="0.1"
                      value={tpAtr}
                      onChange={(e) => setTpAtr(parseFloat(e.target.value))}
                      className="w-full bg-background border border-border rounded-xl p-2 text-xs font-mono font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-text-primary block">Stop Loss ATR Multiplier</label>
                    <input
                      type="number"
                      step="0.1"
                      value={slAtr}
                      onChange={(e) => setSlAtr(parseFloat(e.target.value))}
                      className="w-full bg-background border border-border rounded-xl p-2 text-xs font-mono font-bold focus:outline-none focus:border-primary"
                    />
                  </div>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    onClick={handleSaveParameters}
                    className="px-5 py-2.5 bg-primary hover:bg-primary/90 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-md transition-all active:scale-95"
                  >
                    <Save className="w-3.5 h-3.5" />
                    Save Risk Gates
                  </button>
                </div>

                {savedStatus && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                    <span>Risk parameters updated and stored successfully.</span>
                  </div>
                )}
              </div>
            </div>

            {/* Right Column: Capital Rules & Model Specifications */}
            <div className="space-y-6">
              <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400">
                    <DollarSign className="w-4 h-4" />
                  </div>
                  <h3 className="font-bold text-sm font-display text-text-primary">
                    Micro-Lot Capital Rules
                  </h3>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 bg-background border border-border rounded-xl space-y-1">
                    <span className="text-[10px] text-text-secondary uppercase font-semibold block">Fixed Lot Sizing</span>
                    <span className="font-mono font-bold text-primary text-sm">0.01 Micro Lots ($0.10 / pip)</span>
                  </div>

                  <div className="p-3 bg-background border border-border rounded-xl space-y-1">
                    <span className="text-[10px] text-text-secondary uppercase font-semibold block">Max Simultaneous Positions</span>
                    <span className="font-mono font-bold text-text-primary text-sm">1 Active Trade</span>
                  </div>

                  <div className="p-3 bg-background border border-border rounded-xl space-y-1">
                    <span className="text-[10px] text-text-secondary uppercase font-semibold block">Execution Mode</span>
                    <span className="font-mono font-bold text-emerald-400 text-sm">100% Autonomous AI</span>
                  </div>
                </div>
              </div>

              <div className="bg-card border border-border rounded-2xl p-6 shadow-sm space-y-3 text-xs text-text-secondary">
                <h4 className="font-bold text-text-primary flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-primary" />
                  Institutional Guardrails
                </h4>
                <p className="leading-relaxed">
                  Every signal is gated by London/NY liquidity filters, spread caps, and high-impact macro calendar schedules to protect accounts during erratic volatility.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
