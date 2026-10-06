"use client";

import { useState } from "react";
import {
  Wifi,
  AlertCircle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  LogOut,
  ShieldCheck,
  Bot,
  Power,
  Sparkles,
  X,
  ExternalLink,
  Send,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TELEGRAM_COMMUNITY_URL = "https://t.me/FXMindOfficial";

export interface AccountInfo {
  login: number;
  server: string;
  company: string;
  balance: number;
  equity: number;
  currency: string;
  leverage: number;
}

interface BrokerModalProps {
  isOpen: boolean;
  onClose: () => void;
  account: AccountInfo | null;
  autoTrading: boolean;
  onRefresh: () => void;
  onToggleAutoTrading: () => Promise<void>;
  onDisconnect: () => Promise<void>;
}

export function BrokerModal({
  isOpen,
  onClose,
  account,
  autoTrading,
  onRefresh,
  onToggleAutoTrading,
  onDisconnect,
}: BrokerModalProps) {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [server, setServer] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [connError, setConnError] = useState("");
  const [toggling, setToggling] = useState(false);

  if (!isOpen) return null;

  const isConnected = !!account;

  async function handleConnect(e: React.FormEvent) {
    e.preventDefault();
    setConnecting(true);
    setConnError("");
    try {
      const res = await fetch(`${API}/api/v1/broker/connect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: parseInt(login), password, server }),
      });
      const data = await res.json();
      if (data.success) {
        onRefresh();
        onClose();
      } else {
        setConnError(data.error ?? "Connection failed. Check your MT5 credentials.");
      }
    } catch (_) {
      setConnError("Cannot reach server. Ensure API is running on port 8000.");
    } finally {
      setConnecting(false);
    }
  }

  async function handleToggle() {
    setToggling(true);
    await onToggleAutoTrading();
    setToggling(false);
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        background: "rgba(0, 0, 0, 0.82)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "580px",
          background: "linear-gradient(145deg, #0f172a 0%, #0b0f17 100%)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: "24px",
          padding: "24px",
          boxShadow: "0 25px 60px -10px rgba(0, 0, 0, 0.95), 0 0 35px rgba(59, 130, 246, 0.12)",
          color: "#f9fafb",
          maxHeight: "90vh",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        {/* Top Glowing Gradient Accent Line */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: "15%",
            right: "15%",
            height: "2px",
            background: "linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.8), rgba(16, 185, 129, 0.8), transparent)",
            borderRadius: "2px",
          }}
        />

        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingBottom: "16px",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "14px",
                background: "rgba(37, 99, 235, 0.15)",
                border: "1px solid rgba(59, 130, 246, 0.3)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#60a5fa",
                boxShadow: "0 0 15px rgba(37, 99, 235, 0.2)",
              }}
            >
              <Bot size={22} />
            </div>
            <div>
              <h2
                style={{
                  fontSize: "18px",
                  fontWeight: 800,
                  margin: 0,
                  color: "#f9fafb",
                  letterSpacing: "-0.02em",
                }}
              >
                MetaTrader 5 Auto-Pilot Link
              </h2>
              <p style={{ fontSize: "12px", margin: "2px 0 0", color: "#9ca3af" }}>
                Autonomous Algorithmic Execution &amp; Live Broker Synchronization
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: "8px",
              borderRadius: "10px",
              background: "rgba(255, 255, 255, 0.05)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              color: "#9ca3af",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.12)";
              e.currentTarget.style.color = "#ffffff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.05)";
              e.currentTarget.style.color = "#9ca3af";
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Telegram Community Quick Link Banner */}
        <div
          style={{
            padding: "14px 16px",
            borderRadius: "16px",
            background: "linear-gradient(90deg, rgba(34, 158, 217, 0.15), rgba(15, 23, 42, 0.7))",
            border: "1px solid rgba(34, 158, 217, 0.35)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "10px",
                background: "#229ED9",
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                boxShadow: "0 0 12px rgba(34, 158, 217, 0.4)",
              }}
            >
              <Send size={16} />
            </div>
            <div style={{ minWidth: 0 }}>
              <p style={{ margin: 0, fontSize: "13px", fontWeight: 700, color: "#f9fafb" }}>
                Official Telegram Community
              </p>
              <p style={{ margin: "2px 0 0", fontSize: "11px", color: "#9ca3af" }}>
                Join for live setup broadcasts &amp; discussions
              </p>
            </div>
          </div>
          <a
            href={TELEGRAM_COMMUNITY_URL}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "7px 14px",
              borderRadius: "10px",
              background: "#229ED9",
              color: "#ffffff",
              fontWeight: 700,
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              textDecoration: "none",
              boxShadow: "0 4px 12px rgba(34, 158, 217, 0.3)",
              flexShrink: 0,
            }}
          >
            Join <ExternalLink size={13} />
          </a>
        </div>

        {isConnected && account ? (
          /* Connected State */
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Live Status Header */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "16px",
                borderRadius: "16px",
                background: "rgba(16, 185, 129, 0.08)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <CheckCircle2 size={24} style={{ color: "#34d399", flexShrink: 0 }} />
                <div>
                  <p style={{ margin: 0, fontWeight: 700, fontSize: "14px", color: "#f9fafb" }}>
                    {account.company} — #{account.login}
                  </p>
                  <p style={{ margin: "2px 0 0", fontSize: "11px", color: "#34d399", fontFamily: "monospace" }}>
                    {account.server}
                  </p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <button
                  onClick={onRefresh}
                  title="Refresh Balance"
                  style={{
                    padding: "8px",
                    borderRadius: "10px",
                    background: "rgba(255,255,255,0.06)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    color: "#9ca3af",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <RefreshCw size={15} />
                </button>
                <button
                  onClick={async () => {
                    await onDisconnect();
                    onRefresh();
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 12px",
                    borderRadius: "10px",
                    fontSize: "12px",
                    fontWeight: 700,
                    color: "#f87171",
                    background: "rgba(239, 68, 68, 0.12)",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    cursor: "pointer",
                  }}
                >
                  <LogOut size={14} /> Disconnect
                </button>
              </div>
            </div>

            {/* AI Auto-Trading Master Switch Card */}
            <div
              style={{
                padding: "16px",
                borderRadius: "16px",
                background: autoTrading
                  ? "linear-gradient(135deg, rgba(6, 78, 59, 0.4), rgba(15, 23, 42, 0.8))"
                  : "rgba(15, 23, 42, 0.6)",
                border: `1px solid ${autoTrading ? "rgba(52, 211, 153, 0.4)" : "rgba(255, 255, 255, 0.08)"}`,
                boxShadow: autoTrading ? "0 8px 20px rgba(6, 78, 59, 0.3)" : "none",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px", flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: "220px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <span style={{ fontSize: "14px", fontWeight: 800, color: "#f9fafb" }}>
                      AI Auto-Trading Mode
                    </span>
                    {autoTrading ? (
                      <span
                        style={{
                          padding: "2px 8px",
                          borderRadius: "9999px",
                          fontSize: "10px",
                          fontWeight: 800,
                          background: "#22c55e",
                          color: "#000000",
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                          letterSpacing: "0.5px",
                        }}
                      >
                        <Sparkles size={10} /> ACTIVE (ON)
                      </span>
                    ) : (
                      <span
                        style={{
                          padding: "2px 8px",
                          borderRadius: "9999px",
                          fontSize: "10px",
                          fontWeight: 700,
                          background: "rgba(255,255,255,0.1)",
                          color: "#9ca3af",
                        }}
                      >
                        PAUSED (OFF)
                      </span>
                    )}
                  </div>
                  <p style={{ margin: 0, fontSize: "12px", color: "#9ca3af", lineHeight: "1.5" }}>
                    {autoTrading
                      ? "AI automatically executes trades on your MT5 account for every confirmed high-confidence signal."
                      : "Auto-trading is paused. If you want to trade manually, place orders directly in your MT5 desktop app."}
                  </p>
                </div>

                <button
                  onClick={handleToggle}
                  disabled={toggling}
                  style={{
                    padding: "10px 16px",
                    borderRadius: "12px",
                    fontWeight: 800,
                    fontSize: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                    border: autoTrading ? "1px solid rgba(255,255,255,0.15)" : "none",
                    background: autoTrading ? "rgba(255,255,255,0.08)" : "linear-gradient(90deg, #22c55e, #16a34a)",
                    color: autoTrading ? "#f9fafb" : "#000000",
                    boxShadow: autoTrading ? "none" : "0 4px 14px rgba(34, 197, 94, 0.4)",
                    flexShrink: 0,
                  }}
                >
                  {toggling ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Power size={14} />
                  )}
                  {autoTrading ? "Pause Auto-Trading" : "Enable Auto-Trading"}
                </button>
              </div>
            </div>

            {/* Account Metrics Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px" }}>
              <div
                style={{
                  padding: "12px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                }}
              >
                <span style={{ fontSize: "10px", textTransform: "uppercase", fontWeight: 700, color: "#6b7280", display: "block" }}>
                  Balance
                </span>
                <span style={{ fontSize: "15px", fontWeight: 800, color: "#60a5fa", display: "block", marginTop: "2px", fontFamily: "monospace" }}>
                  {account.currency} {account.balance.toLocaleString()}
                </span>
              </div>
              <div
                style={{
                  padding: "12px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                }}
              >
                <span style={{ fontSize: "10px", textTransform: "uppercase", fontWeight: 700, color: "#6b7280", display: "block" }}>
                  Equity
                </span>
                <span style={{ fontSize: "15px", fontWeight: 800, color: "#f9fafb", display: "block", marginTop: "2px", fontFamily: "monospace" }}>
                  {account.currency} {account.equity.toLocaleString()}
                </span>
              </div>
              <div
                style={{
                  padding: "12px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                }}
              >
                <span style={{ fontSize: "10px", textTransform: "uppercase", fontWeight: 700, color: "#6b7280", display: "block" }}>
                  Leverage
                </span>
                <span style={{ fontSize: "15px", fontWeight: 800, color: "#f9fafb", display: "block", marginTop: "2px", fontFamily: "monospace" }}>
                  1:{account.leverage}
                </span>
              </div>
              <div
                style={{
                  padding: "12px",
                  borderRadius: "14px",
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                }}
              >
                <span style={{ fontSize: "10px", textTransform: "uppercase", fontWeight: 700, color: "#6b7280", display: "block" }}>
                  Floating P&amp;L
                </span>
                <span
                  style={{
                    fontSize: "15px",
                    fontWeight: 800,
                    display: "block",
                    marginTop: "2px",
                    fontFamily: "monospace",
                    color: account.equity - account.balance >= 0 ? "#4ade80" : "#f87171",
                  }}
                >
                  {account.currency} {(account.equity - account.balance).toFixed(2)}
                </span>
              </div>
            </div>

            {/* Algo Trading Reminder */}
            <div
              style={{
                padding: "12px 14px",
                borderRadius: "14px",
                background: "rgba(245, 158, 11, 0.1)",
                border: "1px solid rgba(245, 158, 11, 0.25)",
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                fontSize: "12px",
                color: "#fef3c7",
              }}
            >
              <ShieldCheck size={16} style={{ color: "#fbbf24", flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Tip:</strong> Ensure the <strong>&quot;Algo Trading&quot;</strong> button in your MT5 desktop toolbar is green to permit algorithmic executions.
              </span>
            </div>
          </div>
        ) : (
          /* Disconnected / Connect Form State */
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <p style={{ fontSize: "12px", color: "#9ca3af", margin: 0, lineHeight: "1.5" }}>
              Connect any MetaTrader 5 broker (Demo or Live) to enable 100% autonomous AI execution. If MT5 is already open on this computer, credentials link automatically.
            </p>

            <form onSubmit={handleConnect} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  MT5 Account Login Number
                </label>
                <input
                  type="number"
                  value={login}
                  onChange={(e) => setLogin(e.target.value)}
                  placeholder="e.g. 5056865113"
                  required
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "12px",
                    background: "#0b0f17",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    color: "#f9fafb",
                    fontSize: "13px",
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  Trading Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Your MT5 account password"
                  required
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "12px",
                    background: "#0b0f17",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    color: "#f9fafb",
                    fontSize: "13px",
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "11px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  Broker Server
                </label>
                <input
                  type="text"
                  value={server}
                  onChange={(e) => setServer(e.target.value)}
                  placeholder="e.g. MetaQuotes-Demo, ICMarkets-Live, etc."
                  required
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "12px",
                    background: "#0b0f17",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    color: "#f9fafb",
                    fontSize: "13px",
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              {connError && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    padding: "12px",
                    borderRadius: "12px",
                    background: "rgba(239, 68, 68, 0.12)",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    fontSize: "12px",
                    color: "#f87171",
                  }}
                >
                  <AlertCircle size={16} style={{ flexShrink: 0, marginTop: "1px" }} />
                  <span>{connError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={connecting}
                style={{
                  width: "100%",
                  padding: "12px 20px",
                  borderRadius: "12px",
                  background: "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)",
                  color: "#ffffff",
                  fontWeight: 800,
                  fontSize: "14px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  border: "none",
                  cursor: "pointer",
                  boxShadow: "0 4px 16px rgba(37, 99, 235, 0.4)",
                  marginTop: "6px",
                  opacity: connecting ? 0.6 : 1,
                }}
              >
                {connecting ? (
                  <><Loader2 size={16} className="animate-spin" /> Connecting Broker...</>
                ) : (
                  <><Wifi size={16} /> Link MT5 Account</>
                )}
              </button>
            </form>

            <div
              style={{
                padding: "12px 14px",
                borderRadius: "14px",
                background: "rgba(59, 130, 246, 0.1)",
                border: "1px solid rgba(59, 130, 246, 0.25)",
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                fontSize: "12px",
                color: "#93c5fd",
              }}
            >
              <ShieldCheck size={16} style={{ flexShrink: 0, marginTop: "2px", color: "#60a5fa" }} />
              <span>
                Start with a demo account to observe the AI&apos;s auto-executions in real-time with zero risk.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
