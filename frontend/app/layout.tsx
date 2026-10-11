import type { Metadata } from "next";
import { DM_Sans, IBM_Plex_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-plex-mono",
});

export const metadata: Metadata = {
  title: "FXMind — GBP/USD AI Market Analysis Assistant",
  description:
    "Production-oriented probabilistic AI market analysis for GBP/USD. Multiclass XGBoost classification with calibrated probabilities, regime detection, and transparent reasoning.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${dmSans.variable} ${spaceGrotesk.variable} ${ibmPlexMono.variable}`}>
      <body className="bg-background text-text-primary antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
