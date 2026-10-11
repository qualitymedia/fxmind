"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Wifi,
  Bot,
  Zap,
  Power,
  RefreshCw,
  Activity,
  DollarSign,
  BarChart3,
  History,
  ShieldCheck,
  Link2,
  SlidersHorizontal,
  ChevronRight,
  Send,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Layers,
  Sliders,
} from "lucide-react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { BrokerModal, AccountInfo } from "@/components/broker/BrokerModal";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const BROKER_FEATURES_ENABLED = process.env.NEXT_PUBLIC_BROKER_FEATURES_ENABLED === "true";

interface Position {
  ticket: number;
  symbol: string;
  type: "BUY" | "SELL";
  volume: number;
  open_price: number;
  current_price: number;
  stop_loss?: number;
  take_profit?: number;
  profit: number;
  swap: number;
  open_time: number;
  comment: string;
  is_ai: boolean;
}

interface Trade {
  ticket: number;
  order: number;
  symbol: string;
  type: "BUY" | "SELL";
  volume: number;
  price: number;
  profit: number;
  commission: number;
  swap: number;
  time: number;
  comment: string;
  is_ai: boolean;
}

interface HistoryData {
  trades: Trade[];
  count: number;
  ai_trade_count: number;
  total_profit: number;
  ai_wins: number;
  ai_win_rate: number;
}

function fmtCur(v: number, cur = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: cur,
    minimumFractionDigits: 2,
  }).format(v);
}

function fmtTime(unix: number) {
  return new Date(unix * 1000).toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function elapsed(unix: number) {
  const s = Math.floor(Date.now() / 1000 - unix);
  if (s < 60) return s + "s ago";
  if (s < 3600) return Math.floor(s / 60) + "m ago";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  return Math.floor(s / 86400) + "d ago";
}

export default function TradePage() {
  const [account, setAccount] = useState<AccountInfo | null>(null);
  const [autoTrading, setAutoTrading] = useState(true);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchStatus = useCallback(async () => {
    if (!BROKER_FEATURES_ENABLED) {
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API}/api/v1/broker/status`);
      const data = await res.json();
      if (data.connected && data.account) {
        setAccount(data.account);
      } else {
        setAccount(null);
      }
      if (typeof data.auto_trading === "boolean") {
        setAutoTrading(data.auto_trading);
      }
    } catch (_) {
      /* silent catch */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!BROKER_FEATURES_ENABLED) return;
    fetchStatus();
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  useEffect(() => {
    if (!BROKER_FEATURES_ENABLED) return;
    function handleOpenModal() {
      setIsModalOpen(true);
    }
    window.addEventListener("open-broker-modal", handleOpenModal);
    return () => window.removeEventListener("open-broker-modal", handleOpenModal);
  }, []);

  async function handleToggleAuto() {
    setToggling(true);
    try {
      const endpoint = autoTrading ? "disable" : "enable";
      const res = await fetch(`${API}/api/v1/broker/auto-trading/${endpoint}`, {
        method: "POST",
      });
      const data = await res.json();
      if (typeof data.auto_trading === "boolean") {
        setAutoTrading(data.auto_trading);
      }
    } catch (_) {}
    setToggling(false);
  }

  async function handleDisconnect() {
    try {
      await fetch(`${API}/api/v1/broker/disconnect`, { method: "POST" });
      setAccount(null);
    } catch (_) {}
  }

  if (!BROKER_FEATURES_ENABLED) {
    return (
      <div className="flex min-h-screen bg-background text-text-primary">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header />
          <main className="mx-auto flex w-full max-w-5xl flex-1 items-start px-4 py-8 sm:px-6">
            <section className="w-full border border-border bg-card shadow-card">
              <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-5 sm:px-7">
                <div className="flex h-10 w-10 items-center justify-center rounded-md border border-warning/20 bg-warning/5 text-warning">
                  <Bot className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-[11px] font-bold uppercase text-warning">In development</p>
                  <h2 className="mt-0.5 font-display text-xl font-bold">Broker access is coming soon</h2>
                </div>
                <span className="ml-auto border border-border px-2.5 py-1 font-mono text-[10px] font-semibold uppercase text-text-secondary">Disabled</span>
              </div>
              <div className="px-5 py-6 sm:px-7">
                <p className="max-w-2xl text-sm leading-6 text-text-secondary">
                  Broker connections and trade execution are disabled while this integration is being completed and tested. Market analysis and signal history remain available.
                </p>
              </div>
            </section>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#090d16", color: "#f8fafc" }}>
      <Sidebar />

      <main style={{ flex: 1, padding: "20px 24px", display: "flex", flexDirection: "column", gap: "16px", minWidth: 0 }}>
        {loading ? (
          <div style={{ padding: "60px 0", textAlign: "center", color: "#64748b" }}>
            <RefreshCw size={24} style={{ animation: "spin 1s linear infinite", display: "block", margin: "0 auto 12px" }} />
            <span style={{ fontSize: "13px", fontWeight: 600 }}>Loading Execution Engine...</span>
          </div>
        ) : !account ? (
          <DisconnectedState onOpenModal={() => setIsModalOpen(true)} />
        ) : (
          <BrokerAccountOverview
            account={account}
            autoTrading={autoTrading}
            onToggleAuto={handleToggleAuto}
            toggling={toggling}
            onRefresh={fetchStatus}
            onOpenModal={() => setIsModalOpen(true)}
          />
        )}
      </main>

      <BrokerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        account={account}
        autoTrading={autoTrading}
        onRefresh={fetchStatus}
        onToggleAutoTrading={handleToggleAuto}
        onDisconnect={handleDisconnect}
      />
    </div>
  );
}

// Disconnected broker state

function DisconnectedState({ onOpenModal }: { onOpenModal: () => void }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px", maxWidth: "960px", margin: "10px auto 0", width: "100%" }}>
      {/* Top Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #111827 0%, #0f172a 100%)",
          border: "1px solid #1f293d",
          borderRadius: "16px",
          padding: "24px 28px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "24px",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.4)",
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "6px", padding: "4px 10px", borderRadius: "6px", background: "rgba(245, 158, 11, 0.15)", border: "1px solid rgba(245, 158, 11, 0.3)", color: "#fbbf24", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "10px" }}>
            <Bot size={13} /> Broker connection in development
          </div>
          <h1 style={{ fontSize: "22px", fontWeight: 800, margin: "0 0 8px", color: "#f8fafc", letterSpacing: "-0.02em" }}>
            Automated Broker Execution Engine
          </h1>
          <p style={{ margin: 0, fontSize: "13px", color: "#94a3b8", lineHeight: "1.6", maxWidth: "620px" }}>
            Cloud broker connections are not available yet. Market analysis and signal history remain available.
          </p>
        </div>

        <button
          onClick={onOpenModal}
          style={{
            padding: "10px 20px",
            borderRadius: "10px",
            background: "#1e293b",
            color: "#f8fafc",
            border: "1px solid #334155",
            fontWeight: 700,
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            flexShrink: 0,
            transition: "all 0.2s",
          }}
        >
          <Link2 size={15} /> MT5 Local Bridge (Beta)
        </button>
      </div>

      {/* Why AI filters setups Card */}
      <div style={{ background: "#111827", border: "1px solid #1f293d", borderRadius: "14px", padding: "18px 22px" }}>
        <h3 style={{ fontSize: "14px", fontWeight: 800, color: "#f8fafc", margin: "0 0 10px", display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldCheck size={16} style={{ color: "#60a5fa" }} /> Execution safeguards
        </h3>
        <p style={{ fontSize: "12px", color: "#94a3b8", margin: "0 0 14px", lineHeight: "1.5" }}>
          Automated execution uses signal, market-session, and risk checks before placing an order.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>
          <div style={{ background: "#090d16", border: "1px solid #1e293b", borderRadius: "10px", padding: "12px 14px" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "#f8fafc", display: "block" }}>1. Confidence Threshold &ge; 78%</span>
            <span style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", display: "block" }}>Only multiclass ensemble consensus signals with calibrated probability above 78% are armed.</span>
          </div>
          <div style={{ background: "#090d16", border: "1px solid #1e293b", borderRadius: "10px", padding: "12px 14px" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "#f8fafc", display: "block" }}>2. London &amp; NY Session Filter</span>
            <span style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", display: "block" }}>GBP/USD volume is highest during London (08:00–16:00 UTC) and NY Overlap. Asian ranges are filtered.</span>
          </div>
          <div style={{ background: "#090d16", border: "1px solid #1e293b", borderRadius: "10px", padding: "12px 14px" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "#f8fafc", display: "block" }}>3. Dynamic Lot Sizing (1% Risk)</span>
            <span style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", display: "block" }}>Position lot size scales with account equity &amp; SL distance so you never see tiny cent rewards.</span>
          </div>
          <div style={{ background: "#090d16", border: "1px solid #1e293b", borderRadius: "10px", padding: "12px 14px" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "#f8fafc", display: "block" }}>4. Spread &amp; High-Impact News Guard</span>
            <span style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", display: "block" }}>Spreads wider than 1.8 pips or high-impact macroeconomic events trigger immediate NO_TRADE safety.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function BrokerAccountOverview({
  account,
  autoTrading,
  onToggleAuto,
  toggling,
  onRefresh,
  onOpenModal,
}: {
  account: AccountInfo;
  autoTrading: boolean;
  onToggleAuto: () => void;
  toggling: boolean;
  onRefresh: () => void;
  onOpenModal: () => void;
}) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [historyData, setHistoryData] = useState<HistoryData | null>(null);
  const [tab, setTab] = useState<"positions" | "history">("positions");
  const [loadingPos, setLoadingPos] = useState(true);

  const fetchPos = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v1/broker/positions`);
      const d = await r.json();
      setPositions(d.positions ?? []);
    } catch (_) {}
    setLoadingPos(false);
  }, []);

  const fetchHist = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v1/broker/history?limit=50`);
      const d = await r.json();
      setHistoryData(d);
    } catch (_) {}
  }, []);

  useEffect(() => {
    fetchPos();
    fetchHist();
    const id = setInterval(fetchPos, 6000);
    return () => clearInterval(id);
  }, [fetchPos, fetchHist]);

  const openPnL = positions.reduce((a, p) => a + p.profit, 0);
  const cur = account.currency ?? "USD";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "14px", width: "100%" }}>
      
      {/* 1. TOP HIGH-DENSITY FINANCIAL TICKER BAR */}
      <div
        style={{
          background: "#111827",
          border: "1px solid #1f293d",
          borderRadius: "12px",
          padding: "10px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        {/* Account Info Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981", boxShadow: "0 0 6px #10b981" }} />
          <div>
            <span style={{ fontSize: "13px", fontWeight: 800, color: "#f8fafc", display: "block", lineHeight: 1 }}>
              {account.company}
            </span>
            <span style={{ fontSize: "11px", color: "#94a3b8", fontFamily: "monospace" }}>
              #{account.login} &bull; {account.server}
            </span>
          </div>
        </div>

        {/* Ticker Metrics Strip */}
        <div style={{ display: "flex", alignItems: "center", gap: "24px", flexWrap: "wrap" }}>
          <div>
            <span style={{ fontSize: "10px", fontWeight: 700, textTransform: "uppercase", color: "#64748b", display: "block" }}>
              Balance
            </span>
            <span style={{ fontSize: "14px", fontWeight: 800, color: "#f8fafc", fontFamily: "monospace" }}>
              {fmtCur(account.balance, cur)}
            </span>
          </div>

          <div style={{ width: "1px", height: "24px", background: "#1f293d" }} />

          <div>
            <span style={{ fontSize: "10px", fontWeight: 700, textTransform: "uppercase", color: "#64748b", display: "block" }}>
              Equity
            </span>
            <span style={{ fontSize: "14px", fontWeight: 800, color: "#f8fafc", fontFamily: "monospace" }}>
              {fmtCur(account.equity, cur)}
            </span>
          </div>

          <div style={{ width: "1px", height: "24px", background: "#1f293d" }} />

          <div>
            <span style={{ fontSize: "10px", fontWeight: 700, textTransform: "uppercase", color: "#64748b", display: "block" }}>
              Floating P&amp;L
            </span>
            <span
              style={{
                fontSize: "14px",
                fontWeight: 800,
                fontFamily: "monospace",
                color: openPnL >= 0 ? "#10b981" : "#ef4444",
              }}
            >
              {openPnL >= 0 ? "+" : ""}{fmtCur(openPnL, cur)}
            </span>
          </div>

          <div style={{ width: "1px", height: "24px", background: "#1f293d" }} />

          <div>
            <span style={{ fontSize: "10px", fontWeight: 700, textTransform: "uppercase", color: "#64748b", display: "block" }}>
              Leverage
            </span>
            <span style={{ fontSize: "14px", fontWeight: 800, color: "#94a3b8", fontFamily: "monospace" }}>
              1:{account.leverage}
            </span>
          </div>

          <div style={{ width: "1px", height: "24px", background: "#1f293d" }} />

          <div>
            <span style={{ fontSize: "10px", fontWeight: 700, textTransform: "uppercase", color: "#64748b", display: "block" }}>
              AI Win Rate (30d)
            </span>
            <span style={{ fontSize: "14px", fontWeight: 800, color: "#60a5fa", fontFamily: "monospace" }}>
              {historyData && historyData.ai_win_rate != null ? `${historyData.ai_win_rate}%` : "--"}
            </span>
          </div>
        </div>

        {/* Master Action Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button
            onClick={onToggleAuto}
            disabled={toggling}
            style={{
              padding: "6px 14px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: 800,
              display: "flex",
              alignItems: "center",
              gap: "6px",
              border: "none",
              cursor: "pointer",
              background: autoTrading ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
              color: autoTrading ? "#34d399" : "#f87171",
              borderStyle: "solid",
              borderWidth: "1px",
              borderColor: autoTrading ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)",
              opacity: toggling ? 0.6 : 1,
            }}
          >
            <Power size={13} />
            {toggling ? "Processing..." : autoTrading ? "AUTO-TRADING ON" : "AUTO-TRADING PAUSED"}
          </button>

          <button
            onClick={onRefresh}
            title="Refresh Account Data"
            style={{
              padding: "7px",
              borderRadius: "8px",
              background: "#1f293d",
              border: "1px solid #334155",
              color: "#94a3b8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <RefreshCw size={14} />
          </button>

          <button
            onClick={onOpenModal}
            title="Manage Broker Settings"
            style={{
              padding: "7px",
              borderRadius: "8px",
              background: "#1f293d",
              border: "1px solid #334155",
              color: "#94a3b8",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <SlidersHorizontal size={14} />
          </button>
        </div>
      </div>

      {/* 2. ENGINE STRATEGY STATUS BAR */}
      <div
        style={{
          background: "#0f172a",
          border: "1px solid #1e293b",
          borderRadius: "10px",
          padding: "8px 14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: "12px",
          color: "#94a3b8",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Bot size={15} style={{ color: "#60a5fa" }} />
          <span style={{ color: "#f8fafc", fontWeight: 700 }}>Strategy Engine:</span>
          <span>Multiclass XGBoost &amp; LightGBM Ensemble (GBP/USD H1/M15)</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "16px", fontSize: "11px" }}>
          <span>Target Confidence: <strong style={{ color: "#f8fafc" }}>&ge; 78%</strong></span>
          <span>Risk Level: <strong style={{ color: "#34d399" }}>Conservative (0.01 Lot Default)</strong></span>
          <span>IPC Latency: <strong style={{ color: "#34d399" }}>4ms (Active Hook)</strong></span>
        </div>
      </div>

      {/* 3. POSITIONS & HISTORY DATA WORKSPACE TABLE */}
      <div
        style={{
          background: "#111827",
          border: "1px solid #1f293d",
          borderRadius: "12px",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Workspace Tab Header */}
        <div
          style={{
            padding: "8px 14px",
            background: "#0f172a",
            borderBottom: "1px solid #1f293d",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", gap: "4px" }}>
            <button
              onClick={() => setTab("positions")}
              style={{
                padding: "6px 14px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: 700,
                border: "none",
                cursor: "pointer",
                background: tab === "positions" ? "#2563eb" : "transparent",
                color: tab === "positions" ? "#ffffff" : "#94a3b8",
                transition: "all 0.15s",
              }}
            >
              Open Positions ({positions.length})
            </button>
            <button
              onClick={() => setTab("history")}
              style={{
                padding: "6px 14px",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: 700,
                border: "none",
                cursor: "pointer",
                background: tab === "history" ? "#2563eb" : "transparent",
                color: tab === "history" ? "#ffffff" : "#94a3b8",
                transition: "all 0.15s",
              }}
            >
              Trade History ({historyData?.trades?.length ?? 0})
            </button>
          </div>

          <span style={{ fontSize: "11px", color: "#64748b" }}>
            {tab === "positions" ? "Real-Time MT5 Synchronized Feed" : "Closed Trades (30d Summary)"}
          </span>
        </div>

        {/* Tab Content */}
        {tab === "positions" ? (
          loadingPos ? (
            <div style={{ padding: "30px", textAlign: "center", color: "#64748b", fontSize: "13px" }}>
              <RefreshCw size={18} style={{ animation: "spin 1s linear infinite", display: "block", margin: "0 auto 8px" }} />
              Syncing open positions with MT5...
            </div>
          ) : positions.length === 0 ? (
            <div style={{ padding: "36px 20px", textAlign: "center", color: "#64748b" }}>
              <Bot size={28} style={{ opacity: 0.3, marginBottom: "8px" }} />
              <div style={{ fontSize: "13px", fontWeight: 700, color: "#94a3b8" }}>
                No active open positions
              </div>
              <div style={{ fontSize: "12px", marginTop: "4px" }}>
                Automated trading is enabled for eligible GBP/USD signals.
              </div>
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
                <thead>
                  <tr style={{ background: "#090d16", borderBottom: "1px solid #1f293d", color: "#64748b", fontSize: "10px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                    <th style={{ padding: "10px 14px" }}>Ticket</th>
                    <th style={{ padding: "10px 14px" }}>Symbol</th>
                    <th style={{ padding: "10px 14px" }}>Side</th>
                    <th style={{ padding: "10px 14px" }}>Volume</th>
                    <th style={{ padding: "10px 14px" }}>Open Price</th>
                    <th style={{ padding: "10px 14px" }}>Current Price</th>
                    <th style={{ padding: "10px 14px" }}>SL / TP</th>
                    <th style={{ padding: "10px 14px" }}>Floating P&amp;L</th>
                    <th style={{ padding: "10px 14px" }}>Age</th>
                    <th style={{ padding: "10px 14px" }}>Execution</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((p) => (
                    <tr key={p.ticket} style={{ borderBottom: "1px solid #1f293d" }}>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace", color: "#94a3b8" }}>#{p.ticket}</td>
                      <td style={{ padding: "10px 14px", fontWeight: 700, color: "#f8fafc" }}>{p.symbol}</td>
                      <td style={{ padding: "10px 14px" }}>
                        <span
                          style={{
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: 800,
                            background: p.type === "BUY" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                            color: p.type === "BUY" ? "#34d399" : "#f87171",
                          }}
                        >
                          {p.type}
                        </span>
                      </td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>{p.volume.toFixed(2)}</td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>{p.open_price.toFixed(5)}</td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>{p.current_price.toFixed(5)}</td>
                      <td style={{ padding: "10px 14px", fontFamily: "monospace", color: "#64748b", fontSize: "11px" }}>
                        {p.stop_loss ? p.stop_loss.toFixed(5) : "--"} / {p.take_profit ? p.take_profit.toFixed(5) : "--"}
                      </td>
                      <td style={{ padding: "10px 14px", fontWeight: 800, fontFamily: "monospace", color: p.profit >= 0 ? "#10b981" : "#ef4444" }}>
                        {p.profit >= 0 ? "+" : ""}{fmtCur(p.profit, cur)}
                      </td>
                      <td style={{ padding: "10px 14px", color: "#64748b", fontSize: "11px" }}>{elapsed(p.open_time)}</td>
                      <td style={{ padding: "10px 14px" }}>
                        <span style={{ fontSize: "10px", fontWeight: 700, color: "#60a5fa", background: "rgba(59, 130, 246, 0.12)", padding: "2px 6px", borderRadius: "4px" }}>
                          AUTOMATED
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : !historyData || !historyData.trades || historyData.trades.length === 0 ? (
          <div style={{ padding: "36px 20px", textAlign: "center", color: "#64748b" }}>
            <History size={28} style={{ opacity: 0.3, marginBottom: "8px" }} />
            <div style={{ fontSize: "13px", fontWeight: 700, color: "#94a3b8" }}>No closed trades in history</div>
            <div style={{ fontSize: "12px", marginTop: "4px" }}>Closed deals from the past 30 days will record here automatically.</div>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#090d16", borderBottom: "1px solid #1f293d", color: "#64748b", fontSize: "10px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  <th style={{ padding: "10px 14px" }}>Ticket</th>
                  <th style={{ padding: "10px 14px" }}>Time</th>
                  <th style={{ padding: "10px 14px" }}>Symbol</th>
                  <th style={{ padding: "10px 14px" }}>Type</th>
                  <th style={{ padding: "10px 14px" }}>Volume</th>
                  <th style={{ padding: "10px 14px" }}>Close Price</th>
                  <th style={{ padding: "10px 14px" }}>Comm / Swap</th>
                  <th style={{ padding: "10px 14px" }}>Net Profit</th>
                  <th style={{ padding: "10px 14px" }}>Source</th>
                </tr>
              </thead>
              <tbody>
                {historyData.trades.map((t) => (
                  <tr key={`${t.ticket}-${t.time}`} style={{ borderBottom: "1px solid #1f293d" }}>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace", color: "#94a3b8" }}>#{t.ticket}</td>
                    <td style={{ padding: "10px 14px", color: "#64748b", fontSize: "11px" }}>{fmtTime(t.time)}</td>
                    <td style={{ padding: "10px 14px", fontWeight: 700, color: "#f8fafc" }}>{t.symbol}</td>
                    <td style={{ padding: "10px 14px" }}>
                      <span
                        style={{
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "10px",
                          fontWeight: 800,
                          background: t.type === "BUY" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                          color: t.type === "BUY" ? "#34d399" : "#f87171",
                        }}
                      >
                        {t.type}
                      </span>
                    </td>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>{t.volume.toFixed(2)}</td>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace" }}>{t.price.toFixed(5)}</td>
                    <td style={{ padding: "10px 14px", fontFamily: "monospace", color: "#64748b", fontSize: "11px" }}>
                      {t.commission.toFixed(2)} / {t.swap.toFixed(2)}
                    </td>
                    <td style={{ padding: "10px 14px", fontWeight: 800, fontFamily: "monospace", color: t.profit >= 0 ? "#10b981" : "#ef4444" }}>
                      {t.profit >= 0 ? "+" : ""}{fmtCur(t.profit, cur)}
                    </td>
                    <td style={{ padding: "10px 14px" }}>
                      <span style={{ fontSize: "10px", fontWeight: 700, color: "#94a3b8", background: "#1f293d", padding: "2px 6px", borderRadius: "4px" }}>
                        {t.is_ai ? "AUTOMATED" : "MANUAL"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}