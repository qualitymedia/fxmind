"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Zap,
  Activity,
  Calendar,
  BarChart3,
  Bell,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Signals", href: "/signals", icon: Zap },
  { name: "Activity", href: "/logs", icon: Activity, badge: "LIVE" },
  { name: "Calendar", href: "/calendar", icon: Calendar },
  { name: "Performance", href: "/performance", icon: BarChart3 },
  { name: "Alerts", href: "/alerts", icon: Bell, badge: 3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-card border-r border-border min-h-screen flex flex-col justify-between p-4 flex-shrink-0">
      <div>
        {/* Brand */}
        <div className="flex items-center gap-2 px-3 py-4 mb-4">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold font-display text-lg">
            FX
          </div>
          <div>
            <span className="font-bold text-text-primary text-lg font-display tracking-tight block">
              FXMind
            </span>
            <span className="text-xs text-text-secondary font-medium block">
              GBP/USD AI Assistant
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-text-secondary hover:bg-background hover:text-text-primary"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full font-mono ${
                      item.badge === "LIVE"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
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

      {/* Verified Live Feed Status */}
      <div className="p-3 bg-background rounded-lg border border-border flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-positive animate-pulse" />
        <div>
          <span className="text-xs font-semibold text-text-primary block">
            LIVE FEED &bull; VERIFIED
          </span>
          <span className="text-[11px] text-text-secondary block">
            High-Frequency Forex Feed
          </span>
        </div>
      </div>
    </aside>
  );
}
