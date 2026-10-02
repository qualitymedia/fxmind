"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Bell, ShieldCheck, Zap, AlertCircle, CheckCircle2, Sliders } from "lucide-react";

export default function AlertsPage() {
  const [rules, setRules] = useState([
    {
      id: "rule-1",
      title: "High Confidence AI Trade Signal (>60%)",
      description: "Trigger real-time alert whenever the LightGBM model outputs confidence >= 60.0% with valid SMC entry zone.",
      category: "SIGNAL",
      active: true,
    },
    {
      id: "rule-2",
      title: "High Impact Economic Release Warning",
      description: "Send risk warning 15 minutes prior to USD NFP, CPI, and BoE interest rate announcements.",
      category: "RISK",
      active: true,
    },
    {
      id: "rule-3",
      title: "Paper Trade Resolution Notification",
      description: "Notify immediately when a paper position hits Take Profit, Stop Loss, or expires.",
      category: "EXECUTION",
      active: true,
    },
    {
      id: "rule-4",
      title: "Market Regime Change Alert",
      description: "Alert when market state transitions between Trending, Ranging, or High Volatility.",
      category: "REGIME",
      active: false,
    },
  ]);

  const toggleRule = (id: string) => {
    setRules((prev) =>
      prev.map((r) => (r.id === id ? { ...r, active: !r.active } : r))
    );
  };

  const alertHistory = [
    {
      time: "20 mins ago",
      title: "Paper Position Closed (TARGET_HIT)",
      message: "SHORT GBP/USD closed @ 1.32259. Realized PnL: +13.9p ($13.90)",
      type: "SUCCESS",
    },
    {
      time: "1 hour ago",
      title: "High-Probability Signal Generated",
      message: "LONG setup on GBP/USD (Confidence: 68.4%, RR: 1:2.10)",
      type: "INFO",
    },
    {
      time: "3 hours ago",
      title: "Economic Event Approaching",
      message: "USD Core CPI release in 15 minutes. News blackout gate active.",
      type: "WARNING",
    },
  ];

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
                <Bell className="w-6 h-6 text-primary" />
                <h1 className="text-xl font-bold font-display text-text-primary uppercase tracking-wider">
                  AI Alert Rules & Real-Time Notification Center
                </h1>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Configure automated push notifications, execution alerts, and risk guardrails.
              </p>
            </div>

            <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono font-bold text-xs flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              SYSTEM NOTIFIERS READY
            </span>
          </div>

          {/* Active Rules Grid */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold font-display text-text-primary uppercase tracking-wider flex items-center gap-2">
                <Sliders className="w-4 h-4 text-primary" />
                Automated Notification Guardrails
              </h2>
            </div>

            <div className="space-y-3">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-background border border-border/80 hover:border-primary/30 transition-all flex-wrap gap-4"
                >
                  <div className="flex-1 min-w-[250px]">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-text-primary">{rule.title}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                        {rule.category}
                      </span>
                    </div>
                    <p className="text-xs text-text-secondary mt-1">{rule.description}</p>
                  </div>

                  <button
                    onClick={() => toggleRule(rule.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                      rule.active
                        ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                        : "bg-card text-text-muted border border-border"
                    }`}
                  >
                    {rule.active ? "ACTIVE" : "DISABLED"}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Alert History Stream */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-3">
            <h2 className="text-xs font-bold font-display text-text-primary uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              Recent System Notification Log
            </h2>

            <div className="space-y-2">
              {alertHistory.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 rounded-lg bg-background border border-border/60 text-xs font-mono"
                >
                  {item.type === "SUCCESS" && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />}
                  {item.type === "INFO" && <Zap className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />}
                  {item.type === "WARNING" && <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />}

                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-text-primary">{item.title}</span>
                      <span className="text-[10px] text-text-muted">{item.time}</span>
                    </div>
                    <p className="text-text-secondary text-[11px] mt-0.5">{item.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
