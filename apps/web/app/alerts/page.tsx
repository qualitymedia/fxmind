"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function AlertsPage() {
  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          <h1 className="text-xl font-bold font-display text-text-primary">
            Alert Rules
          </h1>
          <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-4 text-xs">
            <div className="flex justify-between items-center py-3 border-b border-border">
              <div>
                <span className="font-semibold text-text-primary block text-sm">New Bullish Setup Alert</span>
                <span className="text-text-secondary">Trigger when calibrated confidence &gt; 65%</span>
              </div>
              <span className="px-2.5 py-1 rounded bg-positive-light text-positive font-bold">ACTIVE</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-border">
              <div>
                <span className="font-semibold text-text-primary block text-sm">High Impact Economic Event Warning</span>
                <span className="text-text-secondary">Notify 15 minutes before USD CPI, NFP, BoE Rate decisions</span>
              </div>
              <span className="px-2.5 py-1 rounded bg-positive-light text-positive font-bold">ACTIVE</span>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
