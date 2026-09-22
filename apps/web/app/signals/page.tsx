"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useDashboardData } from "@/lib/useDashboardData";
import { Zap, ShieldCheck, Clock } from "lucide-react";

export default function SignalsPage() {
  const { analysis, loading, lastRefresh } = useDashboardData("M15");
  const signal = analysis?.signal ?? null;

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold font-display text-text-primary flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              Real-Time Signal Engine
            </h1>
            {signal?.model_version && (
              <span className="text-xs px-2.5 py-1 rounded-full bg-primary/10 text-primary font-mono font-semibold">
                {signal.model_version}
              </span>
            )}
          </div>

          {/* Current Live Active Signal Card */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <span className="text-xs font-bold text-text-secondary uppercase tracking-wider">
                Current Live Signal Evaluation
              </span>
              <span className="text-[11px] text-text-muted flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {lastRefresh ? `Evaluated ${lastRefresh.toLocaleTimeString()}` : "Evaluating..."}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="text-xs text-text-secondary">AI Market Bias</span>
                <span className={`text-lg font-bold block mt-1 ${
                  signal?.bias === "BULLISH" ? "text-positive" : signal?.bias === "BEARISH" ? "text-negative" : "text-text-primary"
                }`}>
                  {signal?.bias ?? "NEUTRAL"}
                </span>
              </div>
              <div>
                <span className="text-xs text-text-secondary">Calibrated Confidence</span>
                <span className="text-lg font-bold text-text-primary block mt-1">
                  {signal?.confidence != null ? `${(signal.confidence * 100).toFixed(1)}%` : "33.3%"}
                </span>
              </div>
              <div>
                <span className="text-xs text-text-secondary">Market Regime</span>
                <span className="text-lg font-bold text-text-primary block mt-1">
                  {signal?.regime ?? "RANGING"}
                </span>
              </div>
              <div>
                <span className="text-xs text-text-secondary">Trade Status</span>
                <span className={`inline-block px-2 py-0.5 mt-1 rounded text-xs font-bold ${
                  signal?.trade?.status === "ACTIVE"
                    ? "bg-positive/10 text-positive border border-positive/30"
                    : "bg-background text-text-muted border border-border"
                }`}>
                  {signal?.trade?.status ?? "NO_TRADE"}
                </span>
              </div>
            </div>

            {signal?.trade?.status === "ACTIVE" && (
              <div className="mt-4 pt-4 border-t border-border grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div>
                  <span className="text-text-secondary block">Entry Zone:</span>
                  <span className="text-text-primary font-bold">
                    {signal.trade.entry_low?.toFixed(4)} – {signal.trade.entry_high?.toFixed(4)}
                  </span>
                </div>
                <div>
                  <span className="text-text-secondary block">Stop Loss:</span>
                  <span className="text-negative font-bold">{signal.trade.stop_loss?.toFixed(4)}</span>
                </div>
                <div>
                  <span className="text-text-secondary block">Take Profit:</span>
                  <span className="text-positive font-bold">{signal.trade.take_profit?.toFixed(4)}</span>
                </div>
                <div>
                  <span className="text-text-secondary block">Risk/Reward:</span>
                  <span className="text-text-primary font-bold">1:{signal.trade.risk_reward?.toFixed(1)}</span>
                </div>
              </div>
            )}

            {/* Reasons / Decision Drivers */}
            {signal?.reasons && signal.reasons.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-wider block mb-2">
                  Key Decision Drivers
                </span>
                <div className="space-y-1.5">
                  {signal.reasons.map((r: any, idx: number) => {
                    const reasonText = typeof r === "string" ? r : r.reason ?? r.category ?? JSON.stringify(r);
                    const sentiment = typeof r === "object" ? r.sentiment : null;
                    const category = typeof r === "object" ? r.category : null;
                    const isSupportive = sentiment === "SUPPORTIVE" || sentiment === "CLEAR";
                    const isOpposing = sentiment === "OPPOSING";

                    return (
                      <div key={idx} className="flex items-start justify-between gap-2 text-xs">
                        <div className="flex items-start gap-2 text-text-secondary">
                          <span className="text-primary font-bold">•</span>
                          {category && (
                            <span className="font-semibold text-text-primary w-28 flex-shrink-0">{category}</span>
                          )}
                          <span>{reasonText}</span>
                        </div>
                        {sentiment && (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold flex-shrink-0 ${
                              isSupportive
                                ? "bg-positive/10 text-positive border border-positive/20"
                                : isOpposing
                                ? "bg-negative/10 text-negative border border-negative/20"
                                : "bg-background text-text-secondary border border-border"
                            }`}
                          >
                            {sentiment}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
