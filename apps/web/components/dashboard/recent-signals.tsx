"use client";

import type { SignalRow } from "@/lib/useDashboardData";

interface RecentSignalsProps {
  signals?: SignalRow[];
  loading?: boolean;
}

export function RecentSignalsPanel({ signals = [], loading = false }: RecentSignalsProps) {
  const statusColor = (status: string) => {
    if (status === "ACTIVE") return "bg-primary/10 text-primary border border-primary/20";
    if (status === "TARGET_HIT") return "bg-positive-light text-positive border border-positive/20";
    if (status === "STOP_HIT") return "bg-negative-light text-negative border border-negative/20";
    return "bg-background text-text-muted border border-border";
  };

  const formatTime = (ts: string) => {
    try {
      return new Date(ts).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "—";
    }
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
            Recent Signals
          </h2>
          <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-mono font-semibold">
            H1 MTF + Range Engine
          </span>
        </div>
        <span className="text-xs text-text-muted font-medium">
          {loading ? "Fetching…" : `${signals.length} signal${signals.length !== 1 ? "s" : ""}`}
        </span>
      </div>

      {loading && (
        <div className="py-6 text-center text-xs text-text-muted animate-pulse">
          Loading live signals…
        </div>
      )}

      {!loading && signals.length === 0 && (
        <div className="py-6 text-center text-xs text-text-muted">
          No signals recorded in this session yet.
        </div>
      )}

      {!loading && signals.length > 0 && (
        <div className="space-y-2.5 text-xs">
          {signals.map((s, idx) => {
            const isBull = s.bias === "BULLISH";
            const isBear = s.bias === "BEARISH";
            const tradeStatus = s.status ?? "NO_TRADE";
            const stratType = s.strategy_type === "MEAN_REVERSION" ? "RANGE REVERSION" : s.strategy_type === "TREND_FOLLOWING" ? "TREND FOLLOW" : null;

            return (
              <div
                key={s.id ?? idx}
                className="flex items-center justify-between py-1.5 border-b border-border/40 last:border-0 gap-2"
              >
                <span className="font-mono text-text-muted w-12 flex-shrink-0">
                  {formatTime(s.timestamp)}
                </span>

                <span
                  className={`font-semibold flex items-center gap-1 w-20 flex-shrink-0 ${
                    isBull ? "text-positive" : isBear ? "text-negative" : "text-text-secondary"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                      isBull ? "bg-positive" : isBear ? "bg-negative" : "bg-text-secondary"
                    }`}
                  />
                  {s.bias}
                </span>

                <div className="flex items-center gap-1.5 w-32 flex-shrink-0 truncate">
                  <span className="text-text-secondary truncate">
                    {s.regime ?? "—"}
                  </span>
                  {stratType && (
                    <span className="text-[9px] bg-secondary/10 text-secondary px-1 py-0.5 rounded font-mono uppercase font-bold flex-shrink-0">
                      {stratType}
                    </span>
                  )}
                </div>

                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${statusColor(
                    tradeStatus
                  )}`}
                >
                  {tradeStatus}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
