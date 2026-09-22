import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
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
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="bg-background text-text-primary antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
