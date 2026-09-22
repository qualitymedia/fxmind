"use client";

import { ArrowUpRight, ArrowDownRight, Slash } from "lucide-react";

interface SignalCardProps {
  direction?: "LONG" | "SHORT" | null;
  status?: string;
}

export function SignalCard({ direction = "LONG", status = "ACTIVE" }: SignalCardProps) {
  const isLong = direction === "LONG";
  const isShort = direction === "SHORT";
  const isNoTrade = !direction || status === "NO_TRADE";

  const Icon = isLong ? ArrowUpRight : isShort ? ArrowDownRight : Slash;
  const text = isNoTrade ? "NO TRADE" : direction;
  const colorClass = isLong ? "text-positive" : isShort ? "text-negative" : "text-text-secondary";

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card flex items-center justify-between">
      <div>
        <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
          Signal Status
        </span>
        <span className={`text-base font-bold font-display block mt-0.5 ${colorClass}`}>
          {text}
        </span>
        <span className="text-[10px] text-text-secondary block">
          {isNoTrade ? "Gates Active" : "Setup Active"}
        </span>
      </div>

      <div className={`p-2 rounded-lg ${isLong ? "bg-positive-light text-positive" : isShort ? "bg-negative-light text-negative" : "bg-background text-text-secondary"}`}>
        <Icon className="w-4 h-4" />
      </div>
    </div>
  );
}
