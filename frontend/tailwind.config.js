/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#070A0A",
        surface: "#111815",
        elevated: "#17201D",
        wash: "#1A2622",
        ink: "#F2F4F3",
        muted: "#8A9A93",
        sage: "#14BE8A",
        amber: "#E8A42A",
        coral: "#E85D5B",
        border: "rgba(45,90,75,0.18)",
      },
      fontFamily: {
        sans: ["Satoshi", "Geist", "system-ui", "sans-serif"],
        display: ["Cabinet Grotesk", "Satoshi", "sans-serif"],
        mono: ["JetBrains Mono", "Geist Mono", "monospace"],
      },
      borderRadius: {
        card: "1.5rem",
        pill: "999px",
      },
      boxShadow: {
        lab: "0 20px 40px -16px rgba(0,0,0,0.45), 0 8px 16px -8px rgba(0,0,0,0.3)",
        glow: "0 0 0 1px rgba(20,190,138,0.12)",
      },
      keyframes: {
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(200%)" },
        },
        pulseDot: {
          "0%,100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.6", transform: "scale(0.85)" },
        },
        float: {
          "0%,100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-6px)" },
        },
        helix: {
          "0%": { transform: "translateX(0) rotate(0)" },
          "100%": { transform: "translateX(-50%) rotate(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.8s ease-in-out infinite",
        pulseDot: "pulseDot 2s ease-in-out infinite",
        float: "float 4s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
