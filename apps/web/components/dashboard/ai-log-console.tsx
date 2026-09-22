"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchApi } from "@/lib/api";
import { Terminal, Filter, RefreshCw, Layers } from "lucide-react";

export interface LogItem {
  id: number;
  timestamp: string;
  category: "SIGNALS" | "PATTERNS" | "GATES" | "SYSTEM" | "DATA";
  level: "INFO" | "SUCCESS" | "WARNING" | "ERROR";
  message: string;
  details?: Record<string, any>;
}

export function AILogConsolePanel() {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>("ALL");
  const [loading, setLoading] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  const fetchLogs = useCallback(async () => {
    try {
      const url = activeCategory === "ALL" ? "/api/v1/logs?limit=40" : `/api/v1/logs?category=${activeCategory}&limit=40`;
      const data = await fetchApi<LogItem[]>(url);
      setLogs(data);
    } catch {
      // Silently retry
    } finally {
      setLoading(false);
    }
  }, [activeCategory]);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5_000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  const categoryColor = (cat: string) => {
    switch (cat) {
      case "SIGNALS":
        return "text-cyan-400 bg-cyan-400/10 border-cyan-400/20";
      case "PATTERNS":
        return "text-purple-400 bg-purple-400/10 border-purple-400/20";
      case "GATES":
        return "text-amber-400 bg-amber-400/10 border-amber-400/20";
      case "SYSTEM":
        return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20";
      default:
        return "text-slate-400 bg-slate-400/10 border-slate-400/20";
    }
  };

  const levelColor = (level: string) => {
    switch (level) {
      case "SUCCESS":
        return "text-emerald-400 font-bold";
      case "WARNING":
        return "text-amber-400 font-bold";
      case "ERROR":
        return "text-rose-400 font-bold";
      default:
        return "text-slate-300 font-medium";
    }
  };

  const formatTime = (ts: string) => {
    try {
      return new Date(ts).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      return "—";
    }
  };

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card font-mono text-xs">
      {/* Header & Filter Controls */}
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-primary" />
          <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
            AI System Execution Log
          </h2>
          <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded font-bold">
            LIVE FEED
          </span>
        </div>

        {/* Filter Category Tabs */}
        <div className="flex items-center gap-1 bg-background p-1 rounded-lg border border-border">
          {["ALL", "SIGNALS", "PATTERNS", "GATES", "SYSTEM"].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-2.5 py-1 rounded text-[10px] font-bold tracking-wider transition-colors ${
                activeCategory === cat
                  ? "bg-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Terminal View */}
      <div className="bg-[#090D16] border border-border/80 rounded-lg p-3 max-h-56 overflow-y-auto space-y-1.5 scrollbar-thin">
        {loading && logs.length === 0 && (
          <div className="py-8 text-center text-slate-500 animate-pulse flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin" />
            Connecting to AI background log stream…
          </div>
        )}

        {!loading && logs.length === 0 && (
          <div className="py-8 text-center text-slate-500">
            No system log events recorded for filter [{activeCategory}].
          </div>
        )}

        {logs.map((log) => (
          <div
            key={log.id}
            className="flex items-start gap-2 leading-relaxed hover:bg-white/[0.02] p-1 rounded transition-colors"
          >
            <span className="text-slate-500 flex-shrink-0 text-[10px]">
              [{formatTime(log.timestamp)}]
            </span>

            <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold border flex-shrink-0 ${categoryColor(log.category)}`}>
              {log.category}
            </span>

            <span className={`flex-1 break-words ${levelColor(log.level)}`}>
              {log.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
