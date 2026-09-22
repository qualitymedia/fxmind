"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function CalendarPage() {
  const events = [
    { time: "12:30 UTC", currency: "USD", event: "CPI (MoM)", impact: "High", forecast: "0.3%", previous: "0.2%" },
    { time: "14:00 UTC", currency: "USD", event: "FOMC Member Speech", impact: "Medium", forecast: "—", previous: "—" },
    { time: "15:30 UTC", currency: "GBP", event: "BoE Governor Speech", impact: "Medium", forecast: "—", previous: "—" },
    { time: "16:00 UTC", currency: "USD", event: "Consumer Confidence", impact: "Low", forecast: "101.2", previous: "100.4" },
  ];

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          <h1 className="text-xl font-bold font-display text-text-primary">
            Economic Calendar
          </h1>
          <div className="bg-card border border-border rounded-xl shadow-card overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-background border-b border-border text-text-secondary uppercase text-[11px] font-semibold">
                <tr>
                  <th className="p-4">Time</th>
                  <th className="p-4">Currency</th>
                  <th className="p-4">Event</th>
                  <th className="p-4">Impact</th>
                  <th className="p-4">Forecast</th>
                  <th className="p-4">Previous</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {events.map((e, idx) => (
                  <tr key={idx} className="hover:bg-background/50">
                    <td className="p-4 font-mono font-medium text-text-primary">{e.time}</td>
                    <td className="p-4 font-bold">{e.currency}</td>
                    <td className="p-4 font-medium text-text-primary">{e.event}</td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${e.impact === "High" ? "bg-negative-light text-negative" : "bg-warning-light text-warning"}`}>
                        {e.impact}
                      </span>
                    </td>
                    <td className="p-4">{e.forecast}</td>
                    <td className="p-4 text-text-secondary">{e.previous}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}
