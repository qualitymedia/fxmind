"use client";

import { AlertTriangle, Calendar } from "lucide-react";

interface EconomicEvent {
  time?: string;
  currency?: string;
  event?: string;
  impact?: string;
  minutes_away?: number;
}

interface EconomicCalendarProps {
  events?: EconomicEvent[];
}

export function EconomicCalendarPanel({ events = [] }: EconomicCalendarProps) {
  const highImpact = events.find(
    (e) => (e.impact === "HIGH" || e.impact === "High") && (e.minutes_away ?? 999) < 30
  );

  const impactLabel = (impact?: string) => {
    const v = (impact ?? "").toUpperCase();
    if (v === "HIGH") return "High";
    if (v === "MEDIUM") return "Med";
    return "Low";
  };

  const impactClass = (impact?: string) => {
    const v = (impact ?? "").toUpperCase();
    if (v === "HIGH") return "bg-negative-light text-negative";
    if (v === "MEDIUM") return "bg-amber-100 text-amber-700";
    return "bg-background text-text-secondary";
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          Economic Calendar
        </h2>
        <span className="text-xs text-text-muted">Today UTC</span>
      </div>

      {events.length === 0 ? (
        <div className="py-6 flex flex-col items-center gap-2 text-xs text-text-muted">
          <Calendar className="w-6 h-6 opacity-40" />
          <span>No upcoming events detected for today.</span>
          <span className="text-[11px]">Calendar feed not connected — events require Forex Factory or Investing.com API.</span>
        </div>
      ) : (
        <div className="space-y-2.5 text-xs">
          {events.map((e, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between py-1 border-b border-border/40 last:border-0"
            >
              <div className="flex items-center gap-3">
                <span className="text-text-muted w-12 font-mono">{e.time ?? "—"}</span>
                <span className="font-bold text-text-primary w-8">{e.currency ?? "—"}</span>
                <span className="text-text-primary">{e.event ?? "—"}</span>
                {e.minutes_away != null && e.minutes_away < 60 && (
                  <span className="text-negative text-[10px] font-semibold">
                    {e.minutes_away}m
                  </span>
                )}
              </div>

              <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${impactClass(e.impact)}`}>
                {impactLabel(e.impact)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* High-impact warning banner */}
      {highImpact ? (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-negative flex-shrink-0 mt-0.5" />
          <div className="text-xs">
            <span className="font-bold text-text-primary block">
              High-impact event approaching
            </span>
            <span className="text-text-secondary block mt-0.5">
              {highImpact.currency} {highImpact.event} in ~{highImpact.minutes_away} min.
              AI analysis signal paused during news window.
            </span>
          </div>
        </div>
      ) : events.length > 0 ? (
        <div className="mt-4 p-3 bg-positive-light border border-positive/20 rounded-lg flex items-center gap-2 text-xs text-positive">
          <span className="font-semibold">News window is clear</span>
          <span className="text-positive/70">— no high-impact events in the next 30 min</span>
        </div>
      ) : null}
    </div>
  );
}
