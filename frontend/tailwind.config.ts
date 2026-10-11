import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F3F6F5",
        card: "#FFFFFF",
        primary: {
          DEFAULT: "#0D6B62",
          foreground: "#FFFFFF",
        },
        text: {
          primary: "#172522",
          secondary: "#5E706B",
          muted: "#84938E",
        },
        border: "#DCE5E1",
        positive: {
          DEFAULT: "#177A55",
          light: "#E8F4EE",
        },
        negative: {
          DEFAULT: "#BA413A",
          light: "#FBEFED",
        },
        warning: {
          DEFAULT: "#A76513",
          light: "#FBF2E4",
        },
      },
      fontFamily: {
        sans: ["var(--font-dm-sans)", "sans-serif"],
        display: ["var(--font-space-grotesk)", "sans-serif"],
        mono: ["var(--font-ibm-plex-mono)", "monospace"],
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
        xl: "0.5rem",
        "2xl": "0.75rem",
      },
      boxShadow: {
        card: "0 1px 2px rgb(19 43 37 / 0.04), 0 8px 24px rgb(19 43 37 / 0.035)",
      },
    },
  },
  plugins: [],
};

export default config;
