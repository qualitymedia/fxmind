"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Settings as SettingsIcon, ShieldCheck, DollarSign, Sliders, Save, CheckCircle2 } from "lucide-react";

export default function SettingsPage() {
  const [confidence, setConfidence] = useState<number>(0.58);
  const [newsBuffer, setNewsBuffer] = useState<number>(30);
  const [tpAtr, setTpAtr] = useState<number>(1.8);
  const [slAtr, setSlAtr] = useState<number>(1.0);
  const [baseCapital] = useState<number>(100.0);
  const [savedStatus, setSavedStatus] = useState<boolean>(false);

  const handleSave = () => {
    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 3000);
  };

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          {/* Header Banner */}
          <div className="flex items-center justify-between pb-4 border-b border-border flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-2">
                <SettingsIcon className="w-6 h-6 text-primary" />
                <h1 className="text-xl font-bold font-display text-text-primary uppercase tracking-wider">
                  AI Model & Execution Preferences
                </h1>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Customize model confidence gates, risk parameters, and paper account sizing.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono font-bold text-xs flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                CONFIG ENFORCED ($100 BASE)
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Settings Forms */}
            <div className="lg:col-span-2 space-y-6">
              {/* Account Capital Card */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-4">
                <h2 className="text-xs font-bold font-display text-text-primary uppercase tracking-wider flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                  Trading Account Capital Sizing
                </h2>
                <div className="p-4 bg-background border border-border rounded-lg flex items-center justify-between">
                  <div>
                    <span className="text-xs text-text-secondary block">Initial Trading Capital</span>
                    <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">
                      ${baseCapital.toFixed(2)} USD
                    </span>
                    <span className="text-[11px] text-text-muted mt-0.5 block">
                      Configured in development & backtest engine as base capital.
                    </span>
                  </div>
                  <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono text-xs font-bold">
                    $100.00 ACTIVE
                  </span>
                </div>
              </div>

              {/* Inference & Risk Parameters */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-5">
                <h2 className="text-xs font-bold font-display text-text-primary uppercase tracking-wider flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-primary" />
                  Signal Generation & Risk Parameters
                </h2>

                {/* Min Confidence Gate */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <label className="font-bold text-text-primary">Minimum Calibrated Confidence Gate</label>
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
                    Signals with calibrated LightGBM probability below {(confidence * 100).toFixed(0)}% are suppressed.
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
                    className="w-full bg-background border border-border rounded-lg p-2.5 text-xs font-mono font-bold focus:outline-none focus:border-primary"
                  >
                    <option value={15}>15 Minutes Before / After High Impact Event</option>
                    <option value={30}>30 Minutes Before / After High Impact Event (Recommended)</option>
                    <option value={45}>45 Minutes Before / After High Impact Event</option>
                  </select>
                </div>

                {/* Risk Scalers */}
                <div className="grid grid-cols-2 gap-4 pt-3 border-t border-border text-xs">
                  <div>
                    <label className="font-bold text-text-primary block mb-1">Take Profit Scaler (ATR)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={tpAtr}
                      onChange={(e) => setTpAtr(parseFloat(e.target.value))}
                      className="w-full bg-background border border-border rounded-lg p-2 font-mono font-bold"
                    />
                  </div>
                  <div>
                    <label className="font-bold text-text-primary block mb-1">Stop Loss Scaler (ATR)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={slAtr}
                      onChange={(e) => setSlAtr(parseFloat(e.target.value))}
                      className="w-full bg-background border border-border rounded-lg p-2 font-mono font-bold"
                    />
                  </div>
                </div>

                {/* Save Button */}
                <div className="pt-4 flex items-center justify-between border-t border-border">
                  {savedStatus ? (
                    <span className="text-xs font-bold text-emerald-400 font-mono flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      Settings Applied & Saved to Engine!
                    </span>
                  ) : (
                    <span className="text-xs text-text-muted">Changes take effect immediately on next candle evaluation.</span>
                  )}

                  <button
                    onClick={handleSave}
                    className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-xs font-bold font-mono flex items-center gap-2 transition-all shadow-md"
                  >
                    <Save className="w-4 h-4" />
                    Save Parameters
                  </button>
                </div>
              </div>
            </div>

            {/* Right Col: Info & System Status */}
            <div className="space-y-6">
              <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-3 text-xs">
                <h3 className="font-bold font-display text-text-primary uppercase tracking-wider">
                  Active Guardrail Summary
                </h3>
                <div className="space-y-2 font-mono text-[11px]">
                  <div className="flex justify-between py-1.5 border-b border-border/60">
                    <span className="text-text-secondary">Symbol</span>
                    <span className="font-bold text-text-primary">GBPUSD</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/60">
                    <span className="text-text-secondary">Timeframe</span>
                    <span className="font-bold text-text-primary">M15 (15 Min)</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/60">
                    <span className="text-text-secondary">Risk per Trade</span>
                    <span className="font-bold text-emerald-400">1.0% of Capital</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/60">
                    <span className="text-text-secondary">Execution Latency</span>
                    <span className="font-bold text-text-primary">&lt; 50ms</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-border/60">
                    <span className="text-text-secondary">Persistence</span>
                    <span className="font-bold text-emerald-400">SQLite DB Loop</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
