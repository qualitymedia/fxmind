"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Zap,
  BarChart3,
  Settings,
  Bot,
  Sparkles,
  ChevronRight,
  SlidersHorizontal,
  type LucideIcon,
} from "lucide-react";
import { BrokerModal, AccountInfo } from "@/components/broker/BrokerModal";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const BROKER_FEATURES_ENABLED = process.env.NEXT_PUBLIC_BROKER_FEATURES_ENABLED === "true";

const NAV_ITEMS: Array<{ name: string; href: string; icon: LucideIcon; badge?: string }> = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Signals", href: "/signals", icon: Zap },
  { name: "Insights", href: "/calendar", icon: Sparkles },
  { name: "Performance", href: "/performance", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [account, setAccount] = useState<AccountInfo | null>(null);
  const [autoTrading, setAutoTrading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchBrokerStatus = useCallback(async () => {
    if (!BROKER_FEATURES_ENABLED) return;
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
      /* silent */
    }
  }, []);

  useEffect(() => {
    if (!BROKER_FEATURES_ENABLED) return;
    fetchBrokerStatus();
    const interval = setInterval(fetchBrokerStatus, 10000);
    return () => clearInterval(interval);
  }, [fetchBrokerStatus]);

  async function handleToggleAutoTrading() {
    if (!BROKER_FEATURES_ENABLED) return;
    try {
      const endpoint = autoTrading ? "disable" : "enable";
      const res = await fetch(`${API}/api/v1/broker/auto-trading/${endpoint}`, { method: "POST" });
      const data = await res.json();
      if (typeof data.auto_trading === "boolean") {
        setAutoTrading(data.auto_trading);
      }
    } catch (_) {
      /* silent */
    }
  }

  async function handleDisconnect() {
    if (!BROKER_FEATURES_ENABLED) return;
    try {
      await fetch(`${API}/api/v1/broker/disconnect`, { method: "POST" });
      setAccount(null);
    } catch (_) {
      /* silent */
    }
  }

  return (
    <>
      <aside className="hidden md:flex w-60 bg-card border-r border-border h-screen sticky top-0 flex-col justify-between p-3.5 flex-shrink-0 z-30 select-none overflow-hidden">
        {/* Top: Brand & Navigation */}
        <div className="space-y-3.5">
          {/* Brand */}
          <div className="flex items-center gap-2.5 px-2 py-1.5">
            <div className="w-8 h-8 rounded-xl bg-primary flex items-center justify-center text-white font-bold font-display text-base shadow-md shadow-primary/30 flex-shrink-0">
              FX
            </div>
            <div className="min-w-0">
              <span className="font-bold text-text-primary text-base font-display tracking-tight block truncate">
                FXMind
              </span>
              <span className="text-[11px] text-text-secondary font-medium block truncate">
                GBP/USD Market Analysis
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-0.5">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/");
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-primary/10 text-primary font-semibold"
                      : "text-text-secondary hover:bg-background hover:text-text-primary"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`px-1.5 py-0.2 text-[9px] font-bold rounded-full font-mono ${
                        item.badge === "LIVE"
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : item.badge === "VIP"
                          ? "bg-[#229ED9]/20 text-[#229ED9] border border-[#229ED9]/30"
                          : "bg-negative text-white"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Lower Sidebar Section */}
        <div className="space-y-2 pt-2.5 border-t border-border">
          <div
            onClick={() => router.push("/trade")}
            className="p-2.5 rounded-xl bg-gradient-to-b from-primary/10 via-card to-card border border-primary/25 hover:border-primary/50 cursor-pointer transition-all shadow-sm group"
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center text-primary flex-shrink-0">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div>
                  <span className="text-[11px] font-bold text-text-primary block leading-tight">
                    Broker connection
                  </span>
                  <span className="text-[9px] text-text-secondary block">
                    Broker linking
                  </span>
                </div>
              </div>
              <span className="px-1.5 py-0.5 text-[9px] font-extrabold uppercase rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                SOON
              </span>
            </div>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                router.push("/trade");
              }}
              className="w-full py-1 px-2 rounded-lg bg-primary/20 hover:bg-primary/30 border border-primary/30 text-primary text-[10px] font-bold flex items-center justify-center gap-1 transition-colors"
            >
              <Sparkles className="w-2.5 h-2.5" /> Broker access details &rarr;
            </button>
          </div>

          {/* 3. Verified Live Feed Status */}
          <div className="p-1.5 px-2 bg-background rounded-lg border border-border flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-positive animate-pulse flex-shrink-0" />
            <div className="min-w-0">
              <span className="text-[10px] font-semibold text-text-primary block leading-tight truncate">
                FXMIND &bull; M15 MARKET DESK
              </span>
            </div>
          </div>

        </div>
      </aside>

      {/* Broker Management Modal */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-md px-2 py-2">
        <div className="grid grid-cols-5 gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex flex-col items-center justify-center rounded-xl px-1 py-2 text-[10px] transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                <Icon className="w-4 h-4 mb-1" />
                <span className="truncate max-w-[52px] text-center">{item.name}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {BROKER_FEATURES_ENABLED && <BrokerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        account={account}
        autoTrading={autoTrading}
        onRefresh={fetchBrokerStatus}
        onToggleAutoTrading={handleToggleAutoTrading}
        onDisconnect={handleDisconnect}
      />}
    </>
  );
}
