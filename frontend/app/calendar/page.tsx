"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { fetchApi } from "@/lib/api";
import { useDashboardData } from "@/lib/useDashboardData";
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  Clock3,
  ExternalLink,
  Landmark,
  Newspaper,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";

interface CalendarEvent {
  id: number;
  timestamp: string;
  currency: string;
  event: string;
  importance: string;
  actual: number | string | null;
  forecast: number | string | null;
  previous: number | string | null;
  all_day?: boolean;
  url?: string;
}

const BROKER_LISTINGS = [
  {
    name: "Pepperstone",
    category: "Forex and CFDs",
    description: "Explore available currency markets, platforms, fees, and account terms for your region.",
  },
  {
    name: "Deriv",
    category: "Online trading",
    description: "Review the products, platform options, and local account requirements before registering.",
  },
  {
    name: "OANDA",
    category: "Forex trading",
    description: "Compare supported instruments, pricing, and regional availability on the broker's site.",
  },
];
interface NewsHeadline {
  id: string;
  title: string;
  publisher: string;
  url: string;
  published_at: string | null;
  image_url: string | null;
  related_tickers: string[];
}

function formatDate(timestamp: string | null, options: Intl.DateTimeFormatOptions) {
  if (!timestamp) return "Time unavailable";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "Time unavailable";
  return new Intl.DateTimeFormat(undefined, { ...options, timeZone: "UTC" }).format(date);
}

function Sparkline({ values, bullish }: { values: number[]; bullish: boolean }) {
  const points = useMemo(() => {
    if (values.length < 2) return "";
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    return values
      .map((value, index) => {
        const x = (index / (values.length - 1)) * 320;
        const y = 54 - ((value - min) / range) * 44;
        return `${x},${y}`;
      })
      .join(" ");
  }, [values]);

  return (
    <svg viewBox="0 0 320 60" preserveAspectRatio="none" className="h-14 w-full" aria-label="Recent GBP/USD price movement" role="img">
      <path d="M0 30 H320" stroke="#e4e9e7" strokeDasharray="3 5" />
      {points && (
        <polyline
          points={points}
          fill="none"
          stroke={bullish ? "#11836f" : "#d4564b"}
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      )}
    </svg>
  );
}

function SectionHeading({
  icon: Icon,
  title,
  action,
  onAction,
}: {
  icon: typeof Zap;
  title: string;
  action: string;
  onAction?: () => void;
}) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.12em] text-text-secondary">
        <Icon className="h-4 w-4 text-primary" />
        {title}
      </h2>
      {onAction ? (
        <button type="button" onClick={onAction} className="text-xs font-semibold text-primary hover:text-primary/75">
          {action}
        </button>
      ) : (
        <Link href="/signals" className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/75">
          {action}<ArrowRight className="h-3.5 w-3.5" />
        </Link>
      )}
    </div>
  );
}

export default function InsightsPage() {
  const { signals, candles } = useDashboardData("M15");
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [headlines, setHeadlines] = useState<NewsHeadline[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [newsLoading, setNewsLoading] = useState(true);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [reloadVersion, setReloadVersion] = useState(0);
  const [showAllEvents, setShowAllEvents] = useState(false);
  const [showAllNews, setShowAllNews] = useState(false);

  useEffect(() => {
    let active = true;
    setEventsLoading(true);
    setEventsError(null);
    fetchApi<CalendarEvent[]>("/api/v1/calendar?days=14")
      .then((data) => {
        if (active) setEvents(data.filter((event) => ["GBP", "USD"].includes(event.currency.toUpperCase())));
      })
      .catch((error: Error) => {
        if (active) setEventsError(error.message || "Events are unavailable.");
      })
      .finally(() => {
        if (active) setEventsLoading(false);
      });
    return () => { active = false; };
  }, [reloadVersion]);

  useEffect(() => {
    let active = true;
    setNewsLoading(true);
    setNewsError(null);
    fetchApi<NewsHeadline[]>("/api/v1/news?limit=10")
      .then((data) => {
        if (active) setHeadlines(data);
      })
      .catch((error: Error) => {
        if (active) setNewsError(error.message || "News is unavailable.");
      })
      .finally(() => {
        if (active) setNewsLoading(false);
      });
    return () => { active = false; };
  }, [reloadVersion]);

  const chartValues = candles.slice(-36).map((candle) => candle.close);
  const activeSignals = signals.filter((signal) => signal.status === "ACTIVE" && signal.direction);
  const visibleEvents = showAllEvents ? events : events.slice(0, 3);
  const featuredHeadline = headlines[0] ?? null;
  const newsList = headlines.slice(featuredHeadline ? 1 : 0);
  const visibleNews = showAllNews ? newsList : newsList.slice(0, 3);

  return (
    <div className="flex min-h-screen bg-[#f5f7f6] text-text-primary md:bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="mx-auto w-full max-w-5xl space-y-7 px-4 pb-24 pt-5 sm:px-6 sm:pt-7">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-primary">GBP/USD market desk</p>
              <h1 className="mt-1 font-display text-2xl font-bold text-text-primary sm:text-3xl">Insights</h1>
              <p className="mt-1 text-sm text-text-secondary">Market stories, signal notes, and upcoming GBP/USD releases.</p>
            </div>
            <button
              type="button"
              title="Refresh insights"
              aria-label="Refresh insights"
              onClick={() => setReloadVersion((version) => version + 1)}
              disabled={eventsLoading || newsLoading}
              className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-border bg-card text-text-secondary transition-colors hover:text-primary disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${eventsLoading || newsLoading ? "animate-spin" : ""}`} />
            </button>
          </div>

          <section>
            <SectionHeading icon={Zap} title="Trading signals" action="Show more" />
            {signals.length ? (
              <div className="-mx-4 flex snap-x gap-3 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0">
                {signals.slice(0, 8).map((signal) => {
                  const bullish = signal.bias === "BULLISH";
                  const DirectionIcon = bullish ? ArrowUpRight : ArrowDownRight;
                  return (
                    <article key={signal.id} className="w-[min(66vw,270px)] shrink-0 snap-start overflow-hidden rounded-xl border border-border bg-card shadow-[0_3px_14px_rgba(20,40,35,0.05)]">
                      <div className="flex items-center justify-between px-3.5 pt-3">
                        <span className="text-[10px] font-medium text-text-muted">
                          {formatDate(signal.timestamp, { weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} UTC
                        </span>
                        <span className="rounded-sm bg-background px-1.5 py-0.5 text-[9px] font-bold text-text-secondary">M15</span>
                      </div>
                      <div className="mt-2 border-y border-border/70 bg-[#f8faf9] px-2.5">
                        <Sparkline values={chartValues} bullish={bullish} />
                      </div>
                      <div className="p-3.5">
                        <p className="line-clamp-2 min-h-10 text-sm font-semibold leading-5 text-text-primary">
                          GBP/USD {signal.direction ?? signal.bias.toLowerCase()} · {signal.regime.toLowerCase().replaceAll("_", " ")}
                        </p>
                        <div className="mt-3 flex items-center justify-between">
                          <span className={`inline-flex items-center gap-1 rounded-sm px-2 py-1 text-[10px] font-bold uppercase text-white ${bullish ? "bg-[#168775]" : "bg-[#c94d44]"}`}>
                            <DirectionIcon className="h-3 w-3" />{signal.direction ?? signal.bias}
                          </span>
                          <span className="font-mono text-xs text-text-secondary">{(signal.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="rounded-xl border border-border bg-card px-4 py-8 text-center">
                <Sparkles className="mx-auto h-5 w-5 text-text-muted" />
                <p className="mt-2 text-sm font-semibold text-text-primary">No trading signals available</p>
                <p className="mt-1 text-xs text-text-secondary">Signals will appear here when the analysis feed returns them.</p>
              </div>
            )}
          </section>

          {featuredHeadline && (
            <section>
              <SectionHeading icon={Newspaper} title="Latest story" action="Open source" />
              <a href={featuredHeadline.url} target="_blank" rel="noreferrer" className="group grid overflow-hidden rounded-xl border border-border bg-card shadow-[0_4px_18px_rgba(20,40,35,0.06)] transition-colors hover:border-primary/40 md:grid-cols-[1.15fr_1fr]">
                <div className="min-h-48 bg-[#e9efec] md:min-h-64">
                  {featuredHeadline.image_url ? (
                    <img src={featuredHeadline.image_url} alt="" loading="lazy" className="h-full min-h-48 w-full object-cover md:min-h-64" />
                  ) : (
                    <div className="grid h-full min-h-48 place-items-center text-primary md:min-h-64"><Newspaper className="h-10 w-10" /></div>
                  )}
                </div>
                <div className="flex flex-col justify-center p-5 sm:p-7">
                  <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-primary">GBP/USD · Market news</span>
                  <h2 className="mt-3 font-display text-xl font-bold leading-7 text-text-primary group-hover:text-primary sm:text-2xl">
                    {featuredHeadline.title}
                  </h2>
                  <p className="mt-3 text-xs text-text-secondary">
                    {featuredHeadline.publisher}{featuredHeadline.published_at ? ` · ${formatDate(featuredHeadline.published_at, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} UTC` : ""}
                  </p>
                  <span className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-primary">Read at source <ExternalLink className="h-3.5 w-3.5" /></span>
                </div>
              </a>
            </section>
          )}

          <section>
            <SectionHeading
              icon={CalendarDays}
              title="Upcoming events"
              action={showAllEvents ? "Show less" : "Show more"}
              onAction={() => setShowAllEvents((shown) => !shown)}
            />
            <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[0_3px_14px_rgba(20,40,35,0.05)]">
              {eventsError ? (
                <p role="alert" className="px-4 py-8 text-center text-sm text-negative">Events could not be loaded: {eventsError}</p>
              ) : eventsLoading ? (
                <p className="px-4 py-8 text-center text-sm text-text-secondary">Loading upcoming events…</p>
              ) : visibleEvents.length ? (
                <ul className="divide-y divide-border/70">
                  {visibleEvents.map((event) => (
                    <li key={event.id} className="flex items-center gap-3 px-4 py-3.5">
                      <span className={`grid h-9 w-10 shrink-0 place-items-center rounded-md text-[10px] font-bold ${event.currency === "USD" ? "bg-blue-50 text-blue-800" : "bg-rose-50 text-rose-800"}`}>
                        {event.currency}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-semibold text-text-primary">{event.event}</p>
                        <p className="mt-1 flex items-center gap-1.5 text-[11px] text-text-secondary">
                          <Clock3 className="h-3 w-3" />{event.all_day ? formatDate(event.timestamp, { month: "short", day: "numeric" }) + " · All day" : formatDate(event.timestamp, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) + " UTC"}
                          {event.url && <a href={event.url} target="_blank" rel="noreferrer" aria-label={`Open ${event.event} source`} className="ml-1 text-primary"><ExternalLink className="h-3 w-3" /></a>}
                        </p>
                        {(event.forecast || event.previous) && (
                          <p className="mt-1 truncate text-[10px] text-text-muted">
                            {event.forecast ? `Consensus ${event.forecast}` : ""}{event.forecast && event.previous ? " · " : ""}{event.previous ? `Prior ${event.previous}` : ""}
                          </p>
                        )}
                      </div>
                      <span className={`shrink-0 rounded-sm px-2 py-1 text-[9px] font-bold uppercase ${event.importance.toUpperCase() === "HIGH" ? "bg-amber-100 text-amber-800" : "bg-slate-100 text-slate-600"}`}>
                        {event.importance}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="px-4 py-8 text-center">
                  <CalendarDays className="mx-auto h-5 w-5 text-text-muted" />
                  <p className="mt-2 text-sm font-semibold text-text-primary">No upcoming GBP/USD events loaded</p>
                  <p className="mt-1 text-xs text-text-secondary">Connect a licensed economic-calendar feed to populate this section.</p>
                </div>
              )}
            </div>
            <p className="mt-2 text-[10px] text-text-muted">
              Calendar data by <a href="https://www.financecalendar.com" target="_blank" rel="noreferrer" className="font-semibold text-primary underline underline-offset-2">FinanceCalendar.com</a>.
            </p>
          </section>

          <section>
            <SectionHeading
              icon={Newspaper}
              title="Top news"
              action={showAllNews ? "Show less" : "Show more"}
              onAction={() => setShowAllNews((shown) => !shown)}
            />
            <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[0_3px_14px_rgba(20,40,35,0.05)]">
              {newsError ? (
                <p role="alert" className="px-4 py-8 text-center text-sm text-negative">News could not be loaded: {newsError}</p>
              ) : newsLoading ? (
                <p className="px-4 py-8 text-center text-sm text-text-secondary">Loading market news…</p>
              ) : visibleNews.length ? (
                <ul className="divide-y divide-border/70">
                  {visibleNews.map((headline) => (
                    <li key={headline.id}>
                      <a href={headline.url} target="_blank" rel="noreferrer" className="group flex items-center gap-3.5 px-4 py-3.5 transition-colors hover:bg-background/70">
                        {headline.image_url ? (
                          <img src={headline.image_url} alt="" loading="lazy" className="h-14 w-14 shrink-0 rounded-md bg-background object-cover" />
                        ) : (
                          <span className="grid h-14 w-14 shrink-0 place-items-center rounded-md bg-[#edf3ef] text-primary"><Newspaper className="h-5 w-5" /></span>
                        )}
                        <span className="min-w-0 flex-1">
                          <span className="line-clamp-2 block text-sm font-semibold leading-5 text-text-primary group-hover:text-primary">{headline.title}</span>
                          <span className="mt-1.5 block truncate text-[11px] text-text-secondary">
                            {headline.publisher}{headline.published_at ? ` · ${formatDate(headline.published_at, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} UTC` : ""}
                          </span>
                        </span>
                        <ExternalLink className="h-4 w-4 shrink-0 text-text-muted group-hover:text-primary" />
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="px-4 py-8 text-center text-sm text-text-secondary">No GBP/USD headlines are available right now.</p>
              )}
            </div>
            <p className="mt-2 text-[10px] text-text-muted">Headlines and links are provided by Yahoo Finance. Open the source for full articles.</p>
          </section>

          <section>
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.12em] text-text-secondary">
                <Landmark className="h-4 w-4 text-primary" />
                Broker directory
              </h2>
              <span className="text-xs font-semibold text-text-muted">{BROKER_LISTINGS.length} listings</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {BROKER_LISTINGS.map((broker) => (
                <article key={broker.name} className="flex min-h-52 flex-col rounded-xl border border-border bg-card p-4 shadow-[0_3px_14px_rgba(20,40,35,0.05)]">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-display text-base font-bold text-text-primary">{broker.name}</p>
                      <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.1em] text-primary">{broker.category}</p>
                    </div>
                    <Landmark className="h-5 w-5 shrink-0 text-text-muted" />
                  </div>
                  <p className="mt-4 flex-1 text-xs leading-5 text-text-secondary">{broker.description}</p>
                  <button type="button" disabled className="mt-4 w-full cursor-not-allowed rounded-md border border-border bg-background px-3 py-2.5 text-xs font-semibold text-text-muted opacity-80">
                    Registration link coming soon
                  </button>
                </article>
              ))}
            </div>
            <p className="mt-3 text-[10px] leading-4 text-text-muted">
              Listings are informational, not endorsements. Check each broker’s regulation, fees, products, and availability in your country. Any future affiliate relationship will be disclosed.
            </p>
          </section>
        </main>
      </div>
    </div>
  );
}