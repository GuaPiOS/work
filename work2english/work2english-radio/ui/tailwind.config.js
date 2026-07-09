/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Work2English OS palette — violet-led, disciplined
        void: "#05060B",
        abyss: "#0A0D18",
        slate: {
          deep: "#0E1220",
        },
        iris: "#7B61FF",
        plasma: "#C084FC",
        azure: "#38BDF8",
        mist: "#E6E8F0",
        haze: "#6B7390",
        status: {
          ok: "#34D399",
          warn: "#FBBF24",
          err: "#F87171",
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      borderRadius: {
        os: "24px",
      },
      boxShadow: {
        glow: "0 0 60px -12px rgba(123, 97, 255, 0.45)",
        "glow-cyan": "0 0 50px -10px rgba(56, 189, 248, 0.4)",
        inset: "inset 0 1px 0 0 rgba(255,255,255,0.06)",
      },
      backdropBlur: {
        os: "20px",
      },
      keyframes: {
        breathe: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.85" },
          "50%": { transform: "scale(1.04)", opacity: "1" },
        },
        drift: {
          "0%": { transform: "translate3d(0,0,0)" },
          "50%": { transform: "translate3d(3%, -4%, 0)" },
          "100%": { transform: "translate3d(0,0,0)" },
        },
      },
      animation: {
        breathe: "breathe 6s ease-in-out infinite",
        drift: "drift 28s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
