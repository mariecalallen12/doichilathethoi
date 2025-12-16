/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        purple: {
          primary: "#8B5CF6",
          dark: "#6D28D9",
          light: "#A78BFA",
        },
        blue: {
          primary: "#3B82F6",
          dark: "#2563EB",
          light: "#60A5FA",
        },
        green: {
          primary: "#10B981",
          dark: "#059669",
          light: "#34D399",
        },
        red: {
          primary: "#EF4444",
          dark: "#DC2626",
          light: "#F87171",
        },
      },
      backgroundImage: {
        "gradient-purple-blue": "linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)",
        "gradient-dark": "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)",
      },
      backdropBlur: {
        xs: "2px",
      },
      keyframes: {
        blob: {
          "0%, 100%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(30px, -20px) scale(1.05)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.95)" },
        },
        "float": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
        scroll: {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(-100%)" },
        },
        flash: {
          "0%": { filter: "brightness(1.4)" },
          "100%": { filter: "brightness(1)" },
        },
        "pulse-slow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
      animation: {
        blob: "blob 12s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
        "spin-slow": "spin-slow 18s linear infinite",
        scroll: "scroll 30s linear infinite",
        flash: "flash 0.6s ease",
        "pulse-slow": "pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      fontFamily: {
        pacifico: ["Pacifico", "cursive"],
        secular: ["Secular One", "sans-serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        orbitron: ["Orbitron", "monospace"],
        led: ["Orbitron", "monospace"],
      },
      boxShadow: {
        "glass": "0 8px 32px 0 rgba(31, 38, 135, 0.37)",
        "glass-lg": "0 8px 32px 0 rgba(139, 92, 246, 0.3)",
      },
    },
  },
  plugins: [],
};

