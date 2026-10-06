"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import {
  Send,
  Users,
  Sparkles,
  Zap,
  CheckCircle2,
  ShieldCheck,
  TrendingUp,
  MessageSquare,
  Bell,
  ArrowRight,
  ExternalLink,
  Bot,
  Layers,
  Award,
} from "lucide-react";

export default function CommunityPage() {
  // Telegram community invite link (users can customize or join directly)
  const TELEGRAM_COMMUNITY_URL = "https://t.me/FXMindOfficial";

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Header />

        <main className="p-6 md:p-8 space-y-8 max-w-6xl mx-auto w-full">
          {/* Hero Section */}
          <div className="relative rounded-3xl p-8 md:p-10 border border-sky-500/30 bg-gradient-to-br from-sky-950/40 via-card to-card shadow-2xl overflow-hidden">
            {/* Background Glow Accents */}
            <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-sky-500/10 blur-3xl pointer-events-none" />
            <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-primary/10 blur-3xl pointer-events-none" />

            <div className="relative z-10 space-y-6 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-500/15 border border-sky-500/30 text-sky-400 text-xs font-bold font-mono">
                <Send className="w-3.5 h-3.5" />
                OFFICIAL TELEGRAM COMMUNITY
              </div>

              <div className="space-y-3">
                <h1 className="text-3xl md:text-4xl font-extrabold font-display tracking-tight text-text-primary">
                  Connect With The FXMind Trading Community
                </h1>
                <p className="text-sm md:text-base text-text-secondary leading-relaxed">
                  Join our exclusive Telegram channel to receive instant institutional GBP/USD signals, live London &amp; New York session briefings, macroeconomic analysis, and community discussions.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-4 pt-2">
                <a
                  href={TELEGRAM_COMMUNITY_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3.5 rounded-2xl bg-[#229ED9] hover:bg-[#1e8ec3] text-white font-bold text-sm flex items-center gap-2.5 transition-all shadow-lg shadow-sky-500/25 active:scale-95 group"
                >
                  <Send className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  Join Official Telegram Channel
                  <ExternalLink className="w-3.5 h-3.5 opacity-80" />
                </a>

                <div className="flex items-center gap-2 text-xs text-text-secondary">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="font-semibold text-text-primary">2,400+ Active Members</span>
                </div>
              </div>
            </div>
          </div>

          {/* Perks & Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-6 rounded-2xl bg-card border border-border shadow-sm space-y-3 hover:border-primary/40 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary">
                <Zap className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-text-primary">Instant Signal Alerts</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Receive instant push alerts the millisecond an ACTIVE signal is verified by the ensemble model with calibrated probabilities and entry geometry.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-card border border-border shadow-sm space-y-3 hover:border-primary/40 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/25 flex items-center justify-center text-sky-400">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-text-primary">Session Briefings</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Daily pre-London and pre-New York macroeconomic overviews, high-impact news roadmaps, and key institutional watch levels.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-card border border-border shadow-sm space-y-3 hover:border-primary/40 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-base text-text-primary">Zero Setup Required</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                No complex bot tokens or developer keys required. Simply tap Join on your phone or PC and you are connected to the live feed immediately.
              </p>
            </div>
          </div>

          {/* Live Preview of What Community Members Receive */}
          <div className="rounded-3xl border border-border bg-card p-6 md:p-8 space-y-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <span className="w-10 h-10 rounded-2xl bg-[#229ED9]/15 border border-[#229ED9]/30 flex items-center justify-center text-[#229ED9]">
                  <Send className="w-5 h-5" />
                </span>
                <div>
                  <h2 className="text-lg font-bold font-display text-text-primary">
                    Live Community Feed Preview
                  </h2>
                  <p className="text-xs text-text-secondary">
                    Example institutional broadcast sent directly to the Telegram channel
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                BROADCAST VERIFIED
              </span>
            </div>

            {/* Telegram Message Simulation Card */}
            <div className="max-w-xl mx-auto rounded-2xl bg-[#17212b] border border-[#232e3c] p-5 text-white shadow-xl space-y-3.5 font-sans">
              <div className="flex items-center justify-between text-xs text-[#6c7883] border-b border-[#232e3c] pb-2">
                <span className="font-bold text-[#40a7e3] flex items-center gap-1.5">
                  <Bot className="w-3.5 h-3.5" /> FXMind AI Alpha v2
                </span>
                <span>Today at 08:30 UTC</span>
              </div>

              <div className="space-y-2 text-sm">
                <p className="font-bold text-emerald-400 text-base">
                  🟢 NEW ACTIVE SIGNAL &bull; GBP/USD (M15)
                </p>
                <div className="p-3 rounded-xl bg-[#202b36] border border-[#2a3744] space-y-1.5 text-xs font-mono">
                  <p><span className="text-zinc-400">Direction:</span> <span className="font-bold text-emerald-400">BUY / LONG</span></p>
                  <p><span className="text-zinc-400">Confidence:</span> <span className="font-bold text-white">74.2% (Very Strong)</span></p>
                  <p><span className="text-zinc-400">Entry Gate:</span> 1.26450 &mdash; 1.26490</p>
                  <p><span className="text-zinc-400">Stop Loss:</span> 1.26250 (20.0 pips)</p>
                  <p><span className="text-zinc-400">Take Profit:</span> 1.26890 (44.0 pips)</p>
                  <p><span className="text-zinc-400">Risk/Reward:</span> 1:2.2</p>
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">
                  💡 <strong>Reasoning:</strong> Bullish divergence on RSI(14), Volume Profile Point of Control bounce, and Clean macroeconomic buffer before London Open.
                </p>
              </div>

              <div className="pt-2 border-t border-[#232e3c] flex items-center justify-between text-[11px] text-[#6c7883]">
                <span>Automated Broadcast &bull; Institutional Risk Filter</span>
                <span className="text-[#40a7e3]">FXMind System</span>
              </div>
            </div>
          </div>

          {/* Direct CTA */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <h3 className="font-bold text-base text-text-primary">Want to discuss trades with other members?</h3>
              <p className="text-xs text-text-secondary">
                Our Telegram channel features a dedicated discussion group for verified members.
              </p>
            </div>
            <a
              href={TELEGRAM_COMMUNITY_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="px-5 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-white font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 flex-shrink-0"
            >
              <Send className="w-3.5 h-3.5" /> Join Free On Telegram
            </a>
          </div>
        </main>
      </div>
    </div>
  );
}
