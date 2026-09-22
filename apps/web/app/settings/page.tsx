"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          <h1 className="text-xl font-bold font-display text-text-primary">
            Settings & Preferences
          </h1>
          <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-6 text-xs max-w-2xl">
            <div>
              <label className="font-bold text-text-primary block text-sm mb-1">Timezone</label>
              <select className="w-full bg-background border border-border rounded-lg p-2 text-xs">
                <option value="UTC">UTC (Server default)</option>
                <option value="America/New_York">America/New_York (EST)</option>
                <option value="Europe/London">Europe/London (GMT/BST)</option>
              </select>
            </div>
            <div>
              <label className="font-bold text-text-primary block text-sm mb-1">Minimum Confidence Gate</label>
              <input type="number" step="0.01" defaultValue="0.58" className="w-full bg-background border border-border rounded-lg p-2 text-xs" />
            </div>
            <div>
              <label className="font-bold text-text-primary block text-sm mb-1">News Risk Window (Minutes)</label>
              <input type="number" defaultValue="30" className="w-full bg-background border border-border rounded-lg p-2 text-xs" />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
