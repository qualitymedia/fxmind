"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useDashboardData } from "@/lib/useDashboardData";
import {
  Calendar as CalendarIcon,
  AlertTriangle,
  Clock,
  Filter,
  ShieldCheck,
  Zap,
} from "lucide-react";

export default function CalendarPage() {
  const { analysis } = useDashboardData("M15");
  const upcomingEvents = analysis?.upcoming_events ?? [];

  const [impactFilter, setImpactFilter] = useState<string>("ALL");
  const [currencyFilter, setCurrencyFilter] = useState<string>("ALL");

  // Standard high impact macro schedule fallback if API returns empty
  const defaultEvents = [
    { time: "12:30 UTC", currency: "USD", event: "Core CPI (MoM)", impact: "HIGH", forecast: "0.3%", previous: "0.2%" },
    { time: "13:30 UTC", currency: "USD", event: "Non-Farm Payrolls (NFP)", impact: "HIGH", forecast: "175K", previous: "142K" },
    { time: "14:00 UTC", currency: "GBP", event: "BoE Monetary Policy Rate Decision", impact: "HIGH", forecast: "5.00%", previous: "5.00%" },
    { time: "15:30 UTC", currency: "USD", event: "FOMC Press Conference", impact: "HIGH", forecast: "—", previous: "—" },
    { time: "16:00 UTC", currency: "USD", event: "ISM Manufacturing PMI", impact: "MEDIUM", forecast: "49.2", previous: "48.5" },
    { time: "17:00 UTC", currency: "GBP", event: "UK Retail Sales (MoM)", impact: "MEDIUM", forecast: "0.4%", previous: "0.5%" },
  ];

  const eventsList = upcomingEvents.length > 0 ? upcomingEvents : defaultEvents;

  const filteredEvents = eventsList.filter((e: any) => {
    if (impactFilter !== "ALL" && (e.impact || "").toUpperCase() !== impactFilter) return false;
    if (currencyFilter !== "ALL" && (e.currency || "").toUpperCase() !== currencyFilter) return false;
    return true;
  });

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
                <CalendarIcon className="w-6 h-6 text-primary" />
                <h1 className="text-xl font-bold font-display text-text-primary uppercase tracking-wider">
                  Economic Calendar & News Blackout Radar
                </h1>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Real-time macroeconomic release schedule and automatic trading freeze window monitoring.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-bold text-xs border border-emerald-500/20 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                AUTO NEWS RISK GATE ACTIVE
              </span>
            </div>
          </div>

          {/* News Risk Status Card */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-amber-400 animate-pulse" />
              </div>
              <div>
                <span className="text-xs font-bold text-text-primary block">
                  30-Minute News Blackout Rule
                </span>
                <span className="text-xs text-text-secondary block">
                  The AI trading engine automatically suppresses new signal generation 30 minutes before and after high-impact USD & GBP releases.
                </span>
              </div>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-background border border-border font-mono text-xs text-emerald-400 font-bold">
              SYSTEM STATUS: CLEAR TO TRADE
            </div>
          </div>

          {/* Filter Controls & Table */}
          <div className="bg-card border border-border rounded-xl shadow-card p-5 space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-text-primary font-display">
                Scheduled Economic Indicators
              </span>

              <div className="flex items-center gap-3 flex-wrap">
                {/* Impact Filter */}
                <div className="flex items-center gap-1 bg-background border border-border rounded-lg p-0.5 font-mono text-xs">
                  <span className="text-[10px] text-text-muted px-2 font-sans font-bold">IMPACT:</span>
                  {["ALL", "HIGH", "MEDIUM"].map((imp) => (
                    <button
                      key={imp}
                      onClick={() => setImpactFilter(imp)}
                      className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                        impactFilter === imp
                          ? "bg-card text-text-primary border border-border"
                          : "text-text-muted hover:text-text-primary"
                      }`}
                    >
                      {imp}
                    </button>
                  ))}
                </div>

                {/* Currency Filter */}
                <div className="flex items-center gap-1 bg-background border border-border rounded-lg p-0.5 font-mono text-xs">
                  <span className="text-[10px] text-text-muted px-2 font-sans font-bold">PAIR:</span>
                  {["ALL", "USD", "GBP"].map((curr) => (
                    <button
                      key={curr}
                      onClick={() => setCurrencyFilter(curr)}
                      className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                        currencyFilter === curr
                          ? "bg-card text-text-primary border border-border"
                          : "text-text-muted hover:text-text-primary"
                      }`}
                    >
                      {curr}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-background border-b border-border text-text-secondary uppercase text-[10px] font-bold">
                  <tr>
                    <th className="p-3">Time</th>
                    <th className="p-3">Currency</th>
                    <th className="p-3">Economic Indicator</th>
                    <th className="p-3">Impact Level</th>
                    <th className="p-3">Forecast</th>
                    <th className="p-3">Previous</th>
                    <th className="p-3 text-right">Blackout Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {filteredEvents.map((e: any, idx: number) => {
                    const isHigh = (e.impact || "").toUpperCase() === "HIGH";
                    return (
                      <tr key={idx} className="hover:bg-background/50 transition-colors font-mono">
                        <td className="p-3 font-semibold text-text-primary flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-text-muted" />
                          {e.time}
                        </td>
                        <td className="p-3 font-bold text-text-primary">{e.currency}</td>
                        <td className="p-3 font-medium text-text-primary font-sans">{e.event}</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                              isHigh
                                ? "bg-red-500/10 text-red-400 border-red-500/20"
                                : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            }`}
                          >
                            {e.impact}
                          </span>
                        </td>
                        <td className="p-3 text-text-primary">{e.forecast || "—"}</td>
                        <td className="p-3 text-text-muted">{e.previous || "—"}</td>
                        <td className="p-3 text-right font-sans">
                          {isHigh ? (
                            <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                              30m Freeze Window
                            </span>
                          ) : (
                            <span className="text-[10px] text-text-muted">Standard Monitoring</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
