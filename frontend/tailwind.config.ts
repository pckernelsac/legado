import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

/**
 * Identidad visual de Legado Eterno.
 * Verde vida (#008931) como color principal, dorado (#C8A97E) como acento.
 * Estética cálida y luminosa — nunca funeraria.
 */
const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1280px" },
    },
    extend: {
      colors: {
        brand: {
          DEFAULT: "#008931",
          hover: "#006D27",
          light: "#E7F8EE",
          gold: "#C8A97E",
        },
        background: "#FAFAFA",
        card: "#FFFFFF",
        border: "#E5E7EB",
        foreground: {
          DEFAULT: "#111827",
          muted: "#6B7280",
        },
        // Aliases shadcn/ui
        primary: { DEFAULT: "#008931", foreground: "#FFFFFF" },
        secondary: { DEFAULT: "#E7F8EE", foreground: "#006D27" },
        muted: { DEFAULT: "#F3F4F6", foreground: "#6B7280" },
        accent: { DEFAULT: "#C8A97E", foreground: "#111827" },
        destructive: { DEFAULT: "#DC2626", foreground: "#FFFFFF" },
        ring: "#008931",
        input: "#E5E7EB",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      fontSize: {
        h1: ["64px", { lineHeight: "1.05", letterSpacing: "-0.03em", fontWeight: "700" }],
        h2: ["48px", { lineHeight: "1.1", letterSpacing: "-0.02em", fontWeight: "700" }],
        h3: ["32px", { lineHeight: "1.2", letterSpacing: "-0.01em", fontWeight: "600" }],
        body: ["16px", { lineHeight: "1.6" }],
      },
      borderRadius: {
        lg: "1rem",
        md: "0.75rem",
        sm: "0.5rem",
      },
      boxShadow: {
        soft: "0 1px 3px rgba(17,24,39,0.04), 0 8px 24px rgba(17,24,39,0.06)",
        card: "0 2px 8px rgba(17,24,39,0.05)",
        glow: "0 8px 40px rgba(0,137,49,0.18)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(24px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "flame-flicker": {
          "0%, 100%": { transform: "scale(1) rotate(-1deg)", opacity: "0.95" },
          "50%": { transform: "scale(1.05) rotate(1deg)", opacity: "1" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.6s ease-out forwards",
        "slide-up": "slide-up 0.7s cubic-bezier(0.22,1,0.36,1) forwards",
        flame: "flame-flicker 1.8s ease-in-out infinite",
      },
    },
  },
  plugins: [animate],
};

export default config;
