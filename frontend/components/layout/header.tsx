"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import {
  Search,
  Bell,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Bot,
  ExternalLink,
  X,
  Clock,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  time: string;
  type: "signal" | "broker" | "system" | "risk";
  read: boolean;
  link?: string;
}

export function Header() {
  const [utcTime, setUtcTime] = useState<string>("");
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isNotifOpen, setIsNotifOpen] = useState<boolean>(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toISOString().substring(11, 19) + " UTC");
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setIsNotifOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <header className="h-16 bg-card border-b border-border px-3 sm:px-6 flex items-center justify-between flex-shrink-0 relative z-40">
      {/* Search Input */}
      <div className="relative hidden md:block w-80">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          placeholder="Search setups, regimes, or signals..."
          className="w-full bg-background border border-border rounded-xl pl-9 pr-4 py-2 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary transition-all shadow-inner"
        />
      </div>

      <div className="flex items-center gap-2 sm:gap-5 ml-auto">
        {/* Live Status Indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-text-secondary">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-semibold text-emerald-400">Live AI Feed</span>
          <span className="text-text-muted font-mono ml-1">{utcTime || "Syncing..."}</span>
        </div>

        {/* Notifications Icon & Interactive Popover */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setIsNotifOpen(!isNotifOpen)}
            className={`relative p-2 rounded-xl transition-all ${
              isNotifOpen
                ? "bg-primary/20 text-primary border border-primary/30"
                : "text-text-secondary hover:text-text-primary hover:bg-background border border-transparent"
            }`}
            title="Notifications & System Alerts"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 min-w-[16px] h-4 px-1 rounded-full bg-primary text-white text-[10px] font-extrabold flex items-center justify-center animate-pulse">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown Drawer */}
          {isNotifOpen && (
            <div className="absolute right-0 top-12 w-80 sm:w-96 bg-card border border-border/90 rounded-2xl shadow-2xl p-4 space-y-3 animate-in fade-in zoom-in-95 duration-150 z-50">
              {/* Dropdown Header */}
              <div className="flex items-center justify-between pb-2.5 border-b border-border">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-text-primary">Notifications</span>
                  {unreadCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-[10px] font-bold">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-[11px] text-text-secondary hover:text-primary transition-colors font-medium"
                  >
                    Mark all as read
                  </button>
                )}
              </div>

              {/* Notification List */}
              <div className="max-h-80 overflow-y-auto space-y-2 pr-1">
                {notifications.length > 0 ? (
                  notifications.map((item) => (
                    <div
                      key={item.id}
                      className={`p-3 rounded-xl border transition-all text-xs relative group ${
                        item.read
                          ? "bg-background/60 border-border text-text-secondary"
                          : "bg-primary/5 border-primary/25 text-text-primary shadow-sm"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2 mb-1">
                          {item.type === "broker" && (
                            <span className="w-5 h-5 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                              <Bot className="w-3 h-3" />
                            </span>
                          )}
                          {item.type === "signal" && (
                            <span className="w-5 h-5 rounded-md bg-primary/20 text-primary flex items-center justify-center flex-shrink-0">
                              <Zap className="w-3 h-3" />
                            </span>
                          )}
                          {item.type === "system" && (
                            <span className="w-5 h-5 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center flex-shrink-0">
                              <Sparkles className="w-3 h-3" />
                            </span>
                          )}
                          <span className="font-semibold text-text-primary truncate">
                            {item.title}
                          </span>
                        </div>
                        <button
                          onClick={() => clearNotification(item.id)}
                          className="opacity-0 group-hover:opacity-100 p-1 text-text-muted hover:text-text-primary transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>

                      <p className="text-[11px] text-text-secondary leading-relaxed pl-7">
                        {item.message}
                      </p>

                      <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-border/50 text-[10px] text-text-muted pl-7">
                        <span className="flex items-center gap-1">
                          <Clock className="w-2.5 h-2.5" /> {item.time}
                        </span>
                        {item.link && (
                          <Link
                            href={item.link}
                            onClick={() => setIsNotifOpen(false)}
                            className="text-primary hover:underline font-medium flex items-center gap-0.5"
                          >
                            View details <ExternalLink className="w-2.5 h-2.5" />
                          </Link>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-xs text-text-secondary space-y-1">
                    <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto" />
                    <p className="font-semibold text-text-primary">All caught up!</p>
                    <p className="text-[11px]">No active notifications.</p>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="pt-2 border-t border-border flex items-center justify-between text-[11px]">
                <span className="text-text-muted font-mono">FXMind Push Service</span>
                <Link
                  href="/signals"
                  onClick={() => setIsNotifOpen(false)}
                  className="text-primary hover:underline font-medium"
                >
                  Live Signal Feed &rarr;
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3 pl-3 border-l border-border">
          <div className="w-8 h-8 rounded-xl bg-primary/15 text-primary font-bold text-xs flex items-center justify-center border border-primary/30 shadow-sm">
            FX
          </div>
          <div className="text-left hidden sm:block">
            <span className="text-xs font-semibold text-text-primary block leading-none">
              Institutional User
            </span>
            <span className="text-[10px] text-text-secondary font-mono block mt-1 leading-none">
              PRO TRADER
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
